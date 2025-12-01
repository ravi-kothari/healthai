"""
CarePrep Forms API - Appointment-Specific Data Collection.

Handles medical history forms, symptom checker data collection,
and completion tracking for specific appointments.

**Note**: This is the lightweight forms API. For AI-powered symptom analysis,
see careprep_unified.py (/api/careprep/*).
"""

from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import logging
import secrets
import uuid

from src.api.database import get_db
from src.api.models.careprep import CarePrepResponse, CarePrepAccessToken
from src.api.models.appointment import Appointment
from src.api.models.patient import Patient
from src.api.models.user import User
from src.api.auth.dependencies import get_current_user, require_permission
from src.api.auth.permissions import Permission
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/careprep/forms",
    tags=["CarePrep Forms"]
)


# Pydantic schemas for request/response validation
class MedicalHistoryData(BaseModel):
    """Medical history data structure."""
    medications: list[Dict[str, str]] = []
    allergies: list[Dict[str, str]] = []
    conditions: list[Dict[str, str]] = []
    family_history: list[Dict[str, str]] = []
    surgeries: list[Dict[str, str]] = []
    immunizations: list[Dict[str, str]] = []


class SymptomCheckerData(BaseModel):
    """Symptom checker data structure."""
    symptoms: list[Dict[str, Any]] = []
    urgency: Optional[str] = None
    recommendations: Optional[str] = None
    analysis: Optional[str] = None


class TokenResponse(BaseModel):
    token: str
    expires_at: datetime
    url: str


@router.post("/send/{patient_id}", response_model=TokenResponse)
async def send_careprep_link(
    patient_id: str,
    appointment_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.MANAGE_APPOINTMENT))
):
    """
    Generate and send CarePrep link to patient.
    
    Provider-only endpoint to create unique access token and send to patient.
    """
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Verify appointment if provided
    if appointment_id:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Calculate expiration based on appointment date (24h after)
        # For now, default to 7 days from now if appointment date is not set or passed
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        if appointment.scheduled_start:
             expires_at = appointment.scheduled_start + timedelta(hours=24)
    else:
        # Default expiration 7 days
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    # Generate secure token
    token = secrets.token_urlsafe(32)
    
    # Create access token record
    access_token = CarePrepAccessToken(
        token=token,
        patient_id=patient_id,
        appointment_id=appointment_id,
        expires_at=expires_at
    )
    db.add(access_token)
    db.commit()
    db.refresh(access_token)
    
    # Construct URL (assuming frontend runs on same domain/port for now, or use env var)
    # In production, this should come from config
    base_url = "http://localhost:3000" 
    url = f"{base_url}/careprep/form/{token}"
    
    # In a real implementation, we would send email/SMS here
    logger.info(f"Generated CarePrep token for patient {patient_id}: {token}")
    logger.info(f"CarePrep URL: {url}")
    
    return {
        "token": token,
        "expires_at": expires_at,
        "url": url
    }


@router.get("/token/{token}")
async def validate_token_and_get_context(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Validate token and return context (patient name, appointment details).
    Public endpoint.
    """
    access_token = db.query(CarePrepAccessToken).filter(
        CarePrepAccessToken.token == token,
        CarePrepAccessToken.is_active == True
    ).first()
    
    if not access_token:
        raise HTTPException(status_code=404, detail="Invalid or expired token")
        
    if access_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token has expired")
        
    # Update access stats
    if not access_token.first_accessed_at:
        access_token.first_accessed_at = datetime.now(timezone.utc)
    access_token.last_accessed_at = datetime.now(timezone.utc)
    db.commit()
    
    # Fetch details
    patient = db.query(Patient).filter(Patient.id == access_token.patient_id).first()
    appointment = None
    if access_token.appointment_id:
        appointment = db.query(Appointment).filter(Appointment.id == access_token.appointment_id).first()
        
    return {
        "valid": True,
        "patient_first_name": patient.first_name if patient else "Patient",
        "appointment": {
            "id": appointment.id,
            "date": appointment.scheduled_start,
            "provider_id": appointment.provider_id
        } if appointment else None,
        "patient_id": access_token.patient_id
    }


@router.get("/form/{token}")
async def get_careprep_form_by_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Get CarePrep form data using token.
    Public endpoint.
    """
    # Validate token logic reused or called directly
    access_token = db.query(CarePrepAccessToken).filter(
        CarePrepAccessToken.token == token,
        CarePrepAccessToken.is_active == True
    ).first()
    
    if not access_token or access_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    # Get existing response if any
    careprep = None
    if access_token.appointment_id:
        careprep = db.query(CarePrepResponse).filter(
            CarePrepResponse.appointment_id == access_token.appointment_id
        ).first()
        
    if not careprep:
        return {
            "medical_history_data": None,
            "symptom_checker_data": None,
            "status": "new"
        }
        
    return careprep.to_dict()


@router.post("/form/{token}/submit")
async def submit_careprep_response_by_token(
    token: str,
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Submit CarePrep response using token.
    Public endpoint.
    """
    access_token = db.query(CarePrepAccessToken).filter(
        CarePrepAccessToken.token == token,
        CarePrepAccessToken.is_active == True
    ).first()
    
    if not access_token or access_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=404, detail="Invalid or expired token")
        
    if not access_token.appointment_id:
         raise HTTPException(status_code=400, detail="Token not linked to an appointment")

    # Get or create response
    careprep = db.query(CarePrepResponse).filter(
        CarePrepResponse.appointment_id == access_token.appointment_id
    ).first()
    
    if not careprep:
        careprep = CarePrepResponse(
            appointment_id=access_token.appointment_id,
            patient_id=access_token.patient_id
        )
        db.add(careprep)
        
    # Update data
    if "medical_history" in data:
        careprep.medical_history_data = data["medical_history"]
        careprep.medical_history_completed = True
        careprep.medical_history_updated_at = datetime.utcnow()
        
    if "symptoms" in data:
        careprep.symptom_checker_data = data["symptoms"]
        careprep.symptom_checker_completed = True
        careprep.symptom_checker_updated_at = datetime.utcnow()
        
    careprep.calculate_completion()
    
    # Update token stats
    access_token.submission_count += 1
    access_token.last_accessed_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(careprep)
    
    return careprep.to_dict()


@router.get("/summary/{token}")
async def get_appointment_summary_by_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Get appointment summary using token.
    Public endpoint.
    """
    access_token = db.query(CarePrepAccessToken).filter(
        CarePrepAccessToken.token == token,
        CarePrepAccessToken.is_active == True
    ).first()
    
    if not access_token or access_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    # For MVP, we will return the CarePrepResponse data + basic patient info
    # In a full implementation, we would call the data_transformer service
    
    careprep = None
    if access_token.appointment_id:
        careprep = db.query(CarePrepResponse).filter(
            CarePrepResponse.appointment_id == access_token.appointment_id
        ).first()
        
    patient = db.query(Patient).filter(Patient.id == access_token.patient_id).first()
    appointment = None
    if access_token.appointment_id:
        appointment = db.query(Appointment).filter(Appointment.id == access_token.appointment_id).first()

    return {
        "patient_info": {
            "first_name": patient.first_name,
            "last_name": patient.last_name,
        },
        "appointment": {
            "date": appointment.scheduled_start if appointment else None,
            "provider_id": appointment.provider_id if appointment else None
        },
        "submission": careprep.to_dict() if careprep else None,
        "status": "completed" if careprep and careprep.all_tasks_completed else "pending"
    }


@router.post("/form/{token}/generate-questionnaire")
async def generate_questionnaire_by_token(
    token: str,
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Generate dynamic questionnaire using AI (Public endpoint).
    """
    access_token = db.query(CarePrepAccessToken).filter(
        CarePrepAccessToken.token == token,
        CarePrepAccessToken.is_active == True
    ).first()
    
    if not access_token or access_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    chief_complaint = data.get("chief_complaint")
    if not chief_complaint:
        raise HTTPException(status_code=400, detail="Chief complaint is required")

    # Import here to avoid circular dependencies if any
    from src.api.services.previsit.symptom_analyzer import symptom_analyzer

    try:
        questions = await symptom_analyzer.generate_questionnaire(
            chief_complaint=chief_complaint,
            symptoms=data.get("symptoms", [])
        )
        return {"questions": questions}
    except Exception as e:
        logger.error(f"Error generating questionnaire: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate questionnaire")

@router.get("/{appointment_id}")
async def get_careprep_response(
    appointment_id: str,
    db: Session = Depends(get_db)
):
    """
    Get CarePrep response for an appointment (Internal/Legacy).
    """
    # Verify appointment exists
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Get or create CarePrep response
    careprep = db.query(CarePrepResponse).filter(
        CarePrepResponse.appointment_id == appointment_id
    ).first()

    if not careprep:
        # Return empty structure if no response exists yet
        return {
            "appointment_id": appointment_id,
            "patient_id": appointment.patient_id,
            "medical_history_completed": False,
            "medical_history_data": None,
            "symptom_checker_completed": False,
            "symptom_checker_data": None,
            "all_tasks_completed": False,
            "completed_at": None
        }

    logger.info(f"Retrieved CarePrep response for appointment {appointment_id}")
    return careprep.to_dict()


@router.post("/{appointment_id}/medical-history")
async def save_medical_history(
    appointment_id: str,
    medical_history: MedicalHistoryData = Body(...),
    db: Session = Depends(get_db)
):
    """
    Save medical history for an appointment (Internal/Legacy).
    """
    # Verify appointment exists
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Get or create CarePrep response
    careprep = db.query(CarePrepResponse).filter(
        CarePrepResponse.appointment_id == appointment_id
    ).first()

    if not careprep:
        careprep = CarePrepResponse(
            appointment_id=appointment_id,
            patient_id=appointment.patient_id
        )
        db.add(careprep)

    # Update medical history
    careprep.medical_history_data = medical_history.dict()
    careprep.medical_history_completed = True
    careprep.medical_history_updated_at = datetime.utcnow()

    # Calculate overall completion
    careprep.calculate_completion()

    db.commit()
    db.refresh(careprep)

    logger.info(f"Saved medical history for appointment {appointment_id}")

    return careprep.to_dict()


@router.post("/{appointment_id}/symptom-checker")
async def save_symptom_checker(
    appointment_id: str,
    symptom_data: SymptomCheckerData = Body(...),
    db: Session = Depends(get_db)
):
    """
    Save symptom checker results for an appointment (Internal/Legacy).
    """
    # Verify appointment exists
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Get or create CarePrep response
    careprep = db.query(CarePrepResponse).filter(
        CarePrepResponse.appointment_id == appointment_id
    ).first()

    if not careprep:
        careprep = CarePrepResponse(
            appointment_id=appointment_id,
            patient_id=appointment.patient_id
        )
        db.add(careprep)

    # Update symptom checker
    careprep.symptom_checker_data = symptom_data.dict()
    careprep.symptom_checker_completed = True
    careprep.symptom_checker_updated_at = datetime.utcnow()

    # Calculate overall completion
    careprep.calculate_completion()

    db.commit()
    db.refresh(careprep)

    logger.info(f"Saved symptom checker for appointment {appointment_id}")

    return careprep.to_dict()


@router.get("/{appointment_id}/status")
async def get_careprep_status(
    appointment_id: str,
    db: Session = Depends(get_db)
):
    """
    Get completion status for CarePrep tasks.
    """
    careprep = db.query(CarePrepResponse).filter(
        CarePrepResponse.appointment_id == appointment_id
    ).first()

    if not careprep:
        return {
            "appointment_id": appointment_id,
            "medical_history_completed": False,
            "symptom_checker_completed": False,
            "all_tasks_completed": False,
            "completion_percentage": 0
        }

    # Calculate completion percentage
    total_tasks = 2  # Medical history + Symptom checker
    completed_tasks = sum([
        careprep.medical_history_completed,
        careprep.symptom_checker_completed
    ])
    completion_percentage = (completed_tasks / total_tasks) * 100

    return {
        "appointment_id": appointment_id,
        "medical_history_completed": careprep.medical_history_completed,
        "symptom_checker_completed": careprep.symptom_checker_completed,
        "all_tasks_completed": careprep.all_tasks_completed,
        "completion_percentage": completion_percentage,
        "completed_at": careprep.completed_at.isoformat() if careprep.completed_at else None
    }
