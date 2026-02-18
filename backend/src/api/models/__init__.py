"""
Database models package.

Multi-tenant SaaS Architecture:
- Tenant: Organization/company using the platform
- All tenant-specific data includes tenant_id for RLS
- AuditLog: Immutable compliance logging

Role System:
- Role: System-defined roles with permissions (platform, regional, tenant scopes)
- UserRole: User role assignments with scope
- SupportAccessGrant: Time-limited consent-based support access
"""

from src.api.models.user import User, UserRole as UserRoleEnum
from src.api.models.role import (
    Role, UserRole, SupportAccessGrant,
    Permissions, RoleScope, DEFAULT_ROLES
)
from src.api.models.patient import Patient
from src.api.models.appointment import Appointment
from src.api.models.visit import Visit, Transcript, VisitStatus, VisitType, TranscriptionStatus
from src.api.models.clinical import (
    Medication, MedicationStatus,
    LabResult, LabOrder, LabResultStatus, LabOrderStatus,
    Allergy, AllergySeverity, AllergyStatus,
    Condition, ConditionStatus,
    ImagingStudy, ImagingModality, ImagingStatus,
    ClinicalDocument, DocumentType,
    CarePlan, CareGoal, FollowUpInstruction,
    CareGoalStatus, InstructionCategory, InstructionPriority
)
from src.api.models.template import Template, TemplateType, TemplateCategory
from src.api.models.tenant import (
    Tenant, TenantStatus, SubscriptionPlan, SubscriptionStatus,
    AuditLog, TenantInvitation
)
from src.api.models.region import Region, DEFAULT_REGIONS
from src.api.models.clinic import Clinic, ClinicStatus, ClinicType, UserClinicAccess
from src.api.models.consent import (
    ConsentRecord, ConsentBundle, ConsentPurpose, ConsentStatus,
    has_consent, get_active_consent, require_consent, REGIONAL_CONSENT_REQUIREMENTS
)
from src.api.models.base import TenantMixin, SoftDeleteMixin
from src.api.models.billing import (
    Invoice, PaymentMethod, BillingEvent,
    PaymentProvider, InvoiceStatus, PaymentMethodType,
    PLAN_FEATURES, get_plan_features, get_plan_price, is_feature_available
)
from src.api.models.analytics import (
    AnalyticsMetric, AnalyticsSnapshot, ScheduledReport, ReportExecution,
    MetricScope, MetricPeriod, METRIC_DEFINITIONS, get_metric_definition
)

__all__ = [
    # Multi-tenant
    "Tenant", "TenantStatus", "SubscriptionPlan", "SubscriptionStatus",
    "AuditLog", "TenantInvitation",
    "Region", "DEFAULT_REGIONS",
    "Clinic", "ClinicStatus", "ClinicType", "UserClinicAccess",
    # Consent (DPDP/GDPR compliance)
    "ConsentRecord", "ConsentBundle", "ConsentPurpose", "ConsentStatus",
    "has_consent", "get_active_consent", "require_consent", "REGIONAL_CONSENT_REQUIREMENTS",
    "TenantMixin", "SoftDeleteMixin",
    # Users
    "User", "UserRoleEnum",  # UserRoleEnum is legacy enum, use Role/UserRole for new system
    # Roles & Permissions (new system)
    "Role", "UserRole", "SupportAccessGrant",
    "Permissions", "RoleScope", "DEFAULT_ROLES",
    # Core models
    "Patient", "Appointment",
    "Visit", "Transcript", "VisitStatus", "VisitType", "TranscriptionStatus",
    # Clinical
    "Medication", "MedicationStatus",
    "LabResult", "LabOrder", "LabResultStatus", "LabOrderStatus",
    "Allergy", "AllergySeverity", "AllergyStatus",
    "Condition", "ConditionStatus",
    "ImagingStudy", "ImagingModality", "ImagingStatus",
    "ClinicalDocument", "DocumentType",
    "CarePlan", "CareGoal", "FollowUpInstruction",
    "CareGoalStatus", "InstructionCategory", "InstructionPriority",
    # Templates
    "Template", "TemplateType", "TemplateCategory",
    # Billing
    "Invoice", "PaymentMethod", "BillingEvent",
    "PaymentProvider", "InvoiceStatus", "PaymentMethodType",
    "PLAN_FEATURES", "get_plan_features", "get_plan_price", "is_feature_available",
    # Analytics
    "AnalyticsMetric", "AnalyticsSnapshot", "ScheduledReport", "ReportExecution",
    "MetricScope", "MetricPeriod", "METRIC_DEFINITIONS", "get_metric_definition",
]
