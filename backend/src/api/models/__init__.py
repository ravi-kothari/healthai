"""
Database models package.

Multi-tenant SaaS Architecture:
- Tenant: Organization/company using the platform
- All tenant-specific data includes tenant_id for RLS
- AuditLog: Immutable compliance logging
"""

from src.api.models.user import User, UserRole
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
from src.api.models.base import TenantMixin, SoftDeleteMixin

__all__ = [
    # Multi-tenant
    "Tenant", "TenantStatus", "SubscriptionPlan", "SubscriptionStatus",
    "AuditLog", "TenantInvitation",
    "TenantMixin", "SoftDeleteMixin",
    # Users
    "User", "UserRole",
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
    "Template", "TemplateType", "TemplateCategory"
]
