"""
Support Access Grant API endpoints.

Provides consent-based, time-limited support access for healthcare compliance.

Flow:
1. Support agent requests access to tenant
2. Tenant admin reviews and grants/denies access
3. Access is logged and automatically expires (max 48 hours)
4. Tenant admin can revoke access at any time

Security:
- All access is audited
- Maximum 48 hour duration
- Two access levels: metadata (non-PHI) and full (with PHI)
- Requires explicit consent from tenant admin
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import logging

from src.api.database import get_db
from src.api.auth.dependencies import (
    get_current_user,
    require_permissions,
    require_support_access,
)
from src.api.models.user import User
from src.api.models.role import SupportAccessGrant, Permissions, RoleScope
from src.api.models.tenant import Tenant, AuditLog
from src.api.services import role_service
from src.api.schemas.user_management_schemas import (
    SupportAccessRequestCreate,
    SupportAccessGrantCreate,
    SupportAccessGrantResponse,
    SupportAccessGrantListResponse,
    RevokeAccessRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/support-access", tags=["Support Access"])


# =============================================================================
# Helper Functions
# =============================================================================

def build_grant_response(db: Session, grant: SupportAccessGrant) -> SupportAccessGrantResponse:
    """Build response from grant object."""
    # Get tenant name
    tenant = db.query(Tenant).filter(Tenant.id == grant.tenant_id).first()
    tenant_name = tenant.name if tenant else "Unknown"

    # Get user names
    granted_to = db.query(User).filter(User.id == grant.granted_to_user_id).first()
    granted_to_name = granted_to.full_name if granted_to else "Unknown"

    granted_by = db.query(User).filter(User.id == grant.granted_by_user_id).first()
    granted_by_name = granted_by.full_name if granted_by else "Unknown"

    # Get revoker name if revoked
    revoked_by_name = None
    if grant.revoked_by:
        revoker = db.query(User).filter(User.id == grant.revoked_by).first()
        revoked_by_name = revoker.full_name if revoker else None

    return SupportAccessGrantResponse(
        id=grant.id,
        tenant_id=grant.tenant_id,
        tenant_name=tenant_name,
        granted_to_user_id=grant.granted_to_user_id,
        granted_to_name=granted_to_name,
        granted_by_user_id=grant.granted_by_user_id,
        granted_by_name=granted_by_name,
        reason=grant.reason,
        access_level=grant.access_level,
        is_active=grant.is_active(),
        created_at=grant.created_at,
        expires_at=grant.expires_at,
        revoked_at=grant.revoked_at,
        revoked_by=revoked_by_name,
    )


def create_audit_log(
    db: Session,
    tenant_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    performed_by: str,
    details: dict,
):
    """Create an audit log entry for support access actions."""
    audit = AuditLog(
        tenant_id=tenant_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        performed_by=performed_by,
        details=details,
        ip_address=None,  # Would be populated from request
    )
    db.add(audit)


# =============================================================================
# Support Agent Endpoints
# =============================================================================

@router.get("/my-grants", response_model=SupportAccessGrantListResponse)
async def list_my_support_grants(
    include_expired: bool = Query(False, description="Include expired grants"),
    current_user: User = Depends(require_permissions(Permissions.SUPPORT_ACCESS)),
    db: Session = Depends(get_db),
):
    """
    List support access grants for the current support agent.

    Shows all tenants the agent has or had access to.
    """
    query = db.query(SupportAccessGrant).filter(
        SupportAccessGrant.granted_to_user_id == current_user.id
    )

    if not include_expired:
        now = datetime.now(timezone.utc)
        query = query.filter(
            SupportAccessGrant.revoked_at.is_(None),
            SupportAccessGrant.expires_at > now,
        )

    grants = query.order_by(SupportAccessGrant.created_at.desc()).all()

    return SupportAccessGrantListResponse(
        grants=[build_grant_response(db, g) for g in grants],
        total=len(grants),
    )


@router.post("/request", status_code=status.HTTP_202_ACCEPTED)
async def request_support_access(
    request: SupportAccessRequestCreate,
    current_user: User = Depends(require_permissions(Permissions.SUPPORT_ACCESS)),
    db: Session = Depends(get_db),
):
    """
    Request support access to a tenant.

    This creates a pending request that the tenant admin must approve.
    The request is logged for audit purposes.

    Note: This is a simplified implementation. In production, this would
    trigger a notification to the tenant admin and create a pending request.
    """
    # Verify tenant exists
    tenant = db.query(Tenant).filter(Tenant.id == request.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Check if already has active access
    existing = role_service.get_support_access_grant(
        db, current_user.id, request.tenant_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already have active access to this tenant"
        )

    # Create audit log for the request
    create_audit_log(
        db,
        tenant_id=request.tenant_id,
        action="support_access_requested",
        resource_type="support_access",
        resource_id="pending",
        performed_by=current_user.id,
        details={
            "reason": request.reason,
            "access_level": request.access_level.value,
            "duration_hours": request.duration_hours,
            "requester_email": current_user.email,
        },
    )

    db.commit()

    logger.info(
        f"Support access requested: {current_user.id} -> tenant {request.tenant_id}"
    )

    # TODO: In production, this would:
    # 1. Create a SupportAccessRequest record (pending status)
    # 2. Send notification to tenant admins
    # 3. Return request ID for tracking

    return {
        "message": "Support access request submitted",
        "tenant_id": request.tenant_id,
        "status": "pending",
        "note": "A tenant administrator will review your request",
    }


# =============================================================================
# Tenant Admin Endpoints
# =============================================================================

@router.get("/tenant/{tenant_id}/grants", response_model=SupportAccessGrantListResponse)
async def list_tenant_support_grants(
    tenant_id: str,
    include_expired: bool = Query(False, description="Include expired/revoked grants"),
    current_user: User = Depends(require_permissions(Permissions.MANAGE_USERS)),
    db: Session = Depends(get_db),
):
    """
    List all support access grants for a tenant.

    Tenant admins can view the history of support access to their organization.
    """
    # Verify access to tenant
    is_super = role_service.is_super_admin(db, current_user.id)
    if not is_super and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )

    query = db.query(SupportAccessGrant).filter(
        SupportAccessGrant.tenant_id == tenant_id
    )

    if not include_expired:
        now = datetime.now(timezone.utc)
        query = query.filter(
            SupportAccessGrant.revoked_at.is_(None),
            SupportAccessGrant.expires_at > now,
        )

    grants = query.order_by(SupportAccessGrant.created_at.desc()).all()

    return SupportAccessGrantListResponse(
        grants=[build_grant_response(db, g) for g in grants],
        total=len(grants),
    )


@router.post("/tenant/{tenant_id}/grant", response_model=SupportAccessGrantResponse, status_code=status.HTTP_201_CREATED)
async def grant_support_access(
    tenant_id: str,
    request: SupportAccessGrantCreate,
    current_user: User = Depends(require_permissions(Permissions.MANAGE_USERS)),
    db: Session = Depends(get_db),
):
    """
    Grant support access to a support agent.

    Tenant admins grant time-limited access with explicit consent.
    Maximum duration is 48 hours.
    """
    # Verify access to tenant
    is_super = role_service.is_super_admin(db, current_user.id)
    if not is_super and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )

    # Verify tenant exists
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Verify support user exists and has support role
    support_user = db.query(User).filter(User.id == request.support_user_id).first()
    if not support_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support user not found"
        )

    # Verify user has support permissions
    has_support = role_service.has_permission(
        db, request.support_user_id, Permissions.SUPPORT_ACCESS
    )
    if not has_support and not role_service.is_super_admin(db, request.support_user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have support agent role"
        )

    # Check for existing active grant
    existing = role_service.get_support_access_grant(
        db, request.support_user_id, tenant_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has active access to this tenant"
        )

    # Validate duration
    if request.duration_hours > 48:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Support access cannot exceed 48 hours"
        )

    # Create grant
    expires_at = datetime.now(timezone.utc) + timedelta(hours=request.duration_hours)

    grant = SupportAccessGrant(
        tenant_id=tenant_id,
        granted_to_user_id=request.support_user_id,
        granted_by_user_id=current_user.id,
        reason=request.reason,
        access_level=request.access_level.value,
        expires_at=expires_at,
    )
    db.add(grant)

    # Create audit log
    create_audit_log(
        db,
        tenant_id=tenant_id,
        action="support_access_granted",
        resource_type="support_access",
        resource_id=grant.id,
        performed_by=current_user.id,
        details={
            "granted_to": request.support_user_id,
            "reason": request.reason,
            "access_level": request.access_level.value,
            "duration_hours": request.duration_hours,
            "expires_at": expires_at.isoformat(),
        },
    )

    db.commit()
    db.refresh(grant)

    logger.info(
        f"Support access granted: {request.support_user_id} -> tenant {tenant_id} "
        f"by {current_user.id} (expires: {expires_at})"
    )

    return build_grant_response(db, grant)


@router.post("/grant/{grant_id}/revoke", status_code=status.HTTP_200_OK)
async def revoke_support_access(
    grant_id: str,
    request: Optional[RevokeAccessRequest] = None,
    current_user: User = Depends(require_permissions(Permissions.MANAGE_USERS)),
    db: Session = Depends(get_db),
):
    """
    Revoke a support access grant.

    Tenant admins can revoke access at any time before expiration.
    """
    grant = db.query(SupportAccessGrant).filter(
        SupportAccessGrant.id == grant_id
    ).first()

    if not grant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support access grant not found"
        )

    # Verify access to tenant
    is_super = role_service.is_super_admin(db, current_user.id)
    if not is_super and current_user.tenant_id != grant.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this grant"
        )

    # Check if already revoked
    if grant.revoked_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grant already revoked"
        )

    # Revoke
    grant.revoke(current_user.id)

    # Create audit log
    create_audit_log(
        db,
        tenant_id=grant.tenant_id,
        action="support_access_revoked",
        resource_type="support_access",
        resource_id=grant.id,
        performed_by=current_user.id,
        details={
            "revoked_user": grant.granted_to_user_id,
            "reason": request.reason if request else None,
            "original_expires_at": grant.expires_at.isoformat(),
        },
    )

    db.commit()

    logger.info(
        f"Support access revoked: grant {grant_id} by {current_user.id}"
    )

    return {"message": "Support access revoked", "grant_id": grant_id}


# =============================================================================
# Platform Admin Endpoints
# =============================================================================

@router.get("/all", response_model=SupportAccessGrantListResponse)
async def list_all_support_grants(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant"),
    support_user_id: Optional[str] = Query(None, description="Filter by support user"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_permissions(Permissions.VIEW_ALL_ANALYTICS)),
    db: Session = Depends(get_db),
):
    """
    List all support access grants across all tenants.

    Platform admins can view and audit all support access.
    """
    query = db.query(SupportAccessGrant)

    if tenant_id:
        query = query.filter(SupportAccessGrant.tenant_id == tenant_id)
    if support_user_id:
        query = query.filter(SupportAccessGrant.granted_to_user_id == support_user_id)

    if is_active is not None:
        now = datetime.now(timezone.utc)
        if is_active:
            query = query.filter(
                SupportAccessGrant.revoked_at.is_(None),
                SupportAccessGrant.expires_at > now,
            )
        else:
            query = query.filter(
                or_(
                    SupportAccessGrant.revoked_at.isnot(None),
                    SupportAccessGrant.expires_at <= now,
                )
            )

    total = query.count()

    offset = (page - 1) * page_size
    grants = query.order_by(
        SupportAccessGrant.created_at.desc()
    ).offset(offset).limit(page_size).all()

    return SupportAccessGrantListResponse(
        grants=[build_grant_response(db, g) for g in grants],
        total=total,
    )


@router.get("/grant/{grant_id}", response_model=SupportAccessGrantResponse)
async def get_support_grant(
    grant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get details of a specific support access grant.
    """
    grant = db.query(SupportAccessGrant).filter(
        SupportAccessGrant.id == grant_id
    ).first()

    if not grant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support access grant not found"
        )

    # Check access
    is_super = role_service.is_super_admin(db, current_user.id)
    is_tenant_admin = current_user.tenant_id == grant.tenant_id
    is_grantee = current_user.id == grant.granted_to_user_id

    if not (is_super or is_tenant_admin or is_grantee):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return build_grant_response(db, grant)


# Import for or_ filter
from sqlalchemy import or_
