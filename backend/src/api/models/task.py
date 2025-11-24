"""
Provider Task Management Models.
Tracks follow-ups, pending tests, and reminders for healthcare providers.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.api.database import Base


class TaskPriority(str, enum.Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    """Task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskCategory(str, enum.Enum):
    """Task categories."""
    FOLLOW_UP = "follow_up"           # Schedule follow-up appointment
    LAB_ORDER = "lab_order"           # Order lab tests
    IMAGING_ORDER = "imaging_order"   # Order imaging studies
    REFERRAL = "referral"             # Refer to specialist
    MEDICATION = "medication"         # Medication-related task
    PHONE_CALL = "phone_call"         # Call patient
    REVIEW = "review"                 # Review results/records
    DOCUMENTATION = "documentation"   # Complete documentation
    OTHER = "other"                   # Other tasks


class ProviderTask(Base):
    """
    Provider task model for tracking clinical follow-ups and reminders.

    Tasks can be created from:
    - Quick notes during visits (using shortcuts)
    - AI assistant suggestions
    - Manual entry
    """
    __tablename__ = "provider_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    # Task details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(SQLEnum(TaskCategory), nullable=False, default=TaskCategory.OTHER)
    priority = Column(SQLEnum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING)

    # Assignment
    provider_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Patient context
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=True, index=True)
    visit_id = Column(String(36), ForeignKey("visits.id"), nullable=True, index=True)
    appointment_id = Column(String(36), ForeignKey("appointments.id"), nullable=True, index=True)

    # Timing
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Additional metadata
    tags = Column(JSON, nullable=True)  # ["urgent", "call-back", "test-results"]
    task_metadata = Column("metadata", JSON, nullable=True)  # Store shortcut info, AI suggestion source, etc.

    # Auto-generated from shortcuts
    created_from_shortcut = Column(Boolean, default=False)
    shortcut_code = Column(String(50), nullable=True)  # e.g., "!followup", "!lab"

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    provider = relationship("User", foreign_keys=[provider_id])
    patient = relationship("Patient", foreign_keys=[patient_id])
    visit = relationship("Visit", foreign_keys=[visit_id])
    appointment = relationship("Appointment", foreign_keys=[appointment_id])

    def __repr__(self):
        return f"<ProviderTask {self.id} - {self.title} ({self.status})>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value if self.category else None,
            "priority": self.priority.value if self.priority else None,
            "status": self.status.value if self.status else None,
            "provider_id": self.provider_id,
            "patient_id": self.patient_id,
            "visit_id": self.visit_id,
            "appointment_id": self.appointment_id,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tags": self.tags,
            "created_from_shortcut": self.created_from_shortcut,
            "shortcut_code": self.shortcut_code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
