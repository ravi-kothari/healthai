"""
Pydantic schemas for PreVisit.ai requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum


class SymptomSeverity(str, Enum):
    """Symptom severity levels."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class UrgencyLevel(str, Enum):
    """Urgency/triage levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class SymptomInput(BaseModel):
    """Individual symptom input."""

    name: str = Field(..., min_length=1, max_length=200, description="Symptom name")
    severity: SymptomSeverity = Field(..., description="Symptom severity")
    duration: str = Field(..., min_length=1, max_length=100, description="How long symptom has lasted")
    description: Optional[str] = Field(None, max_length=1000, description="Additional details")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Headache",
                "severity": "moderate",
                "duration": "2 days",
                "description": "Throbbing pain in temples, worse in the morning"
            }
        }


class SymptomAnalysisRequest(BaseModel):
    """Request for symptom analysis."""

    patient_id: Optional[str] = Field(None, description="Patient ID for context")
    symptoms: List[SymptomInput] = Field(..., min_items=1, description="List of symptoms")
    vital_signs: Optional[Dict[str, Any]] = Field(None, description="Optional vital signs (temp, BP, etc.)")
    medical_history_notes: Optional[str] = Field(None, max_length=2000, description="Relevant medical history")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
                "symptoms": [
                    {
                        "name": "Headache",
                        "severity": "moderate",
                        "duration": "2 days",
                        "description": "Throbbing pain in temples"
                    },
                    {
                        "name": "Fever",
                        "severity": "mild",
                        "duration": "1 day",
                        "description": "Low-grade fever, 100.5°F"
                    }
                ],
                "vital_signs": {
                    "temperature_f": 100.5,
                    "blood_pressure": "120/80",
                    "heart_rate": 75
                }
            }
        }


class SymptomAnalysisResponse(BaseModel):
    """Response from symptom analysis."""

    urgency: UrgencyLevel = Field(..., description="Overall urgency level")
    severity: str = Field(..., description="Overall severity assessment")
    triage_level: int = Field(..., ge=1, le=5, description="Triage level (1=emergency, 5=routine)")
    chief_complaint: str = Field(..., description="Primary complaint summary")
    summary: str = Field(..., description="Analysis summary")
    possible_conditions: List[str] = Field(..., description="Possible conditions")
    recommendations: List[str] = Field(..., description="Recommended actions")
    red_flags: List[str] = Field(..., description="Warning signs to watch for")
    follow_up: str = Field(..., description="Follow-up guidance")

    class Config:
        json_schema_extra = {
            "example": {
                "urgency": "moderate",
                "severity": "moderate",
                "triage_level": 3,
                "chief_complaint": "Headache and fever",
                "summary": "Patient presents with moderate headache and mild fever...",
                "possible_conditions": ["Viral infection", "Influenza", "Tension headache"],
                "recommendations": ["Rest", "Hydrate", "Monitor temperature"],
                "red_flags": ["Temperature above 103°F", "Severe headache with neck stiffness"],
                "follow_up": "Schedule appointment if symptoms persist beyond 3 days"
            }
        }


class QuestionType(str, Enum):
    """Question types for questionnaires."""
    TEXT = "text"
    SELECT = "select"
    MULTISELECT = "multiselect"
    SCALE = "scale"
    YES_NO = "yes_no"
    DATE = "date"


class QuestionnaireQuestion(BaseModel):
    """Individual questionnaire question."""

    id: str = Field(..., description="Question identifier")
    type: QuestionType = Field(..., description="Question type")
    question: str = Field(..., description="Question text")
    options: Optional[List[Any]] = Field(None, description="Options for select/multiselect")
    required: bool = Field(True, description="Whether question is required")
    conditional_on: Optional[str] = Field(None, description="ID of question this depends on")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "q1",
                "type": "scale",
                "question": "On a scale of 1-10, rate your pain level",
                "options": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "required": True
            }
        }


class QuestionnaireGenerationRequest(BaseModel):
    """Request to generate a questionnaire."""

    patient_id: Optional[str] = Field(None, description="Patient ID")
    chief_complaint: str = Field(..., min_length=1, max_length=500, description="Main complaint")
    symptoms: Optional[List[str]] = Field(None, description="Known symptoms")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
                "chief_complaint": "Headache and fever",
                "symptoms": ["headache", "fever", "body aches"]
            }
        }


class QuestionnaireResponse(BaseModel):
    """Generated questionnaire response."""

    questions: List[QuestionnaireQuestion] = Field(..., description="List of questions")
    estimated_time_minutes: int = Field(..., description="Estimated completion time")

    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    {
                        "id": "q1",
                        "type": "scale",
                        "question": "Rate your headache severity (1-10)",
                        "options": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        "required": True
                    }
                ],
                "estimated_time_minutes": 5
            }
        }


class TriageAssessmentRequest(BaseModel):
    """Request for triage assessment."""

    patient_id: Optional[str] = Field(None, description="Patient ID")
    symptoms: List[SymptomInput] = Field(..., min_items=1)
    vital_signs: Optional[Dict[str, Any]] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    existing_conditions: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
                "symptoms": [
                    {
                        "name": "Chest pain",
                        "severity": "severe",
                        "duration": "30 minutes",
                        "description": "Sharp pain, radiating to left arm"
                    }
                ],
                "vital_signs": {
                    "blood_pressure": "160/100",
                    "heart_rate": 110
                },
                "age": 55,
                "existing_conditions": ["Hypertension", "Diabetes"]
            }
        }


class TriageAssessmentResponse(BaseModel):
    """Triage assessment response."""

    triage_level: int = Field(..., ge=1, le=5, description="1=emergency, 5=routine")
    urgency: UrgencyLevel = Field(..., description="Urgency level")
    recommended_action: str = Field(..., description="Recommended immediate action")
    time_to_see_provider: str = Field(..., description="Recommended timeframe")
    rationale: str = Field(..., description="Reasoning for triage decision")
    emergency_flags: List[str] = Field(..., description="Emergency indicators found")

    class Config:
        json_schema_extra = {
            "example": {
                "triage_level": 1,
                "urgency": "emergency",
                "recommended_action": "Call 911 immediately or go to nearest emergency room",
                "time_to_see_provider": "Immediate",
                "rationale": "Severe chest pain with radiation suggests possible cardiac event",
                "emergency_flags": ["Chest pain with arm radiation", "Elevated blood pressure", "History of cardiovascular disease"]
            }
        }
