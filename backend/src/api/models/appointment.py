"""
Appointment model for scheduling and tracking patient visits.
"""

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Text, Integer, JSON
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime

from src.api.database import Base
from src.api.models.base import UUIDMixin, TimestampMixin


class AppointmentStatus(str, Enum):
    """Appointment status options."""

    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class AppointmentType(str, Enum):
    """Appointment type options."""

    INITIAL_CONSULTATION = "initial_consultation"
    FOLLOW_UP = "follow_up"
    ANNUAL_CHECKUP = "annual_checkup"
    URGENT_CARE = "urgent_care"
    TELEMEDICINE = "telemedicine"
    PROCEDURE = "procedure"
    LAB_WORK = "lab_work"
    VACCINATION = "vaccination"
    OTHER = "other"


class Appointment(Base, UUIDMixin, TimestampMixin):
    """
    Appointment model for patient visits.

    Attributes:
        id: Unique identifier (UUID)
        patient_id: Foreign key to Patient
        provider_id: Foreign key to User (doctor/nurse)
        appointment_type: Type of appointment
        status: Current status
        scheduled_start: Scheduled start time
        scheduled_end: Scheduled end time
        actual_start: Actual start time
        actual_end: Actual end time
        chief_complaint: Patient's main concern
        notes: Appointment notes
        previsit_completed: Whether PreVisit.ai was completed
        previsit_data: PreVisit.ai analysis data (JSON)
        soap_note: SOAP note (if generated)
        transcription_url: URL to audio transcription
        duration_minutes: Scheduled duration
    """

    __tablename__ = "appointments"

    # Relationships
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    provider_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Appointment Details
    appointment_type = Column(SQLEnum(AppointmentType), nullable=False)
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)

    # Scheduling
    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=False, default=30)

    # Clinical Information
    chief_complaint = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # PreVisit.ai Data
    previsit_completed = Column(String(1), default="N", nullable=False)  # Y/N
    previsit_data = Column(JSON, nullable=True)  # Stores symptom analysis, triage results

    # Appoint-Ready Data
    context_data = Column(JSON, nullable=True)  # Patient context from FHIR
    care_gaps = Column(JSON, nullable=True)  # Detected care gaps
    risk_assessment = Column(JSON, nullable=True)  # Risk stratification

    # Clinical Documentation
    soap_note = Column(Text, nullable=True)
    transcription_url = Column(String(500), nullable=True)
    audio_file_url = Column(String(500), nullable=True)

    # Cancellation/Rescheduling
    cancellation_reason = Column(Text, nullable=True)
    rescheduled_from = Column(String(36), ForeignKey("appointments.id"), nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    provider = relationship("User", foreign_keys=[provider_id])
    careprep_response = relationship("CarePrepResponse", back_populates="appointment", uselist=False)

    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, status={self.status})>"

    @property
    def is_past(self):
        """Check if appointment is in the past."""
        return self.scheduled_start < datetime.now(self.scheduled_start.tzinfo)

    @property
    def is_today(self):
        """Check if appointment is today."""
        now = datetime.now(self.scheduled_start.tzinfo)
        return self.scheduled_start.date() == now.date()

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "provider_id": self.provider_id,
            "appointment_type": self.appointment_type.value if self.appointment_type else None,
            "status": self.status.value if self.status else None,
            "scheduled_start": self.scheduled_start.isoformat() if self.scheduled_start else None,
            "scheduled_end": self.scheduled_end.isoformat() if self.scheduled_end else None,
            "actual_start": self.actual_start.isoformat() if self.actual_start else None,
            "actual_end": self.actual_end.isoformat() if self.actual_end else None,
            "duration_minutes": self.duration_minutes,
            "chief_complaint": self.chief_complaint,
            "notes": self.notes,
            "previsit_completed": self.previsit_completed == "Y",
            "previsit_data": self.previsit_data,
            "context_data": self.context_data,
            "care_gaps": self.care_gaps,
            "risk_assessment": self.risk_assessment,
            "soap_note": self.soap_note,
            "transcription_url": self.transcription_url,
            "audio_file_url": self.audio_file_url,
            "is_past": self.is_past,
            "is_today": self.is_today,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
