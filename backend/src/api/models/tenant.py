"""
Multi-tenant organization model for SaaS architecture.
Implements tenant isolation with Row-Level Security (RLS) support.

Security Features:
- Each tenant (organization) has complete data isolation
- Row-Level Security policies enforce access at database level
- Audit logging for compliance (HIPAA, SOC2)
- Subscription management with plan-based feature access
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from enum import Enum
from datetime import datetime
import uuid

from src.api.database import Base
from src.api.models.base import UUIDMixin, TimestampMixin


class SubscriptionPlan(str, Enum):
    """Available subscription plans."""
    TRIAL = "trial"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class TenantStatus(str, Enum):
    """Tenant account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_SETUP = "pending_setup"


class RegionCode(str, Enum):
    """Supported regional codes for internationalization."""
    US = "us"      # United States
    IN = "in"      # India
    CA = "ca"      # Canada
    UK = "uk"      # United Kingdom
    AE = "ae"      # UAE
    BR = "br"      # Brazil


class Region(Base):
    """
    Region model for internationalization and data residency.
    
    Each region represents a geographic/regulatory zone with:
    - Data residency requirements
    - Compliance framework (HIPAA, DPDP, PIPEDA, etc.)
    - Default language and currency
    - Region-specific feature flags
    
    Attributes:
        id: Short region code (us, in, ca, etc.)
        name: Human-readable region name
        default_language: Default UI language for the region
        supported_languages: List of supported languages
        default_currency: Currency code (USD, INR, CAD)
        timezone: Default timezone for the region
        compliance_framework: Primary compliance standard
        is_active: Whether the region is available for new tenants
    """
    
    __tablename__ = "regions"
    
    id = Column(String(10), primary_key=True)  # 'us', 'in', 'ca'
    name = Column(String(100), nullable=False)  # 'United States', 'India'
    
    # Localization
    default_language = Column(String(10), default="en", nullable=False)
    supported_languages = Column(JSON, default=["en"], nullable=False)
    default_currency = Column(String(3), default="USD", nullable=False)
    timezone = Column(String(50), nullable=False)
    
    # Compliance & Data Residency
    compliance_framework = Column(String(50), nullable=False)  # 'HIPAA', 'DPDP', 'PIPEDA'
    data_center_location = Column(String(100), nullable=True)  # 'Azure US East', 'Azure India'
    
    # Communication Channels
    primary_channel = Column(String(50), default="email", nullable=False)  # 'email', 'whatsapp', 'sms'
    whatsapp_enabled = Column(Boolean, default=False, nullable=False)
    sms_enabled = Column(Boolean, default=True, nullable=False)
    
    # Region-specific settings
    settings = Column(JSON, default=dict, nullable=False)
    """
    Settings JSON structure:
    {
        "payment_providers": ["stripe", "upi"],
        "ehr_integrations": ["epic", "cerner"],
        "features": {
            "telemedicine": true,
            "prescription_delivery": false
        }
    }
    """
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenants = relationship("Tenant", back_populates="region", lazy="dynamic")
    
    def __repr__(self):
        return f"<Region(id={self.id}, name={self.name}, compliance={self.compliance_framework})>"
    
    def to_dict(self):
        """Convert to API-safe dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "default_language": self.default_language,
            "supported_languages": self.supported_languages,
            "default_currency": self.default_currency,
            "timezone": self.timezone,
            "compliance_framework": self.compliance_framework,
            "whatsapp_enabled": self.whatsapp_enabled,
            "is_active": self.is_active,
        }
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported in this region."""
        return language_code in self.supported_languages


class Tenant(Base, UUIDMixin, TimestampMixin):
    """
    Tenant/Organization model - the core of multi-tenancy.

    Each tenant represents a healthcare organization (clinic, hospital, practice).
    All patient data, users, and clinical records are isolated per tenant.

    Attributes:
        id: Unique tenant identifier (UUID)
        name: Organization name
        slug: URL-friendly unique identifier
        domain: Custom domain for white-labeling (optional)
        settings: JSON configuration for tenant-specific settings
        subscription_*: Billing and subscription details

    Security:
        - Database RLS policies filter all queries by tenant_id
        - API middleware injects tenant context from JWT
        - Audit logs track all data access per tenant
    """

    __tablename__ = "tenants"

    # Region (for internationalization)
    region_id = Column(String(10), ForeignKey("regions.id"), nullable=True, default="us")

    # Basic Information
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    domain = Column(String(255), unique=True, nullable=True)  # For white-labeling

    # Contact Information
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="USA", nullable=False)

    # Organization Details
    tax_id = Column(String(50), nullable=True)  # EIN for US organizations
    npi_number = Column(String(20), nullable=True)  # National Provider Identifier
    organization_type = Column(String(100), nullable=True)  # clinic, hospital, practice, etc.

    # Status (stored as string to avoid SQLAlchemy enum/database mismatch)
    status = Column(String(50), default=TenantStatus.PENDING_SETUP.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Subscription Information (stored as string for flexibility)
    subscription_plan = Column(String(50), default=SubscriptionPlan.TRIAL.value, nullable=False)
    subscription_status = Column(String(50), default=SubscriptionStatus.TRIAL.value, nullable=False)

    @validates('status')
    def validate_status(self, key, value):
        """Validate status is a valid TenantStatus."""
        if isinstance(value, TenantStatus):
            return value.value
        if value not in [s.value for s in TenantStatus]:
            raise ValueError(f"Invalid status: {value}")
        return value

    @validates('subscription_plan')
    def validate_subscription_plan(self, key, value):
        """Validate subscription_plan is valid."""
        if isinstance(value, SubscriptionPlan):
            return value.value
        if value not in [p.value for p in SubscriptionPlan]:
            raise ValueError(f"Invalid subscription plan: {value}")
        return value

    @validates('subscription_status')
    def validate_subscription_status(self, key, value):
        """Validate subscription_status is valid."""
        if isinstance(value, SubscriptionStatus):
            return value.value
        if value not in [s.value for s in SubscriptionStatus]:
            raise ValueError(f"Invalid subscription status: {value}")
        return value
    subscription_started_at = Column(DateTime(timezone=True), nullable=True)
    subscription_ends_at = Column(DateTime(timezone=True), nullable=True)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)

    # Billing
    stripe_customer_id = Column(String(100), nullable=True, unique=True)
    stripe_subscription_id = Column(String(100), nullable=True, unique=True)
    billing_email = Column(String(255), nullable=True)

    # Feature Limits (based on plan)
    max_users = Column(Integer, default=5, nullable=False)
    max_patients = Column(Integer, default=100, nullable=False)
    max_storage_gb = Column(Integer, default=10, nullable=False)

    # Configuration (tenant-specific settings)
    settings = Column(JSON, default=dict, nullable=False)
    """
    Settings JSON structure:
    {
        "branding": {
            "logo_url": "...",
            "primary_color": "#...",
            "secondary_color": "#..."
        },
        "features": {
            "ai_assistant": true,
            "transcription": true,
            "fhir_integration": true,
            "careprep": true
        },
        "compliance": {
            "hipaa_baa_signed": true,
            "data_retention_days": 2555  # 7 years for HIPAA
        },
        "notifications": {
            "email_enabled": true,
            "sms_enabled": false
        }
    }
    """

    # Security & Compliance
    data_encryption_key_id = Column(String(255), nullable=True)  # For tenant-specific encryption
    last_security_audit = Column(DateTime(timezone=True), nullable=True)
    hipaa_baa_signed_at = Column(DateTime(timezone=True), nullable=True)

    # Onboarding
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    onboarding_step = Column(String(50), default="welcome", nullable=False)

    # Relationships
    region = relationship("Region", back_populates="tenants")
    users = relationship("User", back_populates="tenant", lazy="dynamic")
    # Note: Patient relationship will be added when Patient model gets tenant_id column
    # patients = relationship("Patient", back_populates="tenant", lazy="dynamic")
    audit_logs = relationship("AuditLog", back_populates="tenant", lazy="dynamic")

    # Indexes for performance
    __table_args__ = (
        Index('ix_tenants_status_active', 'status', 'is_active'),
        Index('ix_tenants_subscription', 'subscription_plan', 'subscription_status'),
    )

    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name}, plan={self.subscription_plan})>"

    def to_dict(self):
        """Convert model to dictionary (safe for API responses)."""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "domain": self.domain,
            "email": self.email,
            "phone": self.phone,
            "status": self.status.value if self.status else None,
            "is_active": self.is_active,
            "subscription_plan": self.subscription_plan.value if self.subscription_plan else None,
            "subscription_status": self.subscription_status.value if self.subscription_status else None,
            "max_users": self.max_users,
            "max_patients": self.max_patients,
            "onboarding_completed": self.onboarding_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled for this tenant."""
        features = self.settings.get("features", {})
        return features.get(feature_name, False)

    def can_add_user(self, current_count: int) -> bool:
        """Check if tenant can add more users based on plan limits."""
        return current_count < self.max_users

    def can_add_patient(self, current_count: int) -> bool:
        """Check if tenant can add more patients based on plan limits."""
        return current_count < self.max_patients


class AuditLog(Base, UUIDMixin):
    """
    Audit log for compliance tracking (HIPAA, SOC2).

    Records all data access and modifications for security and compliance.
    Immutable once created - logs cannot be modified or deleted.

    Required for:
    - HIPAA: Track all PHI access
    - SOC2: Security event logging
    - Legal: Evidence for investigations
    """

    __tablename__ = "audit_logs"

    # Tenant isolation
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)

    # Who performed the action
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)  # Denormalized for queries
    user_role = Column(String(50), nullable=True)

    # What action was performed
    action = Column(String(100), nullable=False)  # CREATE, READ, UPDATE, DELETE, LOGIN, etc.
    resource_type = Column(String(100), nullable=False)  # patient, visit, prescription, etc.
    resource_id = Column(String(36), nullable=True)

    # Request details
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    request_method = Column(String(10), nullable=True)
    request_path = Column(String(500), nullable=True)

    # Change details (for UPDATE actions)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)

    # Additional context
    description = Column(Text, nullable=True)
    extra_data = Column("metadata", JSON, nullable=True)  # Renamed to avoid SQLAlchemy reserved word

    # Timestamp (immutable)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="audit_logs")

    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_audit_logs_tenant_created', 'tenant_id', 'created_at'),
        Index('ix_audit_logs_user_action', 'user_id', 'action'),
        Index('ix_audit_logs_resource', 'resource_type', 'resource_id'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource={self.resource_type})>"


class TenantInvitation(Base, UUIDMixin, TimestampMixin):
    """
    Invitations for users to join a tenant/organization.

    Supports:
    - Email-based invitations with expiration
    - Role assignment during invitation
    - Single-use tokens for security
    """

    __tablename__ = "tenant_invitations"

    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)

    # Invitation details
    email = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="staff")

    # Security
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Status
    is_accepted = Column(Boolean, default=False, nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    accepted_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Tracking
    invited_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Relationships
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<TenantInvitation(email={self.email}, tenant_id={self.tenant_id})>"

    def is_valid(self) -> bool:
        """Check if invitation is still valid."""
        from datetime import datetime, timezone
        return not self.is_accepted and datetime.now(timezone.utc) < self.expires_at
