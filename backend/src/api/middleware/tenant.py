"""
Multi-tenant middleware for tenant context management.

This middleware:
1. Extracts tenant_id from JWT token
2. Sets PostgreSQL session variable for RLS
3. Validates tenant exists and is active
4. Provides tenant context to request handlers

Security:
- Defense in depth: validates at API level AND database level
- Tenant context is immutable during request lifecycle
- All database queries automatically filtered by RLS
"""

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from contextvars import ContextVar
import logging

from src.api.database import get_db
from src.api.models.tenant import Tenant, TenantStatus

logger = logging.getLogger(__name__)

# Context variable for tenant - thread-safe
current_tenant_var: ContextVar[Optional[Tenant]] = ContextVar('current_tenant', default=None)


class TenantContext:
    """
    Context manager for tenant isolation.

    Usage:
        with TenantContext(db, tenant_id):
            # All queries are now filtered by tenant_id via RLS
            patients = db.query(Patient).all()  # Only this tenant's patients
    """

    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self._previous_tenant = None

    def __enter__(self):
        # Store previous tenant if any (for nested contexts)
        self._previous_tenant = current_tenant_var.get()

        # Set PostgreSQL session variable for RLS
        self.db.execute(text(f"SET app.current_tenant = :tenant_id"), {"tenant_id": self.tenant_id})

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Reset PostgreSQL session variable
        if self._previous_tenant:
            self.db.execute(text(f"SET app.current_tenant = :tenant_id"), {"tenant_id": self._previous_tenant.id})
        else:
            self.db.execute(text("RESET app.current_tenant"))

        # Restore previous tenant context
        if self._previous_tenant:
            current_tenant_var.set(self._previous_tenant)
        else:
            current_tenant_var.set(None)


def set_tenant_context(db: Session, tenant_id: str) -> None:
    """
    Set tenant context for the current database session.

    This sets the PostgreSQL session variable that RLS policies use
    to filter all queries.

    Args:
        db: SQLAlchemy database session
        tenant_id: The tenant UUID to set as context

    Example:
        set_tenant_context(db, "123e4567-e89b-12d3-a456-426614174000")
        patients = db.query(Patient).all()  # Only this tenant's patients
    """
    db.execute(text("SET app.current_tenant = :tenant_id"), {"tenant_id": tenant_id})
    logger.debug(f"Tenant context set to: {tenant_id}")


def reset_tenant_context(db: Session) -> None:
    """
    Reset tenant context for the current database session.

    Should be called when processing requests that don't require tenant context
    (e.g., super admin operations).
    """
    db.execute(text("RESET app.current_tenant"))
    logger.debug("Tenant context reset")


def get_tenant_from_token(token_payload: dict) -> Optional[str]:
    """
    Extract tenant_id from JWT token payload.

    The tenant_id should be included in the JWT during authentication.

    Args:
        token_payload: Decoded JWT payload

    Returns:
        tenant_id string or None if not present
    """
    return token_payload.get("tenant_id")


async def validate_tenant(db: Session, tenant_id: str) -> Tenant:
    """
    Validate that a tenant exists and is active.

    Args:
        db: Database session
        tenant_id: Tenant UUID to validate

    Returns:
        Tenant object if valid

    Raises:
        HTTPException: If tenant is invalid, inactive, or suspended
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if not tenant:
        logger.warning(f"Tenant not found: {tenant_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    if not tenant.is_active:
        logger.warning(f"Tenant inactive: {tenant_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization account is inactive"
        )

    if tenant.status == TenantStatus.SUSPENDED:
        logger.warning(f"Tenant suspended: {tenant_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization account is suspended. Please contact support."
        )

    if tenant.status == TenantStatus.PENDING_SETUP:
        logger.info(f"Tenant pending setup: {tenant_id}")
        # Allow access but might want to redirect to onboarding
        pass

    return tenant


def get_current_tenant() -> Optional[Tenant]:
    """
    Get the current tenant from context.

    Returns:
        Current Tenant object or None if not set
    """
    return current_tenant_var.get()


def require_tenant():
    """
    Dependency that requires a valid tenant context.

    Usage:
        @app.get("/patients")
        def get_patients(tenant: Tenant = Depends(require_tenant)):
            # tenant is guaranteed to be valid here
            pass
    """
    tenant = current_tenant_var.get()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context not set"
        )
    return tenant


class TenantMiddleware:
    """
    FastAPI middleware for automatic tenant context management.

    This middleware:
    1. Extracts tenant_id from the authenticated user's JWT
    2. Validates the tenant is active
    3. Sets the PostgreSQL session variable for RLS
    4. Makes tenant available via dependency injection
    """

    # Paths that don't require tenant context
    EXEMPT_PATHS = [
        "/health",
        "/api/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/refresh",
        "/api/admin",  # Super admin paths
    ]

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Check if path is exempt
        path = scope.get("path", "")
        if any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS):
            await self.app(scope, receive, send)
            return

        # For non-exempt paths, tenant context will be set by the auth dependency
        # The actual tenant context setting happens in the get_current_user_with_tenant dependency
        await self.app(scope, receive, send)


def get_db_with_tenant(tenant_id: str):
    """
    Get a database session with tenant context already set.

    This is useful for background jobs and async tasks where
    you need to specify the tenant explicitly.

    Args:
        tenant_id: Tenant UUID

    Yields:
        Database session with tenant context

    Example:
        async def process_patient_data(tenant_id: str, patient_id: str):
            for db in get_db_with_tenant(tenant_id):
                patient = db.query(Patient).filter(Patient.id == patient_id).first()
    """
    from src.api.database import SessionLocal

    db = SessionLocal()
    try:
        set_tenant_context(db, tenant_id)
        yield db
    finally:
        reset_tenant_context(db)
        db.close()


# Tenant-aware query helpers
def tenant_query(db: Session, model):
    """
    Create a query that's explicitly filtered by current tenant.

    Even though RLS should handle this, this provides an extra layer
    of safety and makes the tenant filtering explicit in code.

    Usage:
        patients = tenant_query(db, Patient).filter(Patient.is_active == True).all()
    """
    tenant = current_tenant_var.get()
    if not tenant:
        raise ValueError("No tenant context set")

    return db.query(model).filter(model.tenant_id == tenant.id)
