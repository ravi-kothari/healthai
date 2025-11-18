"""
Clinical Data Models.
Tracks medications, lab results, allergies, conditions, imaging, documents, and care plans.
"""

from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.api.database import Base


# Enums
class MedicationStatus(str, enum.Enum):
    """Medication status enumeration."""
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    COMPLETED = "completed"


class LabResultStatus(str, enum.Enum):
    """Lab result status enumeration."""
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    CRITICAL = "critical"


class LabOrderStatus(str, enum.Enum):
    """Lab order status enumeration."""
    PENDING = "pending"
    COLLECTED = "collected"
    RESULTED = "resulted"
    CANCELLED = "cancelled"


class AllergySeverity(str, enum.Enum):
    """Allergy severity enumeration."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    LIFE_THREATENING = "life-threatening"


class AllergyStatus(str, enum.Enum):
    """Allergy status enumeration."""
    ACTIVE = "active"
    RESOLVED = "resolved"


class ConditionStatus(str, enum.Enum):
    """Condition status enumeration."""
    ACTIVE = "active"
    CHRONIC = "chronic"
    RESOLVED = "resolved"


class ImagingModality(str, enum.Enum):
    """Imaging modality enumeration."""
    XRAY = "X-Ray"
    CT = "CT"
    MRI = "MRI"
    ULTRASOUND = "Ultrasound"
    PET = "PET"
    NUCLEAR_MEDICINE = "Nuclear Medicine"
    OTHER = "Other"


class ImagingStatus(str, enum.Enum):
    """Imaging status enumeration."""
    ORDERED = "ordered"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DocumentType(str, enum.Enum):
    """Document type enumeration."""
    DISCHARGE_SUMMARY = "discharge_summary"
    OPERATIVE_REPORT = "operative_report"
    CONSULTATION = "consultation"
    REFERRAL = "referral"
    LAB_REPORT = "lab_report"
    IMAGING_REPORT = "imaging_report"
    CONSENT_FORM = "consent_form"
    OTHER = "other"


class CareGoalStatus(str, enum.Enum):
    """Care goal status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    DISCONTINUED = "discontinued"


class InstructionCategory(str, enum.Enum):
    """Instruction category enumeration."""
    MEDICATION = "medication"
    LIFESTYLE = "lifestyle"
    APPOINTMENT = "appointment"
    MONITORING = "monitoring"
    DIET = "diet"
    EXERCISE = "exercise"
    OTHER = "other"


class InstructionPriority(str, enum.Enum):
    """Instruction priority enumeration."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Models
class Medication(Base):
    """Medication model - tracks patient medications."""
    __tablename__ = "medications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)

    name = Column(String(200), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    route = Column(String(50), nullable=False)  # oral, topical, injection, etc.

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

    prescriber = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(SQLEnum(MedicationStatus), nullable=False, default=MedicationStatus.ACTIVE)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="medications")


class LabResult(Base):
    """Lab result model - tracks laboratory test results."""
    __tablename__ = "lab_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    visit_id = Column(String(36), ForeignKey("visits.id"), nullable=True)

    test_name = Column(String(200), nullable=False)
    result_value = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=True)
    reference_range = Column(String(100), nullable=True)
    status = Column(SQLEnum(LabResultStatus), nullable=False, default=LabResultStatus.NORMAL)

    date_collected = Column(DateTime, nullable=False)
    date_resulted = Column(DateTime, nullable=False)

    ordered_by = Column(String(200), nullable=True)
    lab_name = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="lab_results")


class LabOrder(Base):
    """Lab order model - tracks pending/scheduled lab orders."""
    __tablename__ = "lab_orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    visit_id = Column(String(36), ForeignKey("visits.id"), nullable=True)

    test_name = Column(String(200), nullable=False)
    ordered_date = Column(DateTime, nullable=False)
    status = Column(SQLEnum(LabOrderStatus), nullable=False, default=LabOrderStatus.PENDING)
    priority = Column(String(20), nullable=False, default="routine")  # routine, urgent, stat

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="lab_orders")


class Allergy(Base):
    """Allergy model - tracks patient allergies."""
    __tablename__ = "allergies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)

    allergen = Column(String(200), nullable=False)
    reaction = Column(Text, nullable=False)
    severity = Column(SQLEnum(AllergySeverity), nullable=False)
    onset_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(SQLEnum(AllergyStatus), nullable=False, default=AllergyStatus.ACTIVE)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="allergies")


class Condition(Base):
    """Condition model - tracks patient conditions/diagnoses."""
    __tablename__ = "conditions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)

    name = Column(String(200), nullable=False)
    icd10_code = Column(String(20), nullable=True)
    status = Column(SQLEnum(ConditionStatus), nullable=False, default=ConditionStatus.ACTIVE)
    onset_date = Column(DateTime, nullable=True)
    resolved_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="conditions")


class ImagingStudy(Base):
    """Imaging study model - tracks imaging/radiology studies."""
    __tablename__ = "imaging_studies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    visit_id = Column(String(36), ForeignKey("visits.id"), nullable=True)

    study_type = Column(String(200), nullable=False)
    body_part = Column(String(100), nullable=False)
    modality = Column(SQLEnum(ImagingModality), nullable=False)
    study_date = Column(DateTime, nullable=False)

    ordering_provider = Column(String(200), nullable=True)
    radiologist = Column(String(200), nullable=True)
    findings = Column(Text, nullable=True)
    impression = Column(Text, nullable=True)

    status = Column(SQLEnum(ImagingStatus), nullable=False, default=ImagingStatus.COMPLETED)
    accession_number = Column(String(100), nullable=True)
    facility = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="imaging_studies")


class ClinicalDocument(Base):
    """Clinical document model - tracks uploaded clinical documents."""
    __tablename__ = "clinical_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    visit_id = Column(String(36), ForeignKey("visits.id"), nullable=True)

    title = Column(String(255), nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=True)  # Path to blob storage

    uploaded_by = Column(String(200), nullable=False)
    upload_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="documents")


class CarePlan(Base):
    """Care plan model - tracks patient care plans."""
    __tablename__ = "care_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)

    title = Column(String(255), nullable=False)
    diagnosis = Column(String(255), nullable=True)
    created_by = Column(String(200), nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="care_plans")
    goals = relationship("CareGoal", back_populates="care_plan", cascade="all, delete-orphan")
    instructions = relationship("FollowUpInstruction", back_populates="care_plan", cascade="all, delete-orphan")


class CareGoal(Base):
    """Care goal model - tracks goals within a care plan."""
    __tablename__ = "care_goals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    care_plan_id = Column(String(36), ForeignKey("care_plans.id"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    target_date = Column(DateTime, nullable=True)
    status = Column(SQLEnum(CareGoalStatus), nullable=False, default=CareGoalStatus.NOT_STARTED)
    progress_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    care_plan = relationship("CarePlan", back_populates="goals")


class FollowUpInstruction(Base):
    """Follow-up instruction model - tracks instructions within a care plan."""
    __tablename__ = "followup_instructions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    care_plan_id = Column(String(36), ForeignKey("care_plans.id"), nullable=False)

    instruction = Column(Text, nullable=False)
    category = Column(SQLEnum(InstructionCategory), nullable=False)
    priority = Column(SQLEnum(InstructionPriority), nullable=False, default=InstructionPriority.MEDIUM)
    frequency = Column(String(100), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    care_plan = relationship("CarePlan", back_populates="instructions")
