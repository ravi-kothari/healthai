"""
Pydantic schemas for clinical data requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================================================
# MEDICATION SCHEMAS
# ============================================================================

class MedicationCreate(BaseModel):
    """Schema for creating a medication."""
    patient_id: str
    name: str = Field(..., min_length=1, max_length=200)
    dosage: str = Field(..., min_length=1, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=100)
    route: str = Field(..., min_length=1, max_length=50)
    start_date: datetime
    end_date: Optional[datetime] = None
    prescriber: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    status: str = "active"


class MedicationUpdate(BaseModel):
    """Schema for updating a medication."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    dosage: Optional[str] = Field(None, min_length=1, max_length=100)
    frequency: Optional[str] = Field(None, min_length=1, max_length=100)
    route: Optional[str] = Field(None, min_length=1, max_length=50)
    end_date: Optional[datetime] = None
    prescriber: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    status: Optional[str] = None


class MedicationResponse(BaseModel):
    """Schema for medication response."""
    id: str
    patient_id: str
    name: str
    dosage: str
    frequency: str
    route: str
    start_date: datetime
    end_date: Optional[datetime]
    prescriber: Optional[str]
    notes: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# LAB RESULT SCHEMAS
# ============================================================================

class LabResultCreate(BaseModel):
    """Schema for creating a lab result."""
    patient_id: str
    visit_id: Optional[str] = None
    test_name: str = Field(..., min_length=1, max_length=200)
    result_value: str = Field(..., min_length=1, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    reference_range: Optional[str] = Field(None, max_length=100)
    status: str = "normal"
    date_collected: datetime
    date_resulted: datetime
    ordered_by: Optional[str] = Field(None, max_length=200)
    lab_name: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class LabResultResponse(BaseModel):
    """Schema for lab result response."""
    id: str
    patient_id: str
    visit_id: Optional[str]
    test_name: str
    result_value: str
    unit: Optional[str]
    reference_range: Optional[str]
    status: str
    date_collected: datetime
    date_resulted: datetime
    ordered_by: Optional[str]
    lab_name: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LabOrderCreate(BaseModel):
    """Schema for creating a lab order."""
    patient_id: str
    visit_id: Optional[str] = None
    test_name: str = Field(..., min_length=1, max_length=200)
    ordered_date: datetime
    status: str = "pending"
    priority: str = "routine"


class LabOrderResponse(BaseModel):
    """Schema for lab order response."""
    id: str
    patient_id: str
    visit_id: Optional[str]
    test_name: str
    ordered_date: datetime
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ALLERGY SCHEMAS
# ============================================================================

class AllergyCreate(BaseModel):
    """Schema for creating an allergy."""
    patient_id: str
    allergen: str = Field(..., min_length=1, max_length=200)
    reaction: str = Field(..., min_length=1)
    severity: str
    onset_date: Optional[datetime] = None
    notes: Optional[str] = None
    status: str = "active"


class AllergyUpdate(BaseModel):
    """Schema for updating an allergy."""
    allergen: Optional[str] = Field(None, min_length=1, max_length=200)
    reaction: Optional[str] = None
    severity: Optional[str] = None
    onset_date: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class AllergyResponse(BaseModel):
    """Schema for allergy response."""
    id: str
    patient_id: str
    allergen: str
    reaction: str
    severity: str
    onset_date: Optional[datetime]
    notes: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CONDITION SCHEMAS
# ============================================================================

class ConditionCreate(BaseModel):
    """Schema for creating a condition."""
    patient_id: str
    name: str = Field(..., min_length=1, max_length=200)
    icd10_code: Optional[str] = Field(None, max_length=20)
    status: str = "active"
    onset_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    notes: Optional[str] = None


class ConditionUpdate(BaseModel):
    """Schema for updating a condition."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    icd10_code: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = None
    onset_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    notes: Optional[str] = None


class ConditionResponse(BaseModel):
    """Schema for condition response."""
    id: str
    patient_id: str
    name: str
    icd10_code: Optional[str]
    status: str
    onset_date: Optional[datetime]
    resolved_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# IMAGING STUDY SCHEMAS
# ============================================================================

class ImagingStudyCreate(BaseModel):
    """Schema for creating an imaging study."""
    patient_id: str
    visit_id: Optional[str] = None
    study_type: str = Field(..., min_length=1, max_length=200)
    body_part: str = Field(..., min_length=1, max_length=100)
    modality: str
    study_date: datetime
    ordering_provider: Optional[str] = Field(None, max_length=200)
    radiologist: Optional[str] = Field(None, max_length=200)
    findings: Optional[str] = None
    impression: Optional[str] = None
    status: str = "completed"
    accession_number: Optional[str] = Field(None, max_length=100)
    facility: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class ImagingStudyUpdate(BaseModel):
    """Schema for updating an imaging study."""
    radiologist: Optional[str] = Field(None, max_length=200)
    findings: Optional[str] = None
    impression: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ImagingStudyResponse(BaseModel):
    """Schema for imaging study response."""
    id: str
    patient_id: str
    visit_id: Optional[str]
    study_type: str
    body_part: str
    modality: str
    study_date: datetime
    ordering_provider: Optional[str]
    radiologist: Optional[str]
    findings: Optional[str]
    impression: Optional[str]
    status: str
    accession_number: Optional[str]
    facility: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CLINICAL DOCUMENT SCHEMAS
# ============================================================================

class ClinicalDocumentCreate(BaseModel):
    """Schema for creating a clinical document."""
    patient_id: str
    visit_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    document_type: str
    file_name: str = Field(..., min_length=1, max_length=255)
    file_size: int
    file_type: str = Field(..., min_length=1, max_length=100)
    file_path: Optional[str] = Field(None, max_length=500)
    uploaded_by: str = Field(..., min_length=1, max_length=200)
    notes: Optional[str] = None


class ClinicalDocumentResponse(BaseModel):
    """Schema for clinical document response."""
    id: str
    patient_id: str
    visit_id: Optional[str]
    title: str
    document_type: str
    file_name: str
    file_size: int
    file_type: str
    file_path: Optional[str]
    uploaded_by: str
    upload_date: datetime
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CARE PLAN SCHEMAS
# ============================================================================

class CareGoalCreate(BaseModel):
    """Schema for creating a care goal."""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    target_date: Optional[datetime] = None
    status: str = "not_started"
    progress_notes: Optional[str] = None


class CareGoalUpdate(BaseModel):
    """Schema for updating a care goal."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    status: Optional[str] = None
    progress_notes: Optional[str] = None


class CareGoalResponse(BaseModel):
    """Schema for care goal response."""
    id: str
    care_plan_id: str
    title: str
    description: str
    target_date: Optional[datetime]
    status: str
    progress_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FollowUpInstructionCreate(BaseModel):
    """Schema for creating a follow-up instruction."""
    instruction: str = Field(..., min_length=1)
    category: str
    priority: str = "medium"
    frequency: Optional[str] = Field(None, max_length=100)


class FollowUpInstructionResponse(BaseModel):
    """Schema for follow-up instruction response."""
    id: str
    care_plan_id: str
    instruction: str
    category: str
    priority: str
    frequency: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CarePlanCreate(BaseModel):
    """Schema for creating a care plan."""
    patient_id: str
    title: str = Field(..., min_length=1, max_length=255)
    diagnosis: Optional[str] = Field(None, max_length=255)
    created_by: str = Field(..., min_length=1, max_length=200)
    goals: Optional[List[CareGoalCreate]] = []
    instructions: Optional[List[FollowUpInstructionCreate]] = []


class CarePlanResponse(BaseModel):
    """Schema for care plan response."""
    id: str
    patient_id: str
    title: str
    diagnosis: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    goals: List[CareGoalResponse]
    instructions: List[FollowUpInstructionResponse]

    class Config:
        from_attributes = True
