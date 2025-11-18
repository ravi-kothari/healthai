"""
Unified PreVisit + Appoint-Ready schemas for patient-facing data.

These schemas provide a "firewall" layer that transforms clinical data into
patient-friendly language, hiding sensitive clinical metrics and risk scores.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DiscussionTopic(BaseModel):
    """Patient-friendly topic to discuss with provider."""

    id: str = Field(..., description="Topic identifier")
    text: str = Field(..., description="Patient-friendly description")
    priority: str = Field(..., description="Priority level (high/medium/low)")
    icon: Optional[str] = Field(None, description="Icon name for UI")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "cg-bp",
                "text": "Discussing your blood pressure management",
                "priority": "high",
                "icon": "heart"
            }
        }


class MedicationToConfirm(BaseModel):
    """Medication for patient to confirm."""

    id: str = Field(..., description="Medication identifier")
    name: str = Field(..., description="Medication name and dosage")
    instructions: Optional[str] = Field(None, description="Simple instructions")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "med-1",
                "name": "Lisinopril 10mg",
                "instructions": "Once daily"
            }
        }


class AppointmentPrepItem(BaseModel):
    """Appointment preparation checklist item."""

    id: str = Field(..., description="Item identifier")
    category: str = Field(..., description="Category (screening, vaccination, document)")
    text: str = Field(..., description="What patient needs to do")
    completed: bool = Field(default=False, description="Whether item is completed")
    due_date: Optional[str] = Field(None, description="When this should be done")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "prep-1",
                "category": "screening",
                "text": "Schedule annual diabetic eye exam",
                "completed": False,
                "due_date": "2025-12-01"
            }
        }


class AllergyInfo(BaseModel):
    """Patient allergy information."""

    allergen: str = Field(..., description="What patient is allergic to")
    severity: str = Field(..., description="Severity (mild/moderate/severe)")

    class Config:
        json_schema_extra = {
            "example": {
                "allergen": "Penicillin",
                "severity": "severe"
            }
        }


class PatientBasicInfo(BaseModel):
    """Basic patient information for display."""

    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    age: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1980-01-15",
                "age": 45
            }
        }


class PatientSymptomSummary(BaseModel):
    """Summary of patient's submitted symptoms."""

    chief_complaint: str = Field(..., description="Main reason for visit")
    urgency_message: str = Field(..., description="Patient-friendly urgency message")
    next_steps: List[str] = Field(..., description="What to do before appointment")

    class Config:
        json_schema_extra = {
            "example": {
                "chief_complaint": "Headache and fever",
                "urgency_message": "Your appointment is important. Please arrive 15 minutes early.",
                "next_steps": [
                    "Bring a list of current medications",
                    "Note when your symptoms started",
                    "Write down any questions you have"
                ]
            }
        }


class PatientSummaryResponse(BaseModel):
    """
    Patient-facing appointment summary.

    This is the "firewall" response that shows only patient-appropriate information,
    hiding clinical risk scores, detailed triage levels, and provider-specific metrics.
    """

    patient_id: str
    generated_at: str
    appointment_date: Optional[str] = Field(None, description="Upcoming appointment date")

    # Patient basic info
    patient_info: PatientBasicInfo

    # Symptom analysis (transformed from PreVisit.ai)
    symptoms: Optional[PatientSymptomSummary] = None

    # Topics to discuss (transformed from risk assessment + care gaps)
    topics_to_discuss: List[DiscussionTopic] = Field(
        default=[],
        description="Important topics your provider wants to discuss"
    )

    # Medications to confirm
    medications_to_confirm: List[MedicationToConfirm] = Field(
        default=[],
        description="Please confirm you're still taking these medications"
    )

    # Allergies (always show for safety)
    allergies: List[AllergyInfo] = Field(
        default=[],
        description="Your recorded allergies"
    )

    # Appointment preparation checklist
    appointment_prep: List[AppointmentPrepItem] = Field(
        default=[],
        description="Things to complete before your appointment"
    )

    # General message from care team
    message_from_team: Optional[str] = Field(
        None,
        description="Personalized message from your care team"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
                "generated_at": "2025-11-05T10:30:00Z",
                "appointment_date": "2025-11-10T14:00:00Z",
                "patient_info": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "age": 45
                },
                "symptoms": {
                    "chief_complaint": "Headache and fever",
                    "urgency_message": "Your appointment is scheduled. Please arrive 15 minutes early.",
                    "next_steps": [
                        "Bring your current medications",
                        "Note when symptoms started"
                    ]
                },
                "topics_to_discuss": [
                    {
                        "id": "topic-bp",
                        "text": "Discussing your blood pressure management",
                        "priority": "high",
                        "icon": "heart"
                    },
                    {
                        "id": "topic-diabetes",
                        "text": "Reviewing your diabetes care plan",
                        "priority": "high",
                        "icon": "clipboard"
                    }
                ],
                "medications_to_confirm": [
                    {
                        "id": "med-1",
                        "name": "Metformin 500mg",
                        "instructions": "Twice daily with meals"
                    },
                    {
                        "id": "med-2",
                        "name": "Lisinopril 10mg",
                        "instructions": "Once daily"
                    }
                ],
                "allergies": [
                    {
                        "allergen": "Penicillin",
                        "severity": "severe"
                    }
                ],
                "appointment_prep": [
                    {
                        "id": "prep-1",
                        "category": "screening",
                        "text": "Schedule your annual diabetic eye exam",
                        "completed": False,
                        "due_date": "2025-12-01"
                    },
                    {
                        "id": "prep-2",
                        "category": "vaccination",
                        "text": "Get your flu shot before winter",
                        "completed": False
                    }
                ],
                "message_from_team": "We look forward to seeing you! Our team has reviewed your recent symptoms and medical history to make your visit as efficient as possible."
            }
        }
