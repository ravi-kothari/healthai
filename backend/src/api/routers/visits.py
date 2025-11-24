"""
Visit Management API Endpoints.
Handles clinical visit sessions, transcriptions, and SOAP notes.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from src.api.database import get_db
from src.api.auth.dependencies import get_current_user
from src.api.models.user import User
from src.api.models.visit import VisitStatus
from src.api.schemas.visit_schemas import (
    VisitCreate,
    VisitUpdate,
    VisitEnd,
    VisitResponse,
    VisitWithTranscripts,
    TranscriptionCreate,
    TranscriptionResponse
)
from src.api.services.visit_service import visit_service
from src.api.services.transcription_service import transcription_service
from src.api.services.ai.soap_generator import soap_generator

router = APIRouter(prefix="/api/visits", tags=["visits"])
logger = logging.getLogger(__name__)


# ==================== Visit Endpoints ====================

@router.post("/from-appointment/{appointment_id}", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
async def create_visit_from_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new visit from an appointment with CarePrep data auto-populated.

    Only providers (doctor, nurse, admin, staff) can create visits.
    Automatically populates Subjective section with CarePrep symptom and medical history data.
    """
    # Check if user is a provider
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can create visits"
        )

    try:
        visit = await visit_service.create_visit_from_appointment(
            db=db,
            appointment_id=appointment_id,
            provider_id=current_user.id
        )

        return visit

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating visit from appointment: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
async def create_visit(
    visit_data: VisitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new visit.

    Only providers (doctor, nurse, admin, staff) can create visits.
    """
    # Check if user is a provider
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can create visits"
        )

    try:
        visit = await visit_service.create_visit(
            db=db,
            patient_id=str(visit_data.patient_id),
            provider_id=str(visit_data.provider_id),
            visit_type=visit_data.visit_type,
            chief_complaint=visit_data.chief_complaint,
            reason_for_visit=visit_data.reason_for_visit,
            scheduled_start=visit_data.scheduled_start
        )

        return visit

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{visit_id}/start", response_model=VisitResponse)
async def start_visit(
    visit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a visit session.

    Only providers can start visits.
    """
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can start visits"
        )

    try:
        visit = await visit_service.start_visit(db=db, visit_id=visit_id)
        return visit

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{visit_id}/end", response_model=VisitResponse)
async def end_visit(
    visit_id: str,
    visit_end: VisitEnd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    End a visit session and save SOAP notes.

    Only providers can end visits.
    """
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can end visits"
        )

    try:
        visit = await visit_service.end_visit(
            db=db,
            visit_id=visit_id,
            subjective=visit_end.subjective,
            objective=visit_end.objective,
            assessment=visit_end.assessment,
            plan=visit_end.plan,
            vitals=visit_end.vitals,
            diagnoses=visit_end.diagnoses,
            medications=visit_end.medications
        )

        return visit

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{visit_id}/notes", response_model=VisitResponse)
async def update_visit_notes(
    visit_id: str,
    notes: VisitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update SOAP notes for a visit.

    Only providers can update notes.
    """
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can update visit notes"
        )

    try:
        visit = await visit_service.update_visit_notes(
            db=db,
            visit_id=visit_id,
            subjective=notes.subjective,
            objective=notes.objective,
            assessment=notes.assessment,
            plan=notes.plan
        )

        return visit

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{visit_id}", response_model=VisitWithTranscripts)
async def get_visit(
    visit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get visit details with transcripts.

    Patients can view their own visits.
    Providers can view any visit.
    """
    visit = await visit_service.get_visit(db=db, visit_id=visit_id)

    if not visit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")

    # Check permissions
    if current_user.role == "patient":
        # Patients can only view their own visits
        if str(visit.patient_id) != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own visits"
            )
    elif current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    return visit


@router.get("/patient/{patient_id}", response_model=List[VisitResponse])
async def get_patient_visits(
    patient_id: str,
    status_filter: Optional[VisitStatus] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all visits for a patient.

    Patients can view their own visits.
    Providers can view any patient's visits.
    """
    # Check permissions
    if current_user.role == "patient":
        if patient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own visits"
            )
    elif current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    visits = await visit_service.get_patient_visits(
        db=db,
        patient_id=patient_id,
        status=status_filter,
        limit=limit
    )

    return visits


@router.get("/provider/{provider_id}", response_model=List[VisitResponse])
async def get_provider_visits(
    provider_id: str,
    status_filter: Optional[VisitStatus] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all visits for a provider.

    Only providers can access this endpoint.
    """
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can access this endpoint"
        )

    # Providers can only view their own visits unless they're admin
    if current_user.role != "admin" and provider_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own visits"
        )

    visits = await visit_service.get_provider_visits(
        db=db,
        provider_id=provider_id,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
        limit=limit
    )

    return visits


@router.delete("/{visit_id}", response_model=VisitResponse)
async def cancel_visit(
    visit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a visit.

    Only providers can cancel visits.
    """
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can cancel visits"
        )

    try:
        visit = await visit_service.cancel_visit(db=db, visit_id=visit_id)
        return visit

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== Transcription Endpoints ====================

@router.post("/{visit_id}/transcriptions", response_model=TranscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_transcription(
    visit_id: str,
    audio_file: UploadFile = File(...),
    language: str = "en-US",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload audio file and create transcription.

    Only providers can create transcriptions.
    """
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can create transcriptions"
        )

    # Verify visit exists
    visit = await visit_service.get_visit(db=db, visit_id=visit_id)
    if not visit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")

    try:
        # Read audio file
        audio_data = await audio_file.read()

        # Get file extension
        audio_format = audio_file.filename.split('.')[-1] if audio_file.filename else "wav"

        # Create transcription
        transcript = await transcription_service.create_transcription(
            db=db,
            visit_id=visit_id,
            audio_data=audio_data,
            audio_format=audio_format,
            language=language
        )

        return transcript

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{visit_id}/transcriptions", response_model=List[TranscriptionResponse])
async def get_visit_transcriptions(
    visit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all transcriptions for a visit.

    Providers can view any visit's transcriptions.
    Patients can view their own visit transcriptions.
    """
    # Verify visit exists and check permissions
    visit = await visit_service.get_visit(db=db, visit_id=visit_id)
    if not visit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")

    if current_user.role == "patient":
        if str(visit.patient_id) != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own visit transcriptions"
            )
    elif current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    transcripts = await transcription_service.get_visit_transcriptions(
        db=db,
        visit_id=visit_id
    )

    return transcripts


@router.get("/transcriptions/{transcript_id}", response_model=TranscriptionResponse)
async def get_transcription(
    transcript_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific transcription by ID.

    Only providers can access transcriptions.
    """
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can access transcriptions"
        )

    transcript = await transcription_service.get_transcription(
        db=db,
        transcript_id=transcript_id
    )

    if not transcript:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")

    return transcript


# ==================== SOAP Notes Generation ====================

@router.post("/{visit_id}/generate-soap", response_model=Dict[str, Any])
async def generate_soap_notes(
    visit_id: str,
    transcript_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate SOAP notes from visit transcription.

    If transcript_id is provided, uses that specific transcription.
    Otherwise, uses the most recent transcription for the visit.

    Only providers can generate SOAP notes.
    """
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can generate SOAP notes"
        )

    # Verify visit exists
    visit = await visit_service.get_visit(db=db, visit_id=visit_id)
    if not visit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")

    try:
        # Get transcription
        if transcript_id:
            transcript = await transcription_service.get_transcription(db=db, transcript_id=transcript_id)
        else:
            # Get most recent transcription for visit
            transcripts = await transcription_service.get_visit_transcriptions(db=db, visit_id=visit_id)
            if not transcripts:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No transcriptions found for this visit"
                )
            transcript = transcripts[0]  # Most recent

        if not transcript or not transcript.transcription_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcription text is empty or not available"
            )

        # Build patient context
        patient_context = None
        if visit.patient:
            patient_context = {
                "age": visit.patient.age if hasattr(visit.patient, 'age') else None,
                "gender": visit.patient.gender,
                "allergies": visit.patient.allergies or [],
                "chronic_conditions": visit.patient.chronic_conditions or []
            }

        # Build visit context
        visit_context = {
            "chief_complaint": visit.chief_complaint,
            "visit_type": visit.visit_type,
            "reason_for_visit": visit.reason_for_visit
        }

        # Generate SOAP notes
        soap_notes = await soap_generator.generate_soap_from_transcription(
            transcription_text=transcript.transcription_text,
            patient_context=patient_context,
            visit_context=visit_context
        )

        # Auto-save to visit if not already completed
        if visit.status == "IN_PROGRESS":
            await visit_service.update_visit_notes(
                db=db,
                visit_id=visit_id,
                subjective=soap_notes.get("subjective"),
                objective=soap_notes.get("objective"),
                assessment=soap_notes.get("assessment"),
                plan=soap_notes.get("plan")
            )

        return {
            "visit_id": visit_id,
            "transcript_id": str(transcript.id),
            "soap_notes": soap_notes,
            "auto_saved": visit.status == "IN_PROGRESS"
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating SOAP notes: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{visit_id}/refine-soap-section", response_model=Dict[str, str])
async def refine_soap_section(
    visit_id: str,
    section: str,
    original_text: str,
    refinement_instructions: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Refine a specific SOAP section based on user instructions.

    Only providers can refine SOAP notes.
    """
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can refine SOAP notes"
        )

    # Validate section
    valid_sections = ["subjective", "objective", "assessment", "plan"]
    if section.lower() not in valid_sections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid section. Must be one of: {', '.join(valid_sections)}"
        )

    try:
        refined_text = await soap_generator.refine_soap_section(
            section=section.lower(),
            original_text=original_text,
            refinement_instructions=refinement_instructions
        )

        return {
            "section": section.lower(),
            "refined_text": refined_text
        }

    except Exception as e:
        logger.error(f"Error refining SOAP section: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
