"""
Role and Permission models for multi-scope authorization.

Supports three scopes:
- Platform: Super admins, compliance officers, support agents
- Regional: Regional admins managing tenants in their region
- Tenant: Organization-level roles (admin, provider, staff, patient)

Security:
- Roles are system-defined and immutable
- User role assignments are scoped and time-limited
- Support access requires explicit consent from tenant
"""

from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import List, Optional
from datetime import datetime, timezone

from src.api.database import Base
from src.api.models.base import UUIDMixin, TimestampMixin


# Permission constants
class Permissions:
    """All available permissions in the system."""

    # Platform permissions
    MANAGE_REGIONS = "manage_regions"
    MANAGE_TENANTS = "manage_tenants"
    MANAGE_PLATFORM_USERS = "manage_platform_users"
    VIEW_ALL_ANALYTICS = "view_all_analytics"
    MANAGE_BILLING = "manage_billing"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    VIEW_CONSENT_RECORDS = "view_consent_records"
    GENERATE_COMPLIANCE_REPORTS = "generate_compliance_reports"
    VIEW_ANONYMIZED_DATA = "view_anonymized_data"
    MANAGE_SYSTEM_SETTINGS = "manage_system_settings"
    IMPERSONATE_USERS = "impersonate_users"

    # Regional permissions
    MANAGE_REGIONAL_TENANTS = "manage_regional_tenants"
    VIEW_REGIONAL_ANALYTICS = "view_regional_analytics"
    MANAGE_REGIONAL_USERS = "manage_regional_users"
    VIEW_REGIONAL_AUDIT_LOGS = "view_regional_audit_logs"
    SUPPORT_ACCESS = "support_access"

    # Tenant permissions
    MANAGE_USERS = "manage_users"
    MANAGE_SETTINGS = "manage_settings"
    VIEW_BILLING = "view_billing"
    MANAGE_INVITATIONS = "manage_invitations"
    CLINICAL_ACCESS = "clinical_access"
    MANAGE_PATIENTS = "manage_patients"
    TRANSCRIPTION = "transcription"
    VIEW_ANALYTICS = "view_analytics"
    VIEW_OWN_ANALYTICS = "view_own_analytics"
    MANAGE_APPOINTMENTS = "manage_appointments"
    MANAGE_TEMPLATES = "manage_templates"
    VIEW_PATIENTS = "view_patients"
    BASIC_CLINICAL = "basic_clinical"
    VIEW_OWN_DATA = "view_own_data"
    COMPLETE_QUESTIONNAIRES = "complete_questionnaires"
    MANAGE_OWN_APPOINTMENTS = "manage_own_appointments"

    # System permissions (for automated processes)
    SEND_NOTIFICATIONS = "send_notifications"
    PROCESS_BILLING = "process_billing"
    RUN_JOBS = "run_jobs"
    WRITE_ANALYTICS = "write_analytics"

    # Wildcard (super admin only)
    ALL = "*"


class RoleScope:
    """Role scope types."""
    PLATFORM = "platform"
    REGIONAL = "regional"
    TENANT = "tenant"


class Role(Base, UUIDMixin, TimestampMixin):
    """
    Role definition with permissions.

    Roles are system-defined and represent a set of permissions.
    Users are assigned roles through the UserRole table.

    Attributes:
        name: Unique role identifier (e.g., 'super_admin', 'provider')
        display_name: Human-readable name
        description: Role description
        scope: Role scope (platform, regional, tenant)
        permissions: JSON array of permission strings
        is_system: Whether this is a system role (cannot be deleted)
    """

    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    scope = Column(String(20), nullable=False)
    permissions = Column(JSONB, nullable=False, default=list)
    is_system = Column(Boolean, default=False, nullable=False)

    # Relationships
    user_roles = relationship("UserRole", back_populates="role", lazy="dynamic")

    __table_args__ = (
        CheckConstraint(
            "scope IN ('platform', 'regional', 'tenant')",
            name='roles_scope_check'
        ),
    )

    def __repr__(self):
        return f"<Role(name={self.name}, scope={self.scope})>"

    def has_permission(self, permission: str) -> bool:
        """Check if role has a specific permission."""
        if Permissions.ALL in self.permissions:
            return True
        return permission in self.permissions

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "scope": self.scope,
            "permissions": self.permissions,
            "is_system": self.is_system,
        }


class UserRole(Base, UUIDMixin):
    """
    User role assignment with scope.

    Links users to roles with a specific scope:
    - Platform scope: scope_id is NULL
    - Regional scope: scope_id is region_id
    - Tenant scope: scope_id is tenant_id

    Attributes:
        user_id: The user being assigned the role
        role_id: The role being assigned
        scope_type: Type of scope (platform, regional, tenant)
        scope_id: ID of the scope entity (region or tenant), NULL for platform
        is_primary: Whether this is the user's primary role
        granted_by: User who granted this role
        granted_at: When the role was granted
        expires_at: When the role expires (NULL for permanent)
    """

    __tablename__ = "user_roles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    scope_type = Column(String(20), nullable=False)
    scope_id = Column(String(36), nullable=True)  # NULL for platform scope
    is_primary = Column(Boolean, default=False, nullable=False)
    granted_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    granter = relationship("User", foreign_keys=[granted_by])

    __table_args__ = (
        CheckConstraint(
            "scope_type IN ('platform', 'regional', 'tenant')",
            name='user_roles_scope_type_check'
        ),
        Index('ix_user_roles_scope', 'scope_type', 'scope_id'),
    )

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id}, scope={self.scope_type})>"

    def is_expired(self) -> bool:
        """Check if the role assignment has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def is_active(self) -> bool:
        """Check if the role assignment is currently active."""
        return not self.is_expired()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role_id": self.role_id,
            "scope_type": self.scope_type,
            "scope_id": self.scope_id,
            "is_primary": self.is_primary,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class SupportAccessGrant(Base, UUIDMixin):
    """
    Time-limited support access grant for tenant.

    Allows support agents to access tenant data with explicit consent.
    All access is logged and automatically expires.

    Attributes:
        tenant_id: The tenant granting access
        granted_to_user_id: The support agent receiving access
        granted_by_user_id: The tenant admin who granted access
        reason: Reason for the support request
        access_level: Level of access (metadata or full)
        expires_at: When access expires (max 48 hours)
        revoked_at: When access was revoked (if revoked early)
        revoked_by: Who revoked the access
    """

    __tablename__ = "support_access_grants"

    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    granted_to_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    granted_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=False)
    access_level = Column(String(20), nullable=False)  # 'metadata' or 'full'
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant")
    granted_to = relationship("User", foreign_keys=[granted_to_user_id])
    granted_by = relationship("User", foreign_keys=[granted_by_user_id])
    revoker = relationship("User", foreign_keys=[revoked_by])

    __table_args__ = (
        CheckConstraint(
            "access_level IN ('metadata', 'full')",
            name='support_access_level_check'
        ),
        Index(
            'ix_support_access_grants_active',
            'granted_to_user_id',
            postgresql_where='revoked_at IS NULL'
        ),
    )

    def __repr__(self):
        return f"<SupportAccessGrant(tenant_id={self.tenant_id}, granted_to={self.granted_to_user_id})>"

    def is_active(self) -> bool:
        """Check if the grant is currently active."""
        if self.revoked_at is not None:
            return False
        return datetime.now(timezone.utc) < self.expires_at

    def revoke(self, revoked_by_user_id: str):
        """Revoke this access grant."""
        self.revoked_at = datetime.now(timezone.utc)
        self.revoked_by = revoked_by_user_id

    def to_dict(self):
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "granted_to_user_id": self.granted_to_user_id,
            "granted_by_user_id": self.granted_by_user_id,
            "reason": self.reason,
            "access_level": self.access_level,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "is_active": self.is_active(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Default role configurations (for seeding)
DEFAULT_ROLES = [
    {
        "name": "super_admin",
        "display_name": "Super Administrator",
        "description": "Full platform access",
        "scope": RoleScope.PLATFORM,
        "permissions": [Permissions.ALL],
        "is_system": True,
    },
    {
        "name": "compliance_officer",
        "display_name": "Compliance Officer",
        "description": "Compliance monitoring and audit access",
        "scope": RoleScope.PLATFORM,
        "permissions": [
            Permissions.VIEW_AUDIT_LOGS,
            Permissions.VIEW_CONSENT_RECORDS,
            Permissions.GENERATE_COMPLIANCE_REPORTS,
            Permissions.VIEW_ANONYMIZED_DATA,
        ],
        "is_system": True,
    },
    {
        "name": "regional_admin",
        "display_name": "Regional Administrator",
        "description": "Regional operations management",
        "scope": RoleScope.REGIONAL,
        "permissions": [
            Permissions.MANAGE_REGIONAL_TENANTS,
            Permissions.VIEW_REGIONAL_ANALYTICS,
            Permissions.SUPPORT_ACCESS,
            Permissions.MANAGE_REGIONAL_USERS,
        ],
        "is_system": True,
    },
    {
        "name": "support_agent",
        "display_name": "Support Agent",
        "description": "Customer support with consent-based access",
        "scope": RoleScope.PLATFORM,
        "permissions": [
            Permissions.SUPPORT_ACCESS,
        ],
        "is_system": True,
    },
    {
        "name": "system",
        "display_name": "System Account",
        "description": "Automated service account",
        "scope": RoleScope.PLATFORM,
        "permissions": [
            Permissions.SEND_NOTIFICATIONS,
            Permissions.PROCESS_BILLING,
            Permissions.RUN_JOBS,
            Permissions.WRITE_ANALYTICS,
        ],
        "is_system": True,
    },
    {
        "name": "tenant_admin",
        "display_name": "Organization Admin",
        "description": "Full organization management",
        "scope": RoleScope.TENANT,
        "permissions": [
            Permissions.MANAGE_USERS,
            Permissions.MANAGE_SETTINGS,
            Permissions.VIEW_BILLING,
            Permissions.MANAGE_BILLING,
            Permissions.MANAGE_INVITATIONS,
            Permissions.VIEW_ANALYTICS,
        ],
        "is_system": True,
    },
    {
        "name": "provider",
        "display_name": "Healthcare Provider",
        "description": "Clinical access for doctors and nurses",
        "scope": RoleScope.TENANT,
        "permissions": [
            Permissions.CLINICAL_ACCESS,
            Permissions.MANAGE_PATIENTS,
            Permissions.TRANSCRIPTION,
            Permissions.VIEW_OWN_ANALYTICS,
            Permissions.MANAGE_APPOINTMENTS,
            Permissions.MANAGE_TEMPLATES,
        ],
        "is_system": True,
    },
    {
        "name": "staff",
        "display_name": "Staff",
        "description": "Limited clinical and administrative access",
        "scope": RoleScope.TENANT,
        "permissions": [
            Permissions.VIEW_PATIENTS,
            Permissions.MANAGE_APPOINTMENTS,
            Permissions.BASIC_CLINICAL,
        ],
        "is_system": True,
    },
    {
        "name": "patient",
        "display_name": "Patient",
        "description": "Patient portal access",
        "scope": RoleScope.TENANT,
        "permissions": [
            Permissions.VIEW_OWN_DATA,
            Permissions.COMPLETE_QUESTIONNAIRES,
            Permissions.MANAGE_OWN_APPOINTMENTS,
        ],
        "is_system": True,
    },
]
