"""
Authentication router with login, register, and token management endpoints.
Includes multi-tenant support with tenant_id in JWT tokens.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
import logging

from src.api.database import get_db
from src.api.models.user import User, UserRole
from src.api.models.tenant import Tenant, TenantStatus
from src.api.schemas.auth_schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    TenantInfo,
    UserRoleUpdateRequest,
)
from src.api.auth.password import hash_password, verify_password
from src.api.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from src.api.auth.dependencies import get_current_user
from src.api.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Default tenant ID for development
DEFAULT_TENANT_ID = "defa0000-0000-0000-0000-000000000001"


def _build_user_response(user: User, db: Session) -> UserResponse:
    """Build UserResponse with tenant information."""
    tenant_info = None
    if user.tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if tenant:
            # subscription_plan is now stored as string, not enum
            plan = tenant.subscription_plan if isinstance(tenant.subscription_plan, str) else (
                tenant.subscription_plan.value if hasattr(tenant.subscription_plan, 'value') else "trial"
            )
            tenant_info = TenantInfo(
                id=tenant.id,
                name=tenant.name,
                slug=tenant.slug,
                subscription_plan=plan
            )

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        is_active=user.is_active,
        is_verified=user.is_verified,
        tenant_id=user.tenant_id,
        tenant=tenant_info
    )


def _create_tokens_with_tenant(user: User) -> tuple[str, str]:
    """Create access and refresh tokens with tenant context."""
    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
    }

    # Include tenant_id for non-super-admin users
    if user.tenant_id:
        token_data["tenant_id"] = user.tenant_id

    # Mark super admins in token
    if user.role == UserRole.SUPER_ADMIN:
        token_data["is_super_admin"] = True

    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data={"sub": user.id, "tenant_id": user.tenant_id})

    return access_token, refresh_token


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    For multi-tenant support:
    - Regular users are assigned to the default tenant during public registration
    - Tenant-specific registration should use the tenant invitation flow
    - Super admins have no tenant_id

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        AuthResponse: User data with access tokens

    Raises:
        HTTPException: If username or email already exists
    """
    logger.info(f"Registration attempt for username: {user_data.username}")

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        logger.warning(f"Registration failed: username {user_data.username} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        logger.warning(f"Registration failed: email {user_data.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Get the default tenant (for development/public registration)
    default_tenant = db.query(Tenant).filter(Tenant.id == DEFAULT_TENANT_ID).first()
    if not default_tenant:
        logger.warning("Default tenant not found, creating user without tenant")
        tenant_id = None
    else:
        tenant_id = default_tenant.id

    # Create new user with tenant
    try:
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            phone=user_data.phone,
            role=user_data.role,
            tenant_id=tenant_id,  # Assign to default tenant
            is_active=True,
            is_verified=False  # Email verification would be implemented separately
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"User registered successfully: {new_user.id} in tenant: {tenant_id}")

        # Create tokens with tenant context
        access_token, refresh_token = _create_tokens_with_tenant(new_user)

        return AuthResponse(
            user=_build_user_response(new_user, db),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed due to database constraint"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with username/email and password.

    Multi-tenant features:
    - JWT token includes tenant_id for data isolation
    - Validates tenant status (suspended tenants block login)
    - Super admins can login without tenant context

    Args:
        credentials: Login credentials
        db: Database session

    Returns:
        AuthResponse: User data with access tokens

    Raises:
        HTTPException: If credentials are invalid or tenant is suspended
    """
    logger.info(f"Login attempt for username: {credentials.username}")

    # Find user by username or email
    user = db.query(User).filter(
        (User.username == credentials.username) | (User.email == credentials.username)
    ).first()

    if not user:
        logger.warning(f"Login failed: user not found for {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Login failed: incorrect password for {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login failed: inactive user {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Check tenant status (skip for super admins)
    if user.tenant_id and user.role != UserRole.SUPER_ADMIN:
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if tenant:
            if tenant.status == TenantStatus.SUSPENDED.value:
                logger.warning(f"Login failed: tenant suspended for {credentials.username}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your organization's account has been suspended. Please contact support."
                )
            if not tenant.is_active:
                logger.warning(f"Login failed: tenant inactive for {credentials.username}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your organization's account is inactive. Please contact support."
                )

    logger.info(f"User logged in successfully: {user.id} (tenant: {user.tenant_id})")

    # Create tokens with tenant context
    access_token, refresh_token = _create_tokens_with_tenant(user)

    return AuthResponse(
        user=_build_user_response(user, db),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    Multi-tenant features:
    - Re-validates tenant status on refresh
    - Creates new token with current tenant_id

    Args:
        refresh_data: Refresh token
        db: Database session

    Returns:
        TokenResponse: New access token

    Raises:
        HTTPException: If refresh token is invalid or tenant suspended
    """
    # Verify refresh token
    payload = verify_token(refresh_data.refresh_token)

    # Check token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Re-check tenant status on refresh
    if user.tenant_id and user.role != UserRole.SUPER_ADMIN:
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if tenant and (tenant.status == TenantStatus.SUSPENDED.value or not tenant.is_active):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your organization's account has been suspended or deactivated."
            )

    # Create new access token with tenant context
    access_token, _ = _create_tokens_with_tenant(user)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information with tenant details.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserResponse: User information with tenant details
    """
    return _build_user_response(current_user, db)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user.

    Note: In a stateless JWT system, logout is handled client-side by deleting the token.
    This endpoint is provided for consistency and could be extended with token blacklisting.

    Args:
        current_user: Current authenticated user

    Returns:
        dict: Success message
    """
    logger.info(f"User logged out: {current_user.id}")
    return {
        "message": "Successfully logged out",
        "detail": "Please delete the token on the client side"
    }


@router.get("/users", response_model=list[UserResponse])
async def list_tenant_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all users in the current user's tenant.
    Requires admin or super_admin role.
    """
    # Check permissions (must be admin or super admin)
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    if current_user.role == UserRole.SUPER_ADMIN:
        # Super admin sees all users (or could filter by tenant_id query param)
        # For now, let's just return all users for super admin
        users = db.query(User).all()
    else:
        # Tenant admin sees only their tenant's users
        if not current_user.tenant_id:
            return []
        users = db.query(User).filter(User.tenant_id == current_user.tenant_id).all()

    return [_build_user_response(u, db) for u in users]


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    role_update: UserRoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a user's role.
    Requires admin or super_admin role.
    """
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Find target user
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check tenant isolation
    if current_user.role != UserRole.SUPER_ADMIN:
        if target_user.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

    # Update role
    target_user.role = role_update.role
    db.commit()
    db.refresh(target_user)

    logger.info(f"User role updated: {target_user.id} -> {role_update.role}")
    return _build_user_response(target_user, db)
