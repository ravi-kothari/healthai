"""
Tenant management API endpoints.

Provides:
- Tenant onboarding and setup
- Tenant settings management
- Subscription management
- User invitations

Security:
- Super admins can manage all tenants
- Tenant admins can manage their own tenant
- Regular users have read-only access to their tenant info
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import secrets
import logging

from src.api.database import get_db
from src.api.auth.dependencies import get_current_user
from src.api.models.user import User, UserRole
from src.api.models.tenant import (
    Tenant, TenantStatus, SubscriptionPlan, SubscriptionStatus,
    AuditLog, TenantInvitation
)
from src.api.middleware.tenant import set_tenant_context, reset_tenant_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tenants", tags=["Tenants"])


# ============================================
# Pydantic Schemas
# ============================================

class TenantCreate(BaseModel):
    """Schema for creating a new tenant."""
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=100, pattern=r'^[a-z0-9-]+$')
    email: EmailStr
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "USA"
    organization_type: Optional[str] = None
    subscription_plan: SubscriptionPlan = SubscriptionPlan.TRIAL


class TenantUpdate(BaseModel):
    """Schema for updating tenant information."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    organization_type: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class TenantResponse(BaseModel):
    """Schema for tenant response."""
    id: str
    name: str
    slug: str
    email: str
    phone: Optional[str]
    status: str
    is_active: bool
    subscription_plan: str
    subscription_status: str
    max_users: int
    max_patients: int
    onboarding_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InvitationCreate(BaseModel):
    """Schema for creating user invitation."""
    email: EmailStr
    role: str = Field(default="staff", pattern=r'^(doctor|nurse|staff|admin)$')


class InvitationResponse(BaseModel):
    """Schema for invitation response."""
    id: str
    email: str
    role: str
    expires_at: datetime
    is_accepted: bool
    created_at: datetime

    class Config:
        from_attributes = True


class OnboardingStepUpdate(BaseModel):
    """Schema for updating onboarding progress."""
    step: str
    completed: bool = False
    data: Optional[Dict[str, Any]] = None


# ============================================
# Helper Functions
# ============================================

def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require super admin role."""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


def require_tenant_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require tenant admin or super admin role."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def log_audit(
    db: Session,
    tenant_id: str,
    user: User,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    description: Optional[str] = None
):
    """Create an audit log entry."""
    audit = AuditLog(
        tenant_id=tenant_id,
        user_id=user.id,
        user_email=user.email,
        user_role=user.role.value,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_values=old_values,
        new_values=new_values,
        description=description
    )
    db.add(audit)
    db.commit()


# ============================================
# Super Admin Endpoints
# ============================================

@router.get("/", response_model=List[TenantResponse])
async def list_all_tenants(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[TenantStatus] = None,
    plan_filter: Optional[SubscriptionPlan] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    List all tenants (super admin only).

    Supports filtering by status and subscription plan.
    """
    query = db.query(Tenant)

    if status_filter:
        query = query.filter(Tenant.status == status_filter)
    if plan_filter:
        query = query.filter(Tenant.subscription_plan == plan_filter)

    tenants = query.order_by(Tenant.created_at.desc()).offset(skip).limit(limit).all()
    return tenants


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Create a new tenant (super admin only).

    This creates the organization and sets up initial configuration.
    """
    # Check if slug is unique
    existing = db.query(Tenant).filter(Tenant.slug == tenant_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization slug already exists"
        )

    # Set trial end date (14 days)
    trial_ends_at = datetime.utcnow() + timedelta(days=14)

    # Default settings based on plan
    default_settings = {
        "features": {
            "ai_assistant": tenant_data.subscription_plan != SubscriptionPlan.STARTER,
            "transcription": True,
            "fhir_integration": tenant_data.subscription_plan == SubscriptionPlan.ENTERPRISE,
            "careprep": True,
            "custom_branding": tenant_data.subscription_plan == SubscriptionPlan.ENTERPRISE
        },
        "compliance": {
            "hipaa_baa_signed": False,
            "data_retention_days": 2555  # 7 years
        },
        "notifications": {
            "email_enabled": True,
            "sms_enabled": False
        }
    }

    # Plan-based limits
    plan_limits = {
        SubscriptionPlan.TRIAL: {"max_users": 5, "max_patients": 50, "max_storage_gb": 5},
        SubscriptionPlan.STARTER: {"max_users": 10, "max_patients": 100, "max_storage_gb": 10},
        SubscriptionPlan.PROFESSIONAL: {"max_users": 50, "max_patients": 500, "max_storage_gb": 50},
        SubscriptionPlan.ENTERPRISE: {"max_users": 1000, "max_patients": 100000, "max_storage_gb": 500},
    }

    limits = plan_limits.get(tenant_data.subscription_plan, plan_limits[SubscriptionPlan.TRIAL])

    tenant = Tenant(
        name=tenant_data.name,
        slug=tenant_data.slug,
        email=tenant_data.email,
        phone=tenant_data.phone,
        address_line1=tenant_data.address_line1,
        city=tenant_data.city,
        state=tenant_data.state,
        postal_code=tenant_data.postal_code,
        country=tenant_data.country,
        organization_type=tenant_data.organization_type,
        subscription_plan=tenant_data.subscription_plan,
        subscription_status=SubscriptionStatus.TRIAL,
        trial_ends_at=trial_ends_at,
        settings=default_settings,
        **limits
    )

    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    # Log the action
    log_audit(
        db=db,
        tenant_id=tenant.id,
        user=current_user,
        action="CREATE",
        resource_type="tenant",
        resource_id=tenant.id,
        new_values=tenant.to_dict(),
        description=f"Created tenant: {tenant.name}"
    )

    logger.info(f"Tenant created: {tenant.id} ({tenant.name})")
    return tenant


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get tenant details.

    Super admins can view any tenant.
    Users can only view their own tenant.
    """
    if not current_user.can_access_tenant(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    return tenant


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    tenant_data: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin)
):
    """
    Update tenant information.

    Tenant admins can update their own tenant.
    Super admins can update any tenant.
    """
    if not current_user.can_access_tenant(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    old_values = tenant.to_dict()

    # Update fields
    update_data = tenant_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "settings" and value:
            # Merge settings instead of replacing
            current_settings = tenant.settings or {}
            current_settings.update(value)
            setattr(tenant, field, current_settings)
        else:
            setattr(tenant, field, value)

    db.commit()
    db.refresh(tenant)

    # Log the action
    log_audit(
        db=db,
        tenant_id=tenant_id,
        user=current_user,
        action="UPDATE",
        resource_type="tenant",
        resource_id=tenant_id,
        old_values=old_values,
        new_values=tenant.to_dict(),
        description=f"Updated tenant: {tenant.name}"
    )

    return tenant


@router.post("/{tenant_id}/suspend")
async def suspend_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Suspend a tenant (super admin only)."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Organization not found")

    tenant.status = TenantStatus.SUSPENDED
    tenant.is_active = False
    db.commit()

    log_audit(
        db=db,
        tenant_id=tenant_id,
        user=current_user,
        action="SUSPEND",
        resource_type="tenant",
        resource_id=tenant_id,
        description=f"Suspended tenant: {tenant.name}"
    )

    return {"message": "Organization suspended", "tenant_id": tenant_id}


@router.post("/{tenant_id}/activate")
async def activate_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Activate a suspended tenant (super admin only)."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Organization not found")

    tenant.status = TenantStatus.ACTIVE
    tenant.is_active = True
    db.commit()

    log_audit(
        db=db,
        tenant_id=tenant_id,
        user=current_user,
        action="ACTIVATE",
        resource_type="tenant",
        resource_id=tenant_id,
        description=f"Activated tenant: {tenant.name}"
    )

    return {"message": "Organization activated", "tenant_id": tenant_id}


# ============================================
# Invitation Endpoints
# ============================================

@router.post("/{tenant_id}/invitations", response_model=InvitationResponse)
async def create_invitation(
    tenant_id: str,
    invitation_data: InvitationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin)
):
    """
    Create an invitation to join the tenant.

    Only tenant admins can invite users.
    """
    if not current_user.can_access_tenant(tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check user limit
    current_user_count = db.query(User).filter(User.tenant_id == tenant_id).count()
    if not tenant.can_add_user(current_user_count):
        raise HTTPException(
            status_code=400,
            detail=f"User limit reached ({tenant.max_users}). Please upgrade your plan."
        )

    # Check if email already has pending invitation
    existing = db.query(TenantInvitation).filter(
        TenantInvitation.tenant_id == tenant_id,
        TenantInvitation.email == invitation_data.email,
        TenantInvitation.is_accepted == False
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Invitation already sent to this email")

    # Create invitation
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)

    invitation = TenantInvitation(
        tenant_id=tenant_id,
        email=invitation_data.email,
        role=invitation_data.role,
        token=token,
        expires_at=expires_at,
        invited_by_user_id=current_user.id
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    # TODO: Send invitation email in background
    # background_tasks.add_task(send_invitation_email, invitation, tenant)

    log_audit(
        db=db,
        tenant_id=tenant_id,
        user=current_user,
        action="CREATE",
        resource_type="invitation",
        resource_id=invitation.id,
        description=f"Invited {invitation_data.email} as {invitation_data.role}"
    )

    return invitation


@router.get("/{tenant_id}/invitations", response_model=List[InvitationResponse])
async def list_invitations(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin)
):
    """List all invitations for a tenant."""
    if not current_user.can_access_tenant(tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")

    invitations = db.query(TenantInvitation).filter(
        TenantInvitation.tenant_id == tenant_id
    ).order_by(TenantInvitation.created_at.desc()).all()

    return invitations


# ============================================
# Onboarding Endpoints
# ============================================

@router.post("/{tenant_id}/onboarding/step")
async def update_onboarding_step(
    tenant_id: str,
    step_data: OnboardingStepUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin)
):
    """Update onboarding progress."""
    if not current_user.can_access_tenant(tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Organization not found")

    tenant.onboarding_step = step_data.step

    if step_data.completed:
        tenant.onboarding_completed = True
        tenant.status = TenantStatus.ACTIVE

    # Store step data in settings
    if step_data.data:
        settings = tenant.settings or {}
        onboarding_data = settings.get("onboarding", {})
        onboarding_data[step_data.step] = step_data.data
        settings["onboarding"] = onboarding_data
        tenant.settings = settings

    db.commit()

    return {"message": "Onboarding step updated", "step": step_data.step}


@router.get("/{tenant_id}/stats")
async def get_tenant_stats(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin)
):
    """Get usage statistics for a tenant."""
    if not current_user.can_access_tenant(tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Set tenant context for RLS
    set_tenant_context(db, tenant_id)

    try:
        from src.api.models import Patient, User as UserModel, Visit, Appointment

        user_count = db.query(UserModel).filter(UserModel.tenant_id == tenant_id).count()
        patient_count = db.query(Patient).count()  # RLS filters by tenant
        # visit_count = db.query(Visit).count()  # RLS filters by tenant

        return {
            "tenant_id": tenant_id,
            "usage": {
                "users": {"current": user_count, "limit": tenant.max_users},
                "patients": {"current": patient_count, "limit": tenant.max_patients},
                # "visits_this_month": visit_count,
            },
            "subscription": {
                "plan": tenant.subscription_plan.value,
                "status": tenant.subscription_status.value,
                "trial_ends_at": tenant.trial_ends_at.isoformat() if tenant.trial_ends_at else None
            }
        }
    finally:
        reset_tenant_context(db)
