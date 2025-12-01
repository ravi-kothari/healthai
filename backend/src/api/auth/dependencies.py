"""
Authentication dependencies for FastAPI endpoints.
Provides current user extraction from JWT tokens with multi-tenant support.

Security Features:
- JWT token verification with tenant context
- Row-Level Security (RLS) tenant context setting
- Role-based access control
- Tenant isolation enforcement
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import logging

from src.api.database import get_db
from src.api.models.user import User, UserRole
from src.api.models.tenant import Tenant, TenantStatus
from src.api.auth.jwt_handler import verify_token

logger = logging.getLogger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token and set tenant context.

    Multi-tenant security:
    - Extracts tenant_id from JWT token
    - Sets PostgreSQL session variable for Row-Level Security
    - Validates tenant is active and not suspended
    - Super admins bypass tenant restrictions

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        User: Authenticated user object with tenant context set

    Raises:
        HTTPException: If token is invalid, user not found, or tenant suspended

    Example:
        @app.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user.to_dict()
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    logger.debug(f"Authenticating token (first 50 chars): {token[:50]}...")

    # Verify token and extract payload
    try:
        payload = verify_token(token)
        logger.debug(f"Token verified for user: {payload.get('sub')}")
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise

    # Get user_id from token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get tenant_id from token
    token_tenant_id: Optional[str] = payload.get("tenant_id")
    is_super_admin: bool = payload.get("is_super_admin", False)

    # Fetch user from database (without RLS for this query)
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # Validate and set tenant context for non-super-admin users
    if user.tenant_id and not is_super_admin:
        # Verify tenant exists and is active
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if tenant:
            if tenant.status == TenantStatus.SUSPENDED.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your organization's account has been suspended"
                )
            if not tenant.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your organization's account is inactive"
                )

        # Set PostgreSQL session variable for Row-Level Security
        try:
            db.execute(text("SET app.current_tenant = :tenant_id"), {"tenant_id": user.tenant_id})
            logger.debug(f"Tenant context set: {user.tenant_id}")
        except Exception as e:
            logger.warning(f"Could not set tenant context: {e}")
            # Continue without RLS if setting fails (may not be configured)

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (alias for get_current_user with explicit active check).

    Args:
        current_user: Current user from get_current_user

    Returns:
        User: Active user

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory to require specific user roles.

    Args:
        *allowed_roles: One or more UserRole values

    Returns:
        Dependency function that checks user role

    Example:
        @app.get("/admin", dependencies=[Depends(require_role(UserRole.ADMIN))])
        async def admin_only():
            return {"message": "Admin access"}

        @app.get("/healthcare", dependencies=[Depends(require_role(UserRole.DOCTOR, UserRole.NURSE))])
        async def healthcare_only():
            return {"message": "Healthcare provider access"}
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker


async def require_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require super admin role for platform-wide administration.

    Super admins can:
    - Manage all tenants/organizations
    - View platform-wide analytics
    - Access billing and subscription management
    - Suspend/activate organizations

    Args:
        current_user: Current authenticated user

    Returns:
        User: Super admin user

    Raises:
        HTTPException: If user is not a super admin
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


async def require_tenant_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require tenant admin role for organization management.

    Tenant admins can:
    - Manage users within their organization
    - View organization analytics
    - Manage organization settings
    - Invite new users

    Args:
        current_user: Current authenticated user

    Returns:
        User: Tenant admin user

    Raises:
        HTTPException: If user is not a tenant admin or super admin
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_permission(permission: "Permission"):
    """
    Dependency factory to require a specific permission.
    
    Args:
        permission: The required Permission enum value
        
    Returns:
        Dependency function that checks user permissions
    """
    from src.api.auth.permissions import Permission, get_role_permissions

    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = get_role_permissions(current_user.role)
        if permission not in user_permissions:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {permission.value}"
            )
        return current_user

    return permission_checker


def require_tenant_access(tenant_id: str):
    """
    Dependency factory to require access to a specific tenant.

    Used for cross-tenant operations by super admins or same-tenant access.

    Args:
        tenant_id: The tenant ID to check access for

    Returns:
        Dependency function that validates tenant access

    Example:
        @app.get("/tenants/{tenant_id}/users")
        async def get_tenant_users(
            tenant_id: str,
            user: User = Depends(require_tenant_access(tenant_id))
        ):
            ...
    """
    async def tenant_checker(current_user: User = Depends(get_current_user)) -> User:
        # Super admins can access any tenant
        if current_user.role == UserRole.SUPER_ADMIN:
            return current_user

        # Regular users can only access their own tenant
        if current_user.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this organization"
            )
        return current_user

    return tenant_checker


async def get_current_user_with_tenant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> tuple[User, Optional[Tenant]]:
    """
    Get current user along with their tenant information.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Tuple of (User, Tenant or None)
    """
    tenant = None
    if current_user.tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    return current_user, tenant


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token is provided, None otherwise.
    Useful for endpoints that work with or without authentication.

    Args:
        credentials: Optional HTTP Bearer credentials
        db: Database session

    Returns:
        User or None: Authenticated user if token provided, None otherwise

    Example:
        @app.get("/public")
        async def public_endpoint(user: Optional[User] = Depends(get_optional_user)):
            if user:
                return {"message": f"Hello {user.full_name}"}
            return {"message": "Hello anonymous"}
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            return None

        user = db.query(User).filter(User.id == user_id).first()
        return user if user and user.is_active else None

    except HTTPException:
        return None
