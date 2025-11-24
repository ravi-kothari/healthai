"""
Base model with common fields for all database models.

Multi-tenant SaaS Architecture:
- All tenant-specific data must use TenantMixin
- Row-Level Security (RLS) enforced at database level
- Audit logging for compliance (HIPAA, SOC2)
"""

from sqlalchemy import Column, DateTime, String, ForeignKey, Index, event
from sqlalchemy.sql import func
from sqlalchemy.orm import declared_attr
from datetime import datetime
import uuid


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class UUIDMixin:
    """Mixin for UUID primary key."""

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class TenantMixin:
    """
    Mixin for multi-tenant data isolation.

    CRITICAL: All models containing tenant-specific data MUST include this mixin.

    How it works:
    1. Every record has a tenant_id foreign key
    2. PostgreSQL RLS policies filter queries automatically
    3. API middleware sets tenant context from JWT
    4. Database connection sets app.current_tenant for RLS

    Security:
    - Even if application code has bugs, RLS prevents cross-tenant access
    - Defense in depth: application + database level isolation
    """

    @declared_attr
    def tenant_id(cls):
        return Column(
            String(36),
            ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )

    @declared_attr
    def __table_args__(cls):
        # Add composite index for tenant + common query patterns
        existing_args = getattr(super(), '__table_args__', ())
        if isinstance(existing_args, dict):
            existing_args = (existing_args,)
        elif existing_args is None:
            existing_args = ()

        # Create index name based on table name
        return existing_args + (
            Index(f'ix_{cls.__tablename__}_tenant_id', 'tenant_id'),
        )


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality.

    Instead of permanently deleting records, mark them as deleted.
    Required for:
    - HIPAA compliance (data retention requirements)
    - Audit trail maintenance
    - Data recovery capabilities
    """

    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(String(36), nullable=True)

    @property
    def is_deleted(self) -> bool:
        """Check if record is soft deleted."""
        return self.deleted_at is not None

    def soft_delete(self, user_id: str = None):
        """Mark record as deleted."""
        self.deleted_at = datetime.utcnow()
        self.deleted_by = user_id


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


# SQL Templates for Row-Level Security
RLS_POLICIES = """
-- Enable Row-Level Security on table
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;

-- Force RLS for table owner as well (important!)
ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;

-- Policy: Users can only see data from their tenant
CREATE POLICY tenant_isolation_policy ON {table_name}
    USING (tenant_id = current_setting('app.current_tenant')::text);

-- Policy: Users can only insert data for their tenant
CREATE POLICY tenant_insert_policy ON {table_name}
    FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant')::text);

-- Policy: Users can only update data from their tenant
CREATE POLICY tenant_update_policy ON {table_name}
    FOR UPDATE
    USING (tenant_id = current_setting('app.current_tenant')::text)
    WITH CHECK (tenant_id = current_setting('app.current_tenant')::text);

-- Policy: Users can only delete data from their tenant
CREATE POLICY tenant_delete_policy ON {table_name}
    FOR DELETE
    USING (tenant_id = current_setting('app.current_tenant')::text);
"""

# SQL to set tenant context for a database session
SET_TENANT_CONTEXT = "SET app.current_tenant = '{tenant_id}';"

# SQL to reset tenant context
RESET_TENANT_CONTEXT = "RESET app.current_tenant;"
