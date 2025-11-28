"""
CarePrep Forms API - Appointment-Specific Data Collection.

Handles medical history forms, symptom checker data collection,
and completion tracking for specific appointments.

**Note**: This is the lightweight forms API. For AI-powered symptom analysis,
see careprep_unified.py (/api/careprep/*).
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any
import logging

from src.api.database import get_db
from src.api.models.careprep import CarePrepResponse
from src.api.models.appointment import Appointment
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


@router.get("/{appointment_id}")
async def get_careprep_response(
    appointment_id: str,
    db: Session = Depends(get_db)
):
    """
    Get CarePrep response for an appointment (public endpoint, no auth).

    This endpoint allows patients to retrieve their saved CarePrep data
    using the appointment ID from the CarePrep link token.

    Args:
        appointment_id: The appointment ID
        db: Database session

    Returns:
        dict: CarePrep response data or empty structure if not found
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
    Save medical history for an appointment (public endpoint, no auth).

    Args:
        appointment_id: The appointment ID
        medical_history: Medical history data
        db: Database session

    Returns:
        dict: Updated CarePrep response
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
    Save symptom checker results for an appointment (public endpoint, no auth).

    Args:
        appointment_id: The appointment ID
        symptom_data: Symptom checker data
        db: Database session

    Returns:
        dict: Updated CarePrep response
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

    This endpoint provides a quick summary of what's been completed.

    Args:
        appointment_id: The appointment ID
        db: Database session

    Returns:
        dict: Completion status for each task
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
