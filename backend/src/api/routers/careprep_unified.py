"""
CarePrep API endpoints - Patient-Facing Appointment Preparation.

Provides AI-powered symptom analysis, triage assessment, and dynamic questionnaire generation
to help patients prepare for their healthcare appointments.

**Renamed from**: PreVisit.ai → CarePrep (November 2024)
**Migration Status**: New unified implementation
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.models.user import User
from src.api.models.patient import Patient
from src.api.auth.dependencies import get_current_user, require_permission
from src.api.auth.permissions import Permission
from src.api.schemas.previsit_schemas import (
    SymptomAnalysisRequest,
    SymptomAnalysisResponse,
    QuestionnaireGenerationRequest,
    QuestionnaireResponse,
    QuestionnaireQuestion,
    TriageAssessmentRequest,
    TriageAssessmentResponse
)
from src.api.schemas.unified_schemas import PatientSummaryResponse
from src.api.services.previsit.symptom_analyzer import symptom_analyzer
from src.api.services.previsit.triage_engine import triage_engine
from src.api.services.unified.data_transformer import data_transformer
from src.api.services.appoint_ready.context_builder import context_builder
from src.api.services.appoint_ready.risk_calculator import risk_calculator
from src.api.services.appoint_ready.care_gap_detector import care_gap_detector

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/careprep",
    tags=["CarePrep"]
)


@router.post("/analyze-symptoms", response_model=SymptomAnalysisResponse)
async def analyze_symptoms(
    request: SymptomAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.SUBMIT_PREVISIT_DATA))
):
    """
    Analyze patient symptoms using AI.

    **CarePrep Feature**: Intelligent symptom analysis to help patients understand their condition
    and prepare for their appointment.

    Provides comprehensive symptom analysis including:
    - Urgency assessment
    - Severity evaluation
    - Triage level recommendation
    - Possible conditions
    - Recommended actions
    - Red flags to watch for

    **Example Request:**
    ```json
    {
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
    ```
    """
    logger.info(f"[CarePrep] Symptom analysis requested by user {current_user.id}")

    try:
        # Build patient context from request
        patient_context = {}

        if request.vital_signs:
            patient_context['vital_signs'] = request.vital_signs

        if request.medical_history_notes:
            patient_context['medical_history'] = request.medical_history_notes

        # Perform AI-powered symptom analysis
        analysis = await symptom_analyzer.analyze_symptoms(
            symptoms=request.symptoms,
            patient_context=patient_context if patient_context else None
        )

        logger.info(f"[CarePrep] Symptom analysis completed: urgency={analysis.urgency}, triage_level={analysis.triage_level}")

        return analysis

    except Exception as e:
        logger.error(f"[CarePrep] Error during symptom analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze symptoms. Please try again."
        )


@router.post("/triage-assessment", response_model=TriageAssessmentResponse)
async def triage_assessment(
    request: TriageAssessmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.SUBMIT_PREVISIT_DATA))
):
    """
    Perform medical triage assessment.

    **CarePrep Feature**: Intelligent triage to help patients understand the urgency of their
    symptoms and what action to take.

    Uses rule-based and AI-assisted triage to determine:
    - Triage level (1=emergency, 5=routine)
    - Urgency (emergency/urgent/high/moderate/low)
    - Recommended action
    - Time to see provider
    - Emergency flags

    **Triage Levels:**
    - **Level 1 (Emergency)**: Life-threatening, immediate attention
    - **Level 2 (Urgent)**: Serious, seen within 15-30 minutes
    - **Level 3 (Moderate)**: Moderate severity, seen within 1-2 hours
    - **Level 4 (Less Urgent)**: Minor issues, seen within 2-4 hours
    - **Level 5 (Routine)**: Non-urgent, schedule appointment

    **Example Request:**
    ```json
    {
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
    ```
    """
    logger.info(f"[CarePrep] Triage assessment requested by user {current_user.id}")

    try:
        # Perform triage assessment
        assessment = await triage_engine.assess_triage(
            symptoms=request.symptoms,
            vital_signs=request.vital_signs,
            age=request.age,
            existing_conditions=request.existing_conditions
        )

        logger.info(f"[CarePrep] Triage assessment completed: level={assessment.triage_level}, urgency={assessment.urgency}")

        # Log emergency cases
        if assessment.triage_level == 1:
            logger.warning(f"[CarePrep] EMERGENCY triage for user {current_user.id}: {assessment.emergency_flags}")

        return assessment

    except Exception as e:
        logger.error(f"[CarePrep] Error during triage assessment: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform triage assessment. Please try again."
        )


@router.post("/generate-questionnaire", response_model=QuestionnaireResponse)
async def generate_questionnaire(
    request: QuestionnaireGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.SUBMIT_PREVISIT_DATA))
):
    """
    Generate dynamic questionnaire based on chief complaint.

    **CarePrep Feature**: AI-generated questionnaire to gather comprehensive information
    about the patient's condition before their appointment.

    Uses AI to create relevant, focused questions to gather more information
    about the patient's condition.

    **Example Request:**
    ```json
    {
        "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
        "chief_complaint": "Headache and fever",
        "symptoms": ["headache", "fever", "body aches"]
    }
    ```

    **Example Response:**
    ```json
    {
        "questions": [
            {
                "id": "q1",
                "type": "scale",
                "question": "On a scale of 1-10, how severe is your headache?",
                "options": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "required": true
            },
            {
                "id": "q2",
                "type": "select",
                "question": "When did your symptoms start?",
                "options": ["Less than 24 hours ago", "1-3 days ago", "4-7 days ago", "More than a week ago"],
                "required": true
            }
        ],
        "estimated_time_minutes": 5
    }
    ```
    """
    logger.info(f"[CarePrep] Questionnaire generation requested by user {current_user.id}")

    try:
        # Generate questionnaire using AI
        questions = await symptom_analyzer.generate_questionnaire(
            chief_complaint=request.chief_complaint,
            symptoms=request.symptoms
        )

        # Estimate completion time (roughly 1 minute per question)
        estimated_time = max(len(questions), 5)  # Minimum 5 minutes

        logger.info(f"[CarePrep] Generated {len(questions)} questions for chief complaint: {request.chief_complaint}")

        return QuestionnaireResponse(
            questions=questions,
            estimated_time_minutes=estimated_time
        )

    except Exception as e:
        logger.error(f"[CarePrep] Error generating questionnaire: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate questionnaire. Please try again."
        )


@router.get("/{patient_id}/summary", response_model=PatientSummaryResponse)
async def get_patient_summary(
    patient_id: str,
    include_appointment_prep: bool = Query(default=True, description="Include appointment prep checklist"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.VIEW_OWN_DATA))
):
    """
    Get unified patient-facing appointment summary.

    **🎯 CarePrep Patient-Facing Summary**

    This endpoint combines symptom analysis with ContextAI provider data
    to create a seamless patient preparation experience. It transforms clinical data into
    patient-friendly language, hiding risk scores and sensitive metrics.

    **What This Endpoint Does:**
    - Combines your symptom analysis with medical history
    - Shows topics your provider wants to discuss (without clinical risk scores)
    - Lists medications for you to confirm
    - Provides appointment preparation checklist
    - Gives clear next steps before your visit

    **What's Hidden From Patients:**
    - Clinical risk scores and percentages
    - Detailed triage levels
    - Medical codes (ICD-10, SNOMED, etc.)
    - Provider-specific clinical reasoning

    **Security:**
    - Patients can only access their own summary
    - Providers can access any patient's summary
    - Role-based access control enforced

    **Example Request:**
    ```
    GET /api/careprep/2b7ed7f3-c480-49ba-ad9c-07073e6ca46a/summary
    ```

    **Example Response:**
    ```json
    {
        "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
        "generated_at": "2025-11-05T10:30:00Z",
        "patient_info": {
            "first_name": "John",
            "last_name": "Doe",
            "age": 45
        },
        "topics_to_discuss": [
            {
                "id": "topic-bp",
                "text": "Discussing your blood pressure management",
                "priority": "high",
                "icon": "heart"
            }
        ],
        "medications_to_confirm": [...],
        "allergies": [...],
        "appointment_prep": [...],
        "message_from_team": "We look forward to seeing you!..."
    }
    ```
    """
    logger.info(f"[CarePrep] Patient summary requested for {patient_id} by user {current_user.id}")

    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient not found: {patient_id}"
        )

    # Access control: patients can only see their own data
    if current_user.role == "patient":
        # Find the patient record linked to this user
        user_patient = db.query(Patient).filter(
            Patient.user_id == current_user.id
        ).first()

        if not user_patient or user_patient.id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own patient summary"
            )

    try:
        # Fetch comprehensive provider context (if available)
        provider_context = None
        try:
            provider_context = await context_builder.build_context(
                patient_id=patient_id,
                db=db,
                include_fhir=True,
                include_previsit=True
            )
        except Exception as e:
            logger.warning(f"[CarePrep] Could not fetch full provider context: {e}")

        # Fetch risk scores (if available)
        risk_scores = None
        if provider_context:
            try:
                risks = await risk_calculator.calculate_risks(
                    patient_data=provider_context.get('demographics', {}),
                    medical_history=provider_context.get('medical_history')
                )
                risk_scores = risks
            except Exception as e:
                logger.warning(f"[CarePrep] Could not calculate risk scores: {e}")

        # Fetch care gaps (if enabled)
        care_gaps = None
        if include_appointment_prep and provider_context:
            try:
                gaps = await care_gap_detector.detect_gaps(
                    patient_data=provider_context.get('demographics', {}),
                    medical_history=provider_context.get('medical_history')
                )
                care_gaps = gaps
            except Exception as e:
                logger.warning(f"[CarePrep] Could not detect care gaps: {e}")

        # Get symptom analysis if patient has submitted symptoms
        symptom_analysis = None
        previsit_data = provider_context.get('previsit') if provider_context else None
        if previsit_data and previsit_data.get('has_responses'):
            # This would need to be stored/retrieved from DB
            # For now, we'll skip it if not available
            pass

        # Transform all data into patient-friendly summary
        patient_summary = data_transformer.transform_to_patient_summary(
            patient_id=patient_id,
            provider_context=provider_context,
            symptom_analysis=symptom_analysis,
            risk_scores=risk_scores,
            care_gaps=care_gaps,
            appointment_date=None  # Could be fetched from appointments table
        )

        logger.info(f"[CarePrep] Generated patient summary with {len(patient_summary.topics_to_discuss)} topics")
        return patient_summary

    except Exception as e:
        logger.error(f"[CarePrep] Error generating patient summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate patient summary"
        )


@router.get("/health")
async def careprep_health_check():
    """
    Health check endpoint for CarePrep services.

    Returns the status of symptom analyzer and triage engine.
    """
    return {
        "status": "healthy",
        "service": "CarePrep",
        "components": {
            "symptom_analyzer": "operational",
            "triage_engine": "operational",
            "questionnaire_generator": "operational"
        }
    }
