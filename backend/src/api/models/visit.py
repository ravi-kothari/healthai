"""
Visit and Transcription Models.
Tracks clinical visits and audio transcriptions.
"""

from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.api.database import Base


class VisitStatus(str, enum.Enum):
    """Visit status enumeration."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class VisitType(str, enum.Enum):
    """Visit type enumeration."""
    INITIAL = "initial"
    FOLLOW_UP = "follow_up"
    URGENT = "urgent"
    ROUTINE = "routine"
    TELEHEALTH = "telehealth"
    IN_PERSON = "in_person"


class TranscriptionStatus(str, enum.Enum):
    """Transcription status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Visit(Base):
    """Visit model representing a clinical encounter."""

    __tablename__ = "visits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    # Patient and Provider
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    provider_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Visit Details
    visit_type = Column(SQLEnum(VisitType), nullable=False, default=VisitType.ROUTINE)
    status = Column(SQLEnum(VisitStatus), nullable=False, default=VisitStatus.SCHEDULED)

    # Timing
    scheduled_start = Column(DateTime(timezone=True), nullable=True)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)  # Calculated duration

    # Clinical Information
    chief_complaint = Column(Text, nullable=True)
    reason_for_visit = Column(Text, nullable=True)

    # Visit Notes (structured)
    subjective = Column(Text, nullable=True)  # SOAP - Subjective
    objective = Column(Text, nullable=True)   # SOAP - Objective
    assessment = Column(Text, nullable=True)  # SOAP - Assessment
    plan = Column(Text, nullable=True)        # SOAP - Plan

    # Additional structured data
    vitals = Column(JSON, nullable=True)  # Blood pressure, temp, heart rate, etc.
    diagnoses = Column(JSON, nullable=True)  # ICD-10 codes and descriptions
    medications = Column(JSON, nullable=True)  # Prescriptions
    procedures = Column(JSON, nullable=True)  # Procedures performed

    # AI-generated content
    ai_summary = Column(Text, nullable=True)
    ai_recommendations = Column(JSON, nullable=True)

    # FHIR Integration
    fhir_encounter_id = Column(String(255), nullable=True)  # Reference to FHIR Encounter

    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="visits")
    provider = relationship("User", back_populates="provider_visits")
    transcripts = relationship("Transcript", back_populates="visit", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Visit {self.id} - Patient: {self.patient_id}, Status: {self.status}>"


class Transcript(Base):
    """Transcript model for audio transcriptions during visits."""

    __tablename__ = "transcripts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    # Visit relationship
    visit_id = Column(String(36), ForeignKey("visits.id"), nullable=False, index=True)

    # Audio file information
    audio_file_url = Column(String(500), nullable=True)  # Azure Blob Storage URL
    audio_duration_seconds = Column(Integer, nullable=True)
    audio_format = Column(String(50), nullable=True)  # e.g., "wav", "mp3"

    # Transcription
    transcription_text = Column(Text, nullable=True)
    language = Column(String(10), default="en-US", nullable=False)
    confidence_score = Column(Integer, nullable=True)  # 0-100

    # Status and processing
    status = Column(SQLEnum(TranscriptionStatus), nullable=False, default=TranscriptionStatus.PENDING)
    error_message = Column(Text, nullable=True)

    # Timestamps for processing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    visit = relationship("Visit", back_populates="transcripts")

    def __repr__(self):
        return f"<Transcript {self.id} - Visit: {self.visit_id}, Status: {self.status}>"
