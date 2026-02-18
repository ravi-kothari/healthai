"""
Role and Permission Service for multi-scope authorization.

Supports three scopes:
- Platform: Super admins, compliance officers, support agents
- Regional: Regional admins managing tenants in their region
- Tenant: Organization-level roles (admin, provider, staff, patient)

This service provides the bridge between the new Role/UserRole models
and the auth dependencies.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Set
from datetime import datetime, timezone
import logging

from src.api.models.role import (
    Role, UserRole, SupportAccessGrant,
    Permissions, RoleScope
)
from src.api.models.user import User

logger = logging.getLogger(__name__)


def get_user_roles(
    db: Session,
    user_id: str,
    scope_type: Optional[str] = None,
    scope_id: Optional[str] = None,
    include_expired: bool = False
) -> List[UserRole]:
    """
    Get all active role assignments for a user.

    Args:
        db: Database session
        user_id: User ID to get roles for
        scope_type: Optional filter by scope type (platform, regional, tenant)
        scope_id: Optional filter by scope ID (region_id or tenant_id)
        include_expired: Whether to include expired role assignments

    Returns:
        List of UserRole assignments
    """
    query = db.query(UserRole).filter(UserRole.user_id == user_id)

    if scope_type:
        query = query.filter(UserRole.scope_type == scope_type)

    if scope_id:
        query = query.filter(UserRole.scope_id == scope_id)

    if not include_expired:
        now = datetime.now(timezone.utc)
        query = query.filter(
            (UserRole.expires_at.is_(None)) | (UserRole.expires_at > now)
        )

    return query.all()


def get_user_permissions(
    db: Session,
    user_id: str,
    scope_type: Optional[str] = None,
    scope_id: Optional[str] = None
) -> Set[str]:
    """
    Get all permissions for a user based on their role assignments.

    Args:
        db: Database session
        user_id: User ID
        scope_type: Optional filter by scope type
        scope_id: Optional filter by scope ID

    Returns:
        Set of permission strings
    """
    user_roles = get_user_roles(db, user_id, scope_type, scope_id)
    permissions: Set[str] = set()

    for user_role in user_roles:
        # Load the role to get permissions
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role and role.permissions:
            # Check for wildcard permission (super admin)
            if Permissions.ALL in role.permissions:
                return {Permissions.ALL}  # All permissions
            permissions.update(role.permissions)

    return permissions


def has_permission(
    db: Session,
    user_id: str,
    permission: str,
    scope_type: Optional[str] = None,
    scope_id: Optional[str] = None
) -> bool:
    """
    Check if a user has a specific permission.

    Args:
        db: Database session
        user_id: User ID
        permission: Permission string to check
        scope_type: Optional scope type filter
        scope_id: Optional scope ID filter

    Returns:
        True if user has the permission
    """
    permissions = get_user_permissions(db, user_id, scope_type, scope_id)

    # Check for wildcard (super admin has all)
    if Permissions.ALL in permissions:
        return True

    return permission in permissions


def has_any_permission(
    db: Session,
    user_id: str,
    permissions_to_check: List[str],
    scope_type: Optional[str] = None,
    scope_id: Optional[str] = None
) -> bool:
    """
    Check if a user has any of the specified permissions.

    Args:
        db: Database session
        user_id: User ID
        permissions_to_check: List of permission strings
        scope_type: Optional scope type filter
        scope_id: Optional scope ID filter

    Returns:
        True if user has at least one of the permissions
    """
    user_permissions = get_user_permissions(db, user_id, scope_type, scope_id)

    if Permissions.ALL in user_permissions:
        return True

    return bool(user_permissions.intersection(permissions_to_check))


def has_all_permissions(
    db: Session,
    user_id: str,
    permissions_to_check: List[str],
    scope_type: Optional[str] = None,
    scope_id: Optional[str] = None
) -> bool:
    """
    Check if a user has all of the specified permissions.

    Args:
        db: Database session
        user_id: User ID
        permissions_to_check: List of permission strings
        scope_type: Optional scope type filter
        scope_id: Optional scope ID filter

    Returns:
        True if user has all of the permissions
    """
    user_permissions = get_user_permissions(db, user_id, scope_type, scope_id)

    if Permissions.ALL in user_permissions:
        return True

    return set(permissions_to_check).issubset(user_permissions)


def get_user_primary_role(
    db: Session,
    user_id: str,
    scope_type: Optional[str] = None,
    scope_id: Optional[str] = None
) -> Optional[Role]:
    """
    Get the user's primary role for a scope.

    Args:
        db: Database session
        user_id: User ID
        scope_type: Optional scope type filter
        scope_id: Optional scope ID filter

    Returns:
        Primary Role or None
    """
    query = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.is_primary == True
    )

    if scope_type:
        query = query.filter(UserRole.scope_type == scope_type)
    if scope_id:
        query = query.filter(UserRole.scope_id == scope_id)

    now = datetime.now(timezone.utc)
    query = query.filter(
        (UserRole.expires_at.is_(None)) | (UserRole.expires_at > now)
    )

    user_role = query.first()
    if user_role:
        return db.query(Role).filter(Role.id == user_role.role_id).first()

    return None


def is_super_admin(db: Session, user_id: str) -> bool:
    """
    Check if user has super admin role (platform scope).

    Args:
        db: Database session
        user_id: User ID

    Returns:
        True if user is a super admin
    """
    # Get platform-scoped roles
    user_roles = get_user_roles(db, user_id, scope_type=RoleScope.PLATFORM)

    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role and role.name == "super_admin":
            return True

    return False


def is_regional_admin(db: Session, user_id: str, region_id: Optional[str] = None) -> bool:
    """
    Check if user has regional admin role.

    Args:
        db: Database session
        user_id: User ID
        region_id: Optional specific region to check

    Returns:
        True if user is a regional admin (for the specified region if provided)
    """
    user_roles = get_user_roles(
        db, user_id,
        scope_type=RoleScope.REGIONAL,
        scope_id=region_id
    )

    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role and role.name == "regional_admin":
            return True

    return False


def is_tenant_admin(db: Session, user_id: str, tenant_id: Optional[str] = None) -> bool:
    """
    Check if user has tenant admin role.

    Args:
        db: Database session
        user_id: User ID
        tenant_id: Optional specific tenant to check

    Returns:
        True if user is a tenant admin (for the specified tenant if provided)
    """
    user_roles = get_user_roles(
        db, user_id,
        scope_type=RoleScope.TENANT,
        scope_id=tenant_id
    )

    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role and role.name == "tenant_admin":
            return True

    return False


def can_access_tenant(db: Session, user_id: str, tenant_id: str) -> bool:
    """
    Check if user can access a specific tenant.

    Users can access a tenant if:
    1. They are a super admin (platform scope)
    2. They are a regional admin for the tenant's region
    3. They have a role assigned at the tenant scope for that tenant
    4. They have an active support access grant for that tenant

    Args:
        db: Database session
        user_id: User ID
        tenant_id: Tenant ID to check access for

    Returns:
        True if user can access the tenant
    """
    # Super admins can access any tenant
    if is_super_admin(db, user_id):
        return True

    # Check for tenant-scoped roles
    tenant_roles = get_user_roles(
        db, user_id,
        scope_type=RoleScope.TENANT,
        scope_id=tenant_id
    )
    if tenant_roles:
        return True

    # Check for regional admin access (would need to look up tenant's region)
    # For now, skip this as it requires tenant model relationship

    # Check for active support access grant
    if has_support_access(db, user_id, tenant_id):
        return True

    return False


def has_support_access(
    db: Session,
    user_id: str,
    tenant_id: str,
    access_level: Optional[str] = None
) -> bool:
    """
    Check if user has active support access to a tenant.

    Args:
        db: Database session
        user_id: Support agent user ID
        tenant_id: Tenant ID
        access_level: Optional required access level ('metadata' or 'full')

    Returns:
        True if user has active support access
    """
    now = datetime.now(timezone.utc)

    query = db.query(SupportAccessGrant).filter(
        SupportAccessGrant.granted_to_user_id == user_id,
        SupportAccessGrant.tenant_id == tenant_id,
        SupportAccessGrant.revoked_at.is_(None),
        SupportAccessGrant.expires_at > now
    )

    if access_level:
        query = query.filter(SupportAccessGrant.access_level == access_level)

    return query.first() is not None


def get_support_access_grant(
    db: Session,
    user_id: str,
    tenant_id: str
) -> Optional[SupportAccessGrant]:
    """
    Get the active support access grant for a user/tenant pair.

    Args:
        db: Database session
        user_id: Support agent user ID
        tenant_id: Tenant ID

    Returns:
        Active SupportAccessGrant or None
    """
    now = datetime.now(timezone.utc)

    return db.query(SupportAccessGrant).filter(
        SupportAccessGrant.granted_to_user_id == user_id,
        SupportAccessGrant.tenant_id == tenant_id,
        SupportAccessGrant.revoked_at.is_(None),
        SupportAccessGrant.expires_at > now
    ).first()


def assign_role(
    db: Session,
    user_id: str,
    role_name: str,
    scope_type: str,
    scope_id: Optional[str] = None,
    granted_by: Optional[str] = None,
    is_primary: bool = False,
    expires_at: Optional[datetime] = None
) -> UserRole:
    """
    Assign a role to a user.

    Args:
        db: Database session
        user_id: User to assign role to
        role_name: Name of the role to assign
        scope_type: Scope type (platform, regional, tenant)
        scope_id: Scope ID (None for platform, region_id or tenant_id)
        granted_by: User who is granting this role
        is_primary: Whether this is the user's primary role
        expires_at: Optional expiration datetime

    Returns:
        Created UserRole assignment

    Raises:
        ValueError: If role not found or invalid scope
    """
    # Find the role
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise ValueError(f"Role '{role_name}' not found")

    # Validate scope matches role scope
    if role.scope != scope_type:
        raise ValueError(
            f"Role '{role_name}' is {role.scope} scope but "
            f"{scope_type} scope was requested"
        )

    # Validate scope_id based on scope_type
    if scope_type == RoleScope.PLATFORM and scope_id:
        raise ValueError("Platform scope roles should not have scope_id")
    if scope_type in [RoleScope.REGIONAL, RoleScope.TENANT] and not scope_id:
        raise ValueError(f"{scope_type} scope roles require scope_id")

    # Check for existing assignment
    existing = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role.id,
        UserRole.scope_type == scope_type,
        UserRole.scope_id == scope_id
    ).first()

    if existing:
        # Update existing if needed
        if expires_at:
            existing.expires_at = expires_at
        if is_primary:
            existing.is_primary = is_primary
        return existing

    # Create new assignment
    user_role = UserRole(
        user_id=user_id,
        role_id=role.id,
        scope_type=scope_type,
        scope_id=scope_id,
        is_primary=is_primary,
        granted_by=granted_by,
        expires_at=expires_at
    )

    db.add(user_role)
    return user_role


def revoke_role(
    db: Session,
    user_id: str,
    role_name: str,
    scope_type: str,
    scope_id: Optional[str] = None
) -> bool:
    """
    Revoke a role from a user.

    Args:
        db: Database session
        user_id: User to revoke role from
        role_name: Name of the role to revoke
        scope_type: Scope type
        scope_id: Scope ID

    Returns:
        True if role was revoked, False if not found
    """
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        return False

    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role.id,
        UserRole.scope_type == scope_type,
        UserRole.scope_id == scope_id
    ).first()

    if user_role:
        db.delete(user_role)
        return True

    return False


def grant_support_access(
    db: Session,
    tenant_id: str,
    granted_to_user_id: str,
    granted_by_user_id: str,
    reason: str,
    access_level: str = "metadata",
    duration_hours: int = 24
) -> SupportAccessGrant:
    """
    Grant time-limited support access to a tenant.

    Args:
        db: Database session
        tenant_id: Tenant to grant access to
        granted_to_user_id: Support agent receiving access
        granted_by_user_id: Tenant admin granting access
        reason: Reason for the access request
        access_level: 'metadata' or 'full'
        duration_hours: Duration in hours (max 48)

    Returns:
        Created SupportAccessGrant

    Raises:
        ValueError: If invalid parameters
    """
    if access_level not in ["metadata", "full"]:
        raise ValueError("access_level must be 'metadata' or 'full'")

    if duration_hours > 48:
        raise ValueError("Support access cannot exceed 48 hours")

    expires_at = datetime.now(timezone.utc) + timedelta(hours=duration_hours)

    grant = SupportAccessGrant(
        tenant_id=tenant_id,
        granted_to_user_id=granted_to_user_id,
        granted_by_user_id=granted_by_user_id,
        reason=reason,
        access_level=access_level,
        expires_at=expires_at
    )

    db.add(grant)
    return grant


def revoke_support_access(
    db: Session,
    grant_id: str,
    revoked_by_user_id: str
) -> bool:
    """
    Revoke a support access grant.

    Args:
        db: Database session
        grant_id: ID of the grant to revoke
        revoked_by_user_id: User revoking the grant

    Returns:
        True if revoked, False if not found
    """
    grant = db.query(SupportAccessGrant).filter(
        SupportAccessGrant.id == grant_id
    ).first()

    if grant:
        grant.revoke(revoked_by_user_id)
        return True

    return False


# Import for duration calculation
from datetime import timedelta
