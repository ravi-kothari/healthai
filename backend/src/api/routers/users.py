"""
User Management API endpoints.

Provides:
- User CRUD operations (admin)
- User listing with filters and pagination
- Role assignment/revocation
- User invitations
- Bulk operations

Security:
- Tenant admins can manage users in their tenant
- Super admins can manage all users
- Permission-based access using new role system
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List
from datetime import datetime, timezone
import logging

from src.api.database import get_db
from src.api.auth.dependencies import (
    get_current_user,
    require_permissions,
    require_scoped_tenant_access,
)
from src.api.auth.password import hash_password
from src.api.models.user import User
from src.api.models.role import Role, UserRole as UserRoleModel, Permissions, RoleScope
from src.api.models.tenant import Tenant, TenantInvitation
from src.api.services import role_service
from src.api.schemas.user_management_schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserDetailResponse,
    UserListItemResponse,
    UserListResponse,
    UserRoleAssignment,
    AssignRoleRequest,
    RevokeRoleRequest,
    RoleResponse,
    RoleListResponse,
    BulkUserActionRequest,
    BulkActionResult,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["User Management"])


# =============================================================================
# Helper Functions
# =============================================================================

def build_user_detail_response(db: Session, user: User) -> UserDetailResponse:
    """Build detailed user response with roles."""
    # Get user's roles
    user_roles = role_service.get_user_roles(db, user.id)
    role_assignments = []

    for ur in user_roles:
        role = db.query(Role).filter(Role.id == ur.role_id).first()
        if role:
            # Get granter name if available
            granter_name = None
            if ur.granted_by:
                granter = db.query(User).filter(User.id == ur.granted_by).first()
                if granter:
                    granter_name = granter.full_name

            role_assignments.append(UserRoleAssignment(
                id=ur.id,
                role_id=ur.role_id,
                role_name=role.name,
                role_display_name=role.display_name,
                scope_type=ur.scope_type,
                scope_id=ur.scope_id,
                is_primary=ur.is_primary,
                granted_by=granter_name,
                granted_at=ur.granted_at,
                expires_at=ur.expires_at,
            ))

    # Get tenant name
    tenant_name = None
    if user.tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if tenant:
            tenant_name = tenant.name

    return UserDetailResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        is_active=user.is_active,
        is_verified=user.is_verified,
        tenant_id=user.tenant_id,
        tenant_name=tenant_name,
        roles=role_assignments,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=getattr(user, 'last_login_at', None),
        login_count=getattr(user, 'login_count', 0),
    )


def build_user_list_item(db: Session, user: User) -> UserListItemResponse:
    """Build user list item response."""
    # Get primary role name
    primary_role = role_service.get_user_primary_role(
        db, user.id,
        scope_type=RoleScope.TENANT if user.tenant_id else RoleScope.PLATFORM,
        scope_id=user.tenant_id
    )

    return UserListItemResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        primary_role=primary_role.display_name if primary_role else None,
        tenant_id=user.tenant_id,
        created_at=user.created_at,
        last_login_at=getattr(user, 'last_login_at', None),
    )


# =============================================================================
# User CRUD Endpoints
# =============================================================================

@router.get("", response_model=UserListResponse)
async def list_users(
    search: Optional[str] = Query(None, description="Search by email, username, or name"),
    role_name: Optional[str] = Query(None, description="Filter by role name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verified status"),
    tenant_id: Optional[str] = Query(None, description="Filter by tenant (super admin only)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_permissions(Permissions.MANAGE_USERS, Permissions.VIEW_PATIENTS)),
    db: Session = Depends(get_db),
):
    """
    List users with filtering and pagination.

    - Tenant admins see only users in their tenant
    - Super admins can see all users or filter by tenant
    """
    # Build base query
    query = db.query(User)

    # Tenant scoping
    is_super = role_service.is_super_admin(db, current_user.id)

    if is_super and tenant_id:
        # Super admin filtering by specific tenant
        query = query.filter(User.tenant_id == tenant_id)
    elif not is_super:
        # Non-super admin: only their tenant
        query = query.filter(User.tenant_id == current_user.tenant_id)

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.email.ilike(search_term),
                User.username.ilike(search_term),
                User.full_name.ilike(search_term),
            )
        )

    # Apply status filters
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)

    # TODO: Filter by role_name requires joining user_roles table
    # For now, we'll implement this as a post-filter

    # Get total count
    total = query.count()

    # Paginate
    offset = (page - 1) * page_size
    users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()

    # Build response items
    user_items = [build_user_list_item(db, user) for user in users]

    # Filter by role if specified (post-filter)
    if role_name:
        filtered_items = []
        for item in user_items:
            if item.primary_role and role_name.lower() in item.primary_role.lower():
                filtered_items.append(item)
        user_items = filtered_items
        total = len(user_items)

    total_pages = (total + page_size - 1) // page_size

    return UserListResponse(
        users=user_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_permissions(Permissions.MANAGE_USERS, Permissions.VIEW_PATIENTS)),
    db: Session = Depends(get_db),
):
    """
    Get detailed user information including roles.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check access
    is_super = role_service.is_super_admin(db, current_user.id)
    if not is_super and user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user"
        )

    return build_user_detail_response(db, user)


@router.post("", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    current_user: User = Depends(require_permissions(Permissions.MANAGE_USERS)),
    db: Session = Depends(get_db),
):
    """
    Create a new user (admin operation).

    - Tenant admins can create users in their tenant
    - Super admins can create users in any tenant
    """
    # Determine tenant
    is_super = role_service.is_super_admin(db, current_user.id)

    if request.tenant_id:
        if not is_super and request.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create users in other tenants"
            )
        tenant_id = request.tenant_id
    else:
        tenant_id = current_user.tenant_id

    # Validate tenant exists
    if tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

    # Check for duplicate email/username
    existing = db.query(User).filter(
        or_(User.email == request.email, User.username == request.username)
    ).first()
    if existing:
        if existing.email == request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Validate role exists
    role = db.query(Role).filter(Role.name == request.role_name).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{request.role_name}' not found"
        )

    # Create user
    user = User(
        email=request.email,
        username=request.username,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        phone=request.phone,
        tenant_id=tenant_id,
        is_active=True,
        is_verified=request.is_verified,
    )
    db.add(user)
    db.flush()  # Get the user ID

    # Assign role
    try:
        role_service.assign_role(
            db,
            user_id=user.id,
            role_name=request.role_name,
            scope_type=role.scope,
            scope_id=tenant_id if role.scope == RoleScope.TENANT else None,
            granted_by=current_user.id,
            is_primary=True,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    db.commit()
    db.refresh(user)

    logger.info(f"User created: {user.id} by {current_user.id}")

    # TODO: Send welcome email if request.send_welcome_email

    return build_user_detail_response(db, user)


@router.patch("/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    current_user: User = Depends(require_permissions(Permissions.MANAGE_USERS)),
    db: Session = Depends(get_db),
):
    """
    Update user information.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check access
    is_super = role_service.is_super_admin(db, current_user.id)
    if not is_super and user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user"
        )

    # Update fields
    if request.email is not None:
        # Check for duplicate email
        existing = db.query(User).filter(
            User.email == request.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = request.email

    if request.full_name is not None:
        user.full_name = request.full_name
    if request.phone is not None:
        user.phone = request.phone
    if request.is_active is not None:
        user.is_active = request.is_active
    if request.is_verified is not None:
        user.is_verified = request.is_verified

    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    logger.info(f"User updated: {user.id} by {current_user.id}")

    return build_user_detail_response(db, user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_permissions(Permissions.MANAGE_USERS)),
    db: Session = Depends(get_db),
):
    """
    Deactivate a user (soft delete).

    Does not permanently delete the user to maintain audit trails.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check access
    is_super = role_service.is_super_admin(db, current_user.id)
    if not is_super and user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user"
        )

    # Prevent self-deactivation
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    # Prevent deactivating super admins (unless by another super admin)
    if role_service.is_super_admin(db, user.id) and not is_super:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate a super admin"
        )

    user.is_active = False
    user.updated_at = datetime.now(timezone.utc)
    db.commit()

    logger.info(f"User deactivated: {user.id} by {current_user.id}")


# =============================================================================
# Role Assignment Endpoints
# =============================================================================

@router.get("/{user_id}/roles", response_model=List[UserRoleAssignment])
async def get_user_roles(
    user_id: str,
    current_user: User = Depends(require_permissions(Permissions.MANAGE_USERS, Permissions.VIEW_PATIENTS)),
    db: Session = Depends(get_db),
):
    """
    Get all role assignments for a user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check access
    is_super = role_service.is_super_admin(db, current_user.id)
    if not is_super and user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user"
        )

    user_roles = role_service.get_user_roles(db, user_id)
    result = []

    for ur in user_roles:
        role = db.query(Role).filter(Role.id == ur.role_id).first()
        if role:
            result.append(UserRoleAssignment(
                id=ur.id,
                role_id=ur.role_id,
                role_name=role.name,
                role_display_name=role.display_name,
                scope_type=ur.scope_type,
                scope_id=ur.scope_id,
                is_primary=ur.is_primary,
                granted_by=ur.granted_by,
                granted_at=ur.granted_at,
                expires_at=ur.expires_at,
            ))

    return result


@router.post("/{user_id}/roles", response_model=UserRoleAssignment, status_code=status.HTTP_201_CREATED)
async def assign_role(
    user_id: str,
    request: AssignRoleRequest,
    current_user: User = Depends(require_permissions(Permissions.MANAGE_USERS)),
    db: Session = Depends(get_db),
):
    """
    Assign a role to a user.

    Validates:
    - Role exists and matches scope type
    - Current user has permission to assign roles at this scope
    - Scope ID is valid (tenant/region exists)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check access to user
    is_super = role_service.is_super_admin(db, current_user.id)
    if not is_super:
        if user.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this user"
            )
        # Tenant admins can only assign tenant-scoped roles
        if request.scope_type.value != RoleScope.TENANT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only assign tenant-scoped roles"
            )

    # Validate scope_id
    scope_id = request.scope_id
    if request.scope_type.value == RoleScope.TENANT:
        if not scope_id:
            scope_id = user.tenant_id
        if not scope_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant scope requires scope_id"
            )
        # Verify tenant exists
        tenant = db.query(Tenant).filter(Tenant.id == scope_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
    elif request.scope_type.value == RoleScope.PLATFORM:
        if scope_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platform scope should not have scope_id"
            )
        # Only super admin can assign platform roles
        if not is_super:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can assign platform roles"
            )

    try:
        user_role = role_service.assign_role(
            db,
            user_id=user_id,
            role_name=request.role_name,
            scope_type=request.scope_type.value,
            scope_id=scope_id,
            granted_by=current_user.id,
            is_primary=request.is_primary,
            expires_at=request.expires_at,
        )
        db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Get role details for response
    role = db.query(Role).filter(Role.id == user_role.role_id).first()

    logger.info(f"Role assigned: {request.role_name} to user {user_id} by {current_user.id}")

    return UserRoleAssignment(
        id=user_role.id,
        role_id=user_role.role_id,
        role_name=role.name,
        role_display_name=role.display_name,
        scope_type=user_role.scope_type,
        scope_id=user_role.scope_id,
        is_primary=user_role.is_primary,
        granted_by=current_user.full_name,
        granted_at=user_role.granted_at,
        expires_at=user_role.expires_at,
    )


@router.delete("/{user_id}/roles", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_role(
    user_id: str,
    request: RevokeRoleRequest,
    current_user: User = Depends(require_permissions(Permissions.MANAGE_USERS)),
    db: Session = Depends(get_db),
):
    """
    Revoke a role from a user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check access
    is_super = role_service.is_super_admin(db, current_user.id)
    if not is_super:
        if user.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this user"
            )
        if request.scope_type.value != RoleScope.TENANT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only revoke tenant-scoped roles"
            )

    revoked = role_service.revoke_role(
        db,
        user_id=user_id,
        role_name=request.role_name,
        scope_type=request.scope_type.value,
        scope_id=request.scope_id,
    )

    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found"
        )

    db.commit()
    logger.info(f"Role revoked: {request.role_name} from user {user_id} by {current_user.id}")


# =============================================================================
# Roles Listing
# =============================================================================

@router.get("/roles/available", response_model=RoleListResponse)
async def list_available_roles(
    scope: Optional[str] = Query(None, description="Filter by scope (platform, regional, tenant)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List available roles.

    Returns roles that the current user can assign to others.
    """
    query = db.query(Role)

    is_super = role_service.is_super_admin(db, current_user.id)

    if scope:
        query = query.filter(Role.scope == scope)
    elif not is_super:
        # Non-super admins can only see tenant roles
        query = query.filter(Role.scope == RoleScope.TENANT)

    roles = query.order_by(Role.scope, Role.name).all()

    return RoleListResponse(
        roles=[RoleResponse(
            id=r.id,
            name=r.name,
            display_name=r.display_name,
            description=r.description,
            scope=r.scope,
            permissions=r.permissions,
            is_system=r.is_system,
        ) for r in roles],
        total=len(roles),
    )


# =============================================================================
# Bulk Operations
# =============================================================================

@router.post("/bulk", response_model=BulkActionResult)
async def bulk_user_action(
    request: BulkUserActionRequest,
    current_user: User = Depends(require_permissions(Permissions.MANAGE_USERS)),
    db: Session = Depends(get_db),
):
    """
    Perform bulk actions on users.

    Actions:
    - activate: Activate users
    - deactivate: Deactivate users
    - delete: Soft delete (deactivate) users
    """
    is_super = role_service.is_super_admin(db, current_user.id)

    success_count = 0
    failure_count = 0
    failures = []

    for user_id in request.user_ids:
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                failures.append({"user_id": user_id, "error": "User not found"})
                failure_count += 1
                continue

            # Check access
            if not is_super and user.tenant_id != current_user.tenant_id:
                failures.append({"user_id": user_id, "error": "Access denied"})
                failure_count += 1
                continue

            # Prevent self-action on deactivate/delete
            if user.id == current_user.id and request.action in ["deactivate", "delete"]:
                failures.append({"user_id": user_id, "error": "Cannot modify your own account"})
                failure_count += 1
                continue

            # Perform action
            if request.action == "activate":
                user.is_active = True
            elif request.action in ["deactivate", "delete"]:
                user.is_active = False

            user.updated_at = datetime.now(timezone.utc)
            success_count += 1

        except Exception as e:
            failures.append({"user_id": user_id, "error": str(e)})
            failure_count += 1

    db.commit()

    logger.info(
        f"Bulk action '{request.action}' completed: "
        f"{success_count} success, {failure_count} failures by {current_user.id}"
    )

    return BulkActionResult(
        success_count=success_count,
        failure_count=failure_count,
        failures=failures,
    )
