"""
Pydantic schemas for patient requests and responses.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from src.api.models.patient import Gender, BloodType


class PatientCreateRequest(BaseModel):
    """Schema for creating a new patient."""

    user_id: str = Field(..., description="User ID linked to this patient")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    date_of_birth: date = Field(..., description="Date of birth")
    gender: Gender = Field(..., description="Gender")
    blood_type: Optional[BloodType] = Field(BloodType.UNKNOWN, description="Blood type")

    # Contact Information
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)

    # Emergency Contact
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=100)

    # Insurance
    insurance_provider: Optional[str] = Field(None, max_length=255)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_group_number: Optional[str] = Field(None, max_length=100)

    # Medical Information
    allergies: Optional[List[str]] = Field(default_factory=list)
    chronic_conditions: Optional[List[str]] = Field(default_factory=list)
    current_medications: Optional[List[str]] = Field(default_factory=list)
    notes: Optional[str] = None

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v):
        """Validate date of birth is not in the future."""
        if v > date.today():
            raise ValueError("Date of birth cannot be in the future")

        # Calculate age
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))

        if age > 150:
            raise ValueError("Invalid date of birth: age exceeds 150 years")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "2a977f77-bd03-4550-a62c-c46ac2edab0b",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1985-06-15",
                "gender": "male",
                "blood_type": "A+",
                "address": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94102",
                "emergency_contact_name": "Jane Doe",
                "emergency_contact_phone": "+1-555-0124",
                "emergency_contact_relationship": "Spouse",
                "insurance_provider": "Blue Cross",
                "insurance_policy_number": "BC123456",
                "allergies": ["Penicillin", "Peanuts"],
                "chronic_conditions": ["Hypertension"],
                "current_medications": ["Lisinopril 10mg"]
            }
        }


class PatientUpdateRequest(BaseModel):
    """Schema for updating a patient (all fields optional)."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    blood_type: Optional[BloodType] = None

    # Contact Information
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)

    # Emergency Contact
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=100)

    # Insurance
    insurance_provider: Optional[str] = Field(None, max_length=255)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_group_number: Optional[str] = Field(None, max_length=100)

    # Medical Information
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "address": "456 New St",
                "city": "Los Angeles",
                "current_medications": ["Lisinopril 20mg", "Aspirin 81mg"]
            }
        }


class PatientResponse(BaseModel):
    """Schema for patient response."""

    id: str
    user_id: str
    mrn: str
    first_name: str
    last_name: str
    full_name: str
    date_of_birth: date
    age: Optional[int]
    gender: str
    blood_type: str

    # Contact Information
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]

    # Emergency Contact
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    emergency_contact_relationship: Optional[str]

    # Insurance
    insurance_provider: Optional[str]
    insurance_policy_number: Optional[str]

    # Medical Information
    allergies: Optional[List[str]]
    chronic_conditions: Optional[List[str]]
    current_medications: Optional[List[str]]

    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    """Schema for paginated patient list response."""

    items: List[PatientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5
            }
        }
