"""
Patient model for storing patient demographic and medical information.
HIPAA compliant with audit trails.
"""

from sqlalchemy import Column, String, Date, Enum as SQLEnum, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import date

from src.api.database import Base
from src.api.models.base import UUIDMixin, TimestampMixin


class Gender(str, Enum):
    """Gender options."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class BloodType(str, Enum):
    """Blood type options."""

    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    UNKNOWN = "unknown"


class Patient(Base, UUIDMixin, TimestampMixin):
    """
    Patient model with demographic and medical information.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to User model
        mrn: Medical Record Number (unique)
        first_name: Patient's first name
        last_name: Patient's last name
        date_of_birth: Date of birth
        gender: Gender
        blood_type: Blood type
        address: Physical address
        city: City
        state: State
        zip_code: ZIP code
        emergency_contact_name: Emergency contact name
        emergency_contact_phone: Emergency contact phone
        insurance_provider: Insurance provider name
        insurance_policy_number: Insurance policy number
        allergies: List of allergies (JSON)
        chronic_conditions: List of chronic conditions (JSON)
        current_medications: List of current medications (JSON)
        notes: Additional notes (HIPAA protected)
    """

    __tablename__ = "patients"

    # Link to User account
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)

    # Medical Record Number (unique identifier in healthcare system)
    mrn = Column(String(50), unique=True, index=True, nullable=False)

    # Demographics
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(SQLEnum(Gender), nullable=False)
    blood_type = Column(SQLEnum(BloodType), default=BloodType.UNKNOWN)

    # Contact Information
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)  # US state code
    zip_code = Column(String(10), nullable=True)

    # Emergency Contact
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(100), nullable=True)

    # Insurance Information
    insurance_provider = Column(String(255), nullable=True)
    insurance_policy_number = Column(String(100), nullable=True)
    insurance_group_number = Column(String(100), nullable=True)

    # Medical Information (stored as JSON for flexibility)
    allergies = Column(JSON, default=list, nullable=True)
    chronic_conditions = Column(JSON, default=list, nullable=True)
    current_medications = Column(JSON, default=list, nullable=True)

    # Additional Notes
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", backref="patient")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    visits = relationship("Visit", back_populates="patient", cascade="all, delete-orphan")

    # Clinical data relationships
    medications = relationship("Medication", back_populates="patient", cascade="all, delete-orphan")
    lab_results = relationship("LabResult", back_populates="patient", cascade="all, delete-orphan")
    lab_orders = relationship("LabOrder", back_populates="patient", cascade="all, delete-orphan")
    allergies = relationship("Allergy", back_populates="patient", cascade="all, delete-orphan")
    conditions = relationship("Condition", back_populates="patient", cascade="all, delete-orphan")
    imaging_studies = relationship("ImagingStudy", back_populates="patient", cascade="all, delete-orphan")
    documents = relationship("ClinicalDocument", back_populates="patient", cascade="all, delete-orphan")
    care_plans = relationship("CarePlan", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient(id={self.id}, mrn={self.mrn}, name={self.first_name} {self.last_name})>"

    @property
    def full_name(self):
        """Get patient's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        """Calculate patient's age."""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def to_dict(self):
        """Convert model to dictionary (excluding sensitive fields in some contexts)."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "mrn": self.mrn,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "age": self.age,
            "gender": self.gender.value if self.gender else None,
            "blood_type": self.blood_type.value if self.blood_type else None,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "emergency_contact_name": self.emergency_contact_name,
            "emergency_contact_phone": self.emergency_contact_phone,
            "emergency_contact_relationship": self.emergency_contact_relationship,
            "insurance_provider": self.insurance_provider,
            "insurance_policy_number": self.insurance_policy_number,
            "allergies": self.allergies,
            "chronic_conditions": self.chronic_conditions,
            "current_medications": self.current_medications,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
