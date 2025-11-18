"""
Pydantic schemas for Appoint-Ready requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class PatientDemographics(BaseModel):
    """Patient demographic information."""

    patient_id: str
    mrn: str
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    emergency_contact: Optional[Dict[str, str]] = None


class MedicalCondition(BaseModel):
    """Medical condition/diagnosis."""

    name: str
    code: Optional[str] = None
    code_system: Optional[str] = None
    status: str
    recorded_date: Optional[str] = None
    is_active: bool


class Medication(BaseModel):
    """Medication information."""

    name: str
    code: Optional[str] = None
    status: str
    is_active: bool


class Allergy(BaseModel):
    """Allergy information."""

    allergen: str
    code: Optional[str] = None
    criticality: str
    is_high_risk: bool


class VitalSign(BaseModel):
    """Vital sign observation."""

    name: str
    code: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    date: Optional[str] = None
    status: Optional[str] = None


class MedicalHistory(BaseModel):
    """Aggregated medical history from FHIR."""

    conditions: List[MedicalCondition] = []
    medications: List[Medication] = []
    allergies: List[Allergy] = []
    recent_vitals: List[VitalSign] = []


class PreVisitData(BaseModel):
    """PreVisit.ai response data."""

    has_responses: bool
    last_response_date: Optional[str] = None
    chief_complaint: Optional[str] = None
    triage_level: Optional[int] = None
    urgency: Optional[str] = None


class ContextAlert(BaseModel):
    """Alert for provider attention."""

    type: str = Field(..., description="Alert type (allergy, previsit_triage, etc.)")
    severity: str = Field(..., description="Alert severity (low/medium/high)")
    message: str = Field(..., description="Alert message")


class ContextHighlight(BaseModel):
    """Context highlight for quick review."""

    type: str = Field(..., description="Highlight type (conditions, medications, etc.)")
    count: int = Field(..., description="Number of items")
    items: List[str] = Field(..., description="Top items to display")


class ContextSummary(BaseModel):
    """High-level summary of appointment context."""

    has_data: bool
    data_completeness: float = Field(..., description="Percentage of data sources available")
    alerts: List[ContextAlert] = []
    highlights: List[ContextHighlight] = []


class AppointmentContextResponse(BaseModel):
    """Complete appointment context for providers."""

    patient_id: str
    generated_at: str
    data_sources: List[str] = Field(..., description="Data sources used (database, fhir, previsit)")
    demographics: Optional[PatientDemographics] = None
    medical_history: Optional[MedicalHistory] = None
    previsit: Optional[PreVisitData] = None
    summary: ContextSummary

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
                "generated_at": "2025-11-02T10:30:00Z",
                "data_sources": ["database", "fhir"],
                "demographics": {
                    "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
                    "mrn": "MRN-20251102-12345",
                    "first_name": "John",
                    "last_name": "Doe",
                    "age": 45,
                    "gender": "male"
                },
                "medical_history": {
                    "conditions": [
                        {
                            "name": "Type 2 diabetes mellitus",
                            "code": "E11.9",
                            "status": "active",
                            "is_active": True
                        }
                    ],
                    "medications": [
                        {
                            "name": "Metformin 500mg",
                            "status": "active",
                            "is_active": True
                        }
                    ],
                    "allergies": [
                        {
                            "allergen": "Penicillin",
                            "criticality": "high",
                            "is_high_risk": True
                        }
                    ],
                    "recent_vitals": []
                },
                "summary": {
                    "has_data": True,
                    "data_completeness": 66.7,
                    "alerts": [
                        {
                            "type": "allergy",
                            "severity": "high",
                            "message": "HIGH-RISK ALLERGIES: Penicillin"
                        }
                    ],
                    "highlights": [
                        {
                            "type": "conditions",
                            "count": 1,
                            "items": ["Type 2 diabetes mellitus"]
                        }
                    ]
                }
            }
        }


class CareGap(BaseModel):
    """Identified care gap."""

    gap_type: str = Field(..., description="Type of gap (screening, vaccination, follow-up)")
    description: str = Field(..., description="Gap description")
    priority: str = Field(..., description="Priority level (low/medium/high)")
    due_date: Optional[str] = Field(None, description="When this is due")
    overdue: bool = Field(default=False, description="Whether gap is overdue")
    recommendation: str = Field(..., description="Recommended action")


class CareGapsResponse(BaseModel):
    """Care gaps analysis response."""

    patient_id: str
    gaps: List[CareGap]
    total_gaps: int
    high_priority_count: int
    overdue_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
                "gaps": [
                    {
                        "gap_type": "screening",
                        "description": "Annual diabetic eye exam overdue",
                        "priority": "high",
                        "due_date": "2025-10-01",
                        "overdue": True,
                        "recommendation": "Schedule ophthalmology appointment for diabetic retinopathy screening"
                    }
                ],
                "total_gaps": 1,
                "high_priority_count": 1,
                "overdue_count": 1
            }
        }


class RiskScore(BaseModel):
    """Individual risk score."""

    risk_type: str = Field(..., description="Type of risk (cardiovascular, diabetes, fall)")
    score: float = Field(..., ge=0, le=100, description="Risk score (0-100)")
    category: str = Field(..., description="Risk category (low/moderate/high/very-high)")
    factors: List[str] = Field(..., description="Contributing risk factors")
    recommendations: List[str] = Field(..., description="Risk mitigation recommendations")


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response."""

    patient_id: str
    assessed_at: str
    risk_scores: List[RiskScore]
    overall_risk_level: str = Field(..., description="Overall risk level")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
                "assessed_at": "2025-11-02T10:30:00Z",
                "risk_scores": [
                    {
                        "risk_type": "cardiovascular",
                        "score": 42.5,
                        "category": "moderate",
                        "factors": [
                            "Age 45+",
                            "Hypertension",
                            "High cholesterol"
                        ],
                        "recommendations": [
                            "Monitor blood pressure regularly",
                            "Consider statin therapy",
                            "Lifestyle modifications (diet, exercise)"
                        ]
                    }
                ],
                "overall_risk_level": "moderate"
            }
        }
