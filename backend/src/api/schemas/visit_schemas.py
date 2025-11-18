"""
Pydantic schemas for Visit and Transcription endpoints.
"""

from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.api.models.visit import VisitStatus, VisitType, TranscriptionStatus


# ==================== Visit Schemas ====================

class VisitCreate(BaseModel):
    """Schema for creating a visit."""

    patient_id: UUID4
    provider_id: UUID4
    visit_type: VisitType
    chief_complaint: Optional[str] = None
    reason_for_visit: Optional[str] = None
    scheduled_start: Optional[datetime] = None


class VisitUpdate(BaseModel):
    """Schema for updating visit notes."""

    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None


class VisitEnd(BaseModel):
    """Schema for ending a visit with SOAP notes."""

    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    vitals: Optional[Dict[str, Any]] = None
    diagnoses: Optional[List[Dict[str, Any]]] = None
    medications: Optional[List[Dict[str, Any]]] = None


class VisitResponse(BaseModel):
    """Schema for visit response."""

    id: UUID4
    patient_id: UUID4
    provider_id: UUID4
    visit_type: VisitType
    status: VisitStatus

    # Timing
    scheduled_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    duration_minutes: Optional[int] = None

    # Clinical
    chief_complaint: Optional[str] = None
    reason_for_visit: Optional[str] = None

    # SOAP Notes
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None

    # Additional data
    vitals: Optional[Dict[str, Any]] = None
    diagnoses: Optional[List[Dict[str, Any]]] = None
    medications: Optional[List[Dict[str, Any]]] = None

    # AI-generated
    ai_summary: Optional[str] = None
    ai_recommendations: Optional[List[str]] = None

    # FHIR
    fhir_encounter_id: Optional[str] = None

    # Metadata
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Transcription Schemas ====================

class TranscriptionCreate(BaseModel):
    """Schema for creating a transcription."""

    visit_id: UUID4
    language: str = Field(default="en-US", description="Language code (e.g., 'en-US')")


class TranscriptionResponse(BaseModel):
    """Schema for transcription response."""

    id: UUID4
    visit_id: UUID4
    audio_file_url: Optional[str] = None
    audio_duration_seconds: Optional[int] = None
    audio_format: Optional[str] = None
    transcription_text: Optional[str] = None
    language: str
    confidence_score: Optional[int] = None
    status: TranscriptionStatus
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Combined Schemas ====================

class VisitWithTranscripts(VisitResponse):
    """Visit response with transcripts included."""

    transcripts: List[TranscriptionResponse] = []

    class Config:
        from_attributes = True
