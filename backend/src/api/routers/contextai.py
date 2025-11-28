"""
ContextAI API endpoints - Provider-Facing Clinical Decision Support.

Provides comprehensive appointment context, risk assessment, care gap detection,
and clinical decision support tools to help providers prepare for patient appointments.

**Renamed from**: Appoint-Ready → ContextAI (November 2024)
**Migration Status**: New unified implementation
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.models.user import User
from src.api.models.patient import Patient
from src.api.auth.dependencies import get_current_user
from src.api.schemas.appoint_ready_schemas import (
    AppointmentContextResponse,
    CareGapsResponse,
    RiskAssessmentResponse,
    TestResultsResponse,
    MedicationReviewResponse,
    CareGap,
    RiskScore
)
from src.api.services.appoint_ready.context_builder import context_builder
from src.api.services.appoint_ready.care_gap_detector import care_gap_detector
from src.api.services.appoint_ready.risk_calculator import risk_calculator
from src.api.services.appoint_ready.test_results_analyzer import TestResultsAnalyzer
from src.api.services.appoint_ready.medication_interaction_checker import MedicationInteractionChecker

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/contextai",
    tags=["ContextAI"]
)


@router.get("/context/{patient_id}", response_model=AppointmentContextResponse)
async def get_appointment_context(
    patient_id: str,
    include_fhir: bool = Query(default=True, description="Include FHIR medical history"),
    include_previsit: bool = Query(default=True, description="Include PreVisit.ai responses"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive appointment context for a patient.

    Aggregates data from multiple sources:
    - Patient demographics (database)
    - Medical history (FHIR server)
    - PreVisit.ai responses
    - Summary with alerts and highlights

    **Requires:** Provider role (doctor, nurse, admin, staff)

    **Example Request:**
    ```
    GET /api/contextai/context/2b7ed7f3-c480-49ba-ad9c-07073e6ca46a?include_fhir=true
    ```

    **Example Response:**
    ```json
    {
        "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
        "generated_at": "2025-11-02T10:30:00Z",
        "data_sources": ["database", "fhir", "previsit"],
        "demographics": {
            "first_name": "John",
            "last_name": "Doe",
            "mrn": "MRN-20251102-12345",
            "age": 45
        },
        "medical_history": {
            "conditions": [...],
            "medications": [...],
            "allergies": [...]
        },
        "summary": {
            "has_data": true,
            "data_completeness": 100.0,
            "alerts": [...],
            "highlights": [...]
        }
    }
    ```
    """
    logger.info(f"[ContextAI] Appointment context requested for patient {patient_id} by user {current_user.id}")

    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient not found: {patient_id}"
        )

    # Role-based access control (providers only)
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only healthcare providers can access appointment context"
        )

    try:
        # Build comprehensive context
        context = await context_builder.build_context(
            patient_id=patient_id,
            db=db,
            include_fhir=include_fhir,
            include_previsit=include_previsit
        )

        logger.info(f"Context built with {len(context['data_sources'])} sources")
        return context

    except Exception as e:
        logger.error(f"Error building appointment context: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to build appointment context"
        )


@router.get("/care-gaps/{patient_id}", response_model=CareGapsResponse)
async def get_care_gaps(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Identify care gaps for a patient.

    Detects:
    - Missing preventive screenings (mammography, colonoscopy, etc.)
    - Overdue vaccinations (flu, pneumonia, COVID-19)
    - Chronic disease management gaps (A1C for diabetes, etc.)
    - Follow-up appointments

    **Requires:** Provider role

    **Example Response:**
    ```json
    {
        "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
        "gaps": [
            {
                "gap_type": "screening",
                "description": "Annual diabetic eye exam overdue",
                "priority": "high",
                "due_date": "2025-10-01",
                "overdue": true,
                "recommendation": "Schedule ophthalmology appointment"
            }
        ],
        "total_gaps": 3,
        "high_priority_count": 1,
        "overdue_count": 2
    }
    ```
    """
    logger.info(f"Care gaps analysis requested for patient {patient_id}")

    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient not found: {patient_id}"
        )

    # Role check
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only healthcare providers can access care gap analysis"
        )

    try:
        # Get patient context first
        context = await context_builder.build_context(patient_id, db)

        # Detect gaps
        gaps = await care_gap_detector.detect_gaps(
            patient_data=context.get('demographics', {}),
            medical_history=context.get('medical_history')
        )

        # Calculate statistics
        high_priority = len([g for g in gaps if g['priority'] == 'high'])
        overdue = len([g for g in gaps if g['overdue']])

        logger.info(f"Found {len(gaps)} care gaps for patient {patient_id}")

        return CareGapsResponse(
            patient_id=patient_id,
            gaps=[CareGap(**gap) for gap in gaps],
            total_gaps=len(gaps),
            high_priority_count=high_priority,
            overdue_count=overdue
        )

    except Exception as e:
        logger.error(f"Error detecting care gaps: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect care gaps"
        )


@router.get("/risk-assessment/{patient_id}", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate clinical risk scores for a patient.

    Risk assessments:
    - **Cardiovascular risk:** 10-year CVD risk (Framingham-based)
    - **Diabetes risk:** Type 2 diabetes risk (ADA-based)
    - **Fall risk:** Fall risk for elderly patients (STEADI-based)

    **Requires:** Provider role

    **Example Response:**
    ```json
    {
        "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
        "assessed_at": "2025-11-02T10:30:00Z",
        "risk_scores": [
            {
                "risk_type": "cardiovascular",
                "score": 42.5,
                "category": "moderate",
                "factors": ["Age 45+", "Hypertension"],
                "recommendations": [
                    "Monitor blood pressure regularly",
                    "Consider statin therapy"
                ]
            }
        ],
        "overall_risk_level": "moderate"
    }
    ```
    """
    logger.info(f"Risk assessment requested for patient {patient_id}")

    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient not found: {patient_id}"
        )

    # Role check
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only healthcare providers can access risk assessments"
        )

    try:
        # Get patient context
        context = await context_builder.build_context(patient_id, db)

        # Calculate risks
        risks = await risk_calculator.calculate_risks(
            patient_data=context.get('demographics', {}),
            medical_history=context.get('medical_history')
        )

        # Get overall risk level
        overall_risk = await risk_calculator.get_overall_risk_level(risks)

        logger.info(f"Calculated {len(risks)} risk scores for patient {patient_id}")

        return RiskAssessmentResponse(
            patient_id=patient_id,
            assessed_at=context.get('generated_at'),
            risk_scores=[RiskScore(**risk) for risk in risks],
            overall_risk_level=overall_risk
        )

    except Exception as e:
        logger.error(f"Error calculating risk assessment: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate risk assessment"
        )


@router.get("/test-results/{patient_id}", response_model=TestResultsResponse)
async def get_test_results(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get and analyze relevant test results for a patient.

    Highlights:
    - Abnormal lab values compared to reference ranges
    - Critical results requiring immediate attention
    - Trends over time for repeated tests
    - Categorized by test type (hematology, chemistry, etc.)

    **Requires:** Provider role

    **Example Response:**
    ```json
    {
        "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
        "results": [
            {
                "test_name": "Hemoglobin A1c",
                "value": "8.2",
                "unit": "%",
                "reference_range": "4.0-6.0",
                "status": "abnormal_high",
                "date": "2025-11-01T08:00:00Z",
                "category": "chemistry",
                "trend": "up"
            }
        ],
        "abnormal_count": 1,
        "critical_count": 0,
        "last_updated": "2025-11-02T10:30:00Z"
    }
    ```
    """
    logger.info(f"Test results requested for patient {patient_id}")

    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient not found: {patient_id}"
        )

    # Role check
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only healthcare providers can access test results"
        )

    try:
        # Analyze test results
        analyzer = TestResultsAnalyzer(db)
        results = analyzer.get_relevant_test_results(patient_id)

        logger.info(f"Found {len(results.get('results', []))} test results for patient {patient_id}")
        return TestResultsResponse(**results)

    except Exception as e:
        logger.error(f"Error analyzing test results: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze test results"
        )


@router.get("/medication-review/{patient_id}", response_model=MedicationReviewResponse)
async def get_medication_review(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform comprehensive medication review including interaction checking.

    Features:
    - Active medication list
    - Drug-drug interaction detection
    - Interaction severity levels (severe/moderate/mild)
    - Clinical recommendations
    - Drug allergy alerts

    **Requires:** Provider role

    **Example Response:**
    ```json
    {
        "patient_id": "2b7ed7f3-c480-49ba-ad9c-07073e6ca46a",
        "medications": [
            {
                "medication_id": "med-123",
                "name": "Warfarin",
                "dosage": "5mg",
                "frequency": "Once daily",
                "route": "Oral",
                "status": "active"
            }
        ],
        "interactions": [
            {
                "interaction_id": "1",
                "medication_1": "Warfarin",
                "medication_2": "Aspirin",
                "severity": "severe",
                "description": "Increased risk of bleeding",
                "recommendation": "Monitor INR closely"
            }
        ],
        "allergies": [
            {
                "allergen": "Penicillin",
                "reaction": "Rash, hives",
                "severity": "moderate"
            }
        ],
        "total_medications": 1,
        "interaction_count": 1,
        "severe_interaction_count": 1
    }
    ```
    """
    logger.info(f"Medication review requested for patient {patient_id}")

    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient not found: {patient_id}"
        )

    # Role check
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only healthcare providers can access medication reviews"
        )

    try:
        # Perform medication review
        checker = MedicationInteractionChecker(db)
        review = checker.get_medication_review(patient_id)

        logger.info(f"Medication review completed for patient {patient_id}: {review['total_medications']} meds, {review['interaction_count']} interactions")
        return MedicationReviewResponse(**review)

    except Exception as e:
        logger.error(f"Error performing medication review: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform medication review"
        )


@router.get("/health")
async def contextai_health_check():
    """
    Health check endpoint for ContextAI services.

    Returns status of all ContextAI components.
    """
    return {
        "status": "healthy",
        "services": {
            "context_builder": "operational",
            "care_gap_detector": "operational",
            "risk_calculator": "operational",
            "test_results_analyzer": "operational",
            "medication_interaction_checker": "operational"
        }
    }
