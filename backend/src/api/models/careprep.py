"""
CarePrep response models.
Stores patient responses to CarePrep checklist items.
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.api.database import Base


class CarePrepResponse(Base):
    """
    CarePrep response model.
    Stores patient responses to CarePrep checklist for an appointment.
    """
    __tablename__ = "careprep_responses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    appointment_id = Column(String, ForeignKey("appointments.id"), nullable=False)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)

    # Medical History
    medical_history_completed = Column(Boolean, default=False)
    medical_history_data = Column(JSON, nullable=True)  # Stores structured medical history
    medical_history_updated_at = Column(DateTime, nullable=True)

    # Symptom Checker
    symptom_checker_completed = Column(Boolean, default=False)
    symptom_checker_data = Column(JSON, nullable=True)  # Stores symptom analysis results
    symptom_checker_updated_at = Column(DateTime, nullable=True)

    # Overall completion
    all_tasks_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    appointment = relationship("Appointment", back_populates="careprep_response")
    patient = relationship("Patient")

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "medical_history_completed": self.medical_history_completed,
            "medical_history_data": self.medical_history_data,
            "medical_history_updated_at": self.medical_history_updated_at.isoformat() if self.medical_history_updated_at else None,
            "symptom_checker_completed": self.symptom_checker_completed,
            "symptom_checker_data": self.symptom_checker_data,
            "symptom_checker_updated_at": self.symptom_checker_updated_at.isoformat() if self.symptom_checker_updated_at else None,
            "all_tasks_completed": self.all_tasks_completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def calculate_completion(self):
        """Calculate overall completion status."""
        self.all_tasks_completed = (
            self.medical_history_completed and
            self.symptom_checker_completed
        )
        if self.all_tasks_completed and not self.completed_at:
            self.completed_at = datetime.utcnow()
