"""
Visit Management Service.
Handles clinical visit sessions, SOAP notes, and visit lifecycle.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.api.models.visit import Visit, VisitStatus, VisitType
from src.api.models.patient import Patient
from src.api.models.user import User

logger = logging.getLogger(__name__)


class VisitService:
    """Service for managing clinical visits."""

    async def create_visit(
        self,
        db: Session,
        patient_id: str,
        provider_id: str,
        visit_type: VisitType,
        chief_complaint: Optional[str] = None,
        reason_for_visit: Optional[str] = None,
        scheduled_start: Optional[datetime] = None
    ) -> Visit:
        """
        Create a new visit.

        Args:
            db: Database session
            patient_id: Patient ID
            provider_id: Provider (doctor/nurse) user ID
            visit_type: Type of visit
            chief_complaint: Patient's main complaint
            reason_for_visit: Reason for the visit
            scheduled_start: Scheduled start time

        Returns:
            Visit model instance
        """
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        # Verify provider exists and has appropriate role
        provider = db.query(User).filter(User.id == provider_id).first()
        if not provider:
            raise ValueError(f"Provider {provider_id} not found")

        if provider.role not in ["doctor", "nurse", "admin", "staff"]:
            raise ValueError(f"User {provider_id} is not a provider")

        # Create visit
        visit = Visit(
            patient_id=patient_id,
            provider_id=provider_id,
            visit_type=visit_type,
            status=VisitStatus.SCHEDULED,
            chief_complaint=chief_complaint,
            reason_for_visit=reason_for_visit,
            scheduled_start=scheduled_start
        )

        db.add(visit)
        db.commit()
        db.refresh(visit)

        logger.info(f"Created visit {visit.id} for patient {patient_id}")

        return visit

    async def start_visit(
        self,
        db: Session,
        visit_id: str
    ) -> Visit:
        """
        Start a visit session.

        Args:
            db: Database session
            visit_id: Visit ID

        Returns:
            Updated Visit instance
        """
        visit = db.query(Visit).filter(Visit.id == visit_id).first()

        if not visit:
            raise ValueError(f"Visit {visit_id} not found")

        if visit.status == VisitStatus.IN_PROGRESS:
            raise ValueError(f"Visit {visit_id} is already in progress")

        if visit.status == VisitStatus.COMPLETED:
            raise ValueError(f"Visit {visit_id} is already completed")

        visit.status = VisitStatus.IN_PROGRESS
        visit.actual_start = datetime.utcnow()

        db.commit()
        db.refresh(visit)

        logger.info(f"Started visit {visit_id}")

        return visit

    async def end_visit(
        self,
        db: Session,
        visit_id: str,
        subjective: Optional[str] = None,
        objective: Optional[str] = None,
        assessment: Optional[str] = None,
        plan: Optional[str] = None,
        vitals: Optional[Dict] = None,
        diagnoses: Optional[List[Dict]] = None,
        medications: Optional[List[Dict]] = None
    ) -> Visit:
        """
        End a visit session and save SOAP notes.

        Args:
            db: Database session
            visit_id: Visit ID
            subjective: SOAP - Subjective notes
            objective: SOAP - Objective notes
            assessment: SOAP - Assessment
            plan: SOAP - Plan
            vitals: Vital signs dictionary
            diagnoses: List of diagnoses with ICD-10 codes
            medications: List of prescribed medications

        Returns:
            Updated Visit instance
        """
        visit = db.query(Visit).filter(Visit.id == visit_id).first()

        if not visit:
            raise ValueError(f"Visit {visit_id} not found")

        if visit.status != VisitStatus.IN_PROGRESS:
            raise ValueError(f"Visit {visit_id} is not in progress")

        # Update visit
        visit.status = VisitStatus.COMPLETED
        visit.actual_end = datetime.utcnow()

        # Calculate duration
        if visit.actual_start:
            duration = visit.actual_end - visit.actual_start
            visit.duration_minutes = int(duration.total_seconds() / 60)

        # Update SOAP notes
        if subjective:
            visit.subjective = subjective
        if objective:
            visit.objective = objective
        if assessment:
            visit.assessment = assessment
        if plan:
            visit.plan = plan

        # Update vitals and clinical data
        if vitals:
            visit.vitals = vitals
        if diagnoses:
            visit.diagnoses = diagnoses
        if medications:
            visit.medications = medications

        db.commit()
        db.refresh(visit)

        logger.info(f"Ended visit {visit_id}, duration: {visit.duration_minutes} minutes")

        return visit

    async def update_visit_notes(
        self,
        db: Session,
        visit_id: str,
        subjective: Optional[str] = None,
        objective: Optional[str] = None,
        assessment: Optional[str] = None,
        plan: Optional[str] = None
    ) -> Visit:
        """
        Update SOAP notes for a visit.

        Args:
            db: Database session
            visit_id: Visit ID
            subjective: Subjective notes
            objective: Objective notes
            assessment: Assessment
            plan: Plan

        Returns:
            Updated Visit instance
        """
        visit = db.query(Visit).filter(Visit.id == visit_id).first()

        if not visit:
            raise ValueError(f"Visit {visit_id} not found")

        if subjective is not None:
            visit.subjective = subjective
        if objective is not None:
            visit.objective = objective
        if assessment is not None:
            visit.assessment = assessment
        if plan is not None:
            visit.plan = plan

        db.commit()
        db.refresh(visit)

        return visit

    async def get_visit(
        self,
        db: Session,
        visit_id: str
    ) -> Optional[Visit]:
        """
        Get visit by ID.

        Args:
            db: Database session
            visit_id: Visit ID

        Returns:
            Visit instance or None
        """
        return db.query(Visit).filter(Visit.id == visit_id).first()

    async def get_patient_visits(
        self,
        db: Session,
        patient_id: str,
        status: Optional[VisitStatus] = None,
        limit: int = 50
    ) -> List[Visit]:
        """
        Get all visits for a patient.

        Args:
            db: Database session
            patient_id: Patient ID
            status: Optional status filter
            limit: Maximum number of results

        Returns:
            List of Visit instances
        """
        query = db.query(Visit).filter(Visit.patient_id == patient_id)

        if status:
            query = query.filter(Visit.status == status)

        return query.order_by(Visit.created_at.desc()).limit(limit).all()

    async def get_provider_visits(
        self,
        db: Session,
        provider_id: str,
        status: Optional[VisitStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Visit]:
        """
        Get all visits for a provider.

        Args:
            db: Database session
            provider_id: Provider user ID
            status: Optional status filter
            date_from: Start date filter
            date_to: End date filter
            limit: Maximum number of results

        Returns:
            List of Visit instances
        """
        query = db.query(Visit).filter(Visit.provider_id == provider_id)

        if status:
            query = query.filter(Visit.status == status)

        if date_from:
            query = query.filter(Visit.created_at >= date_from)

        if date_to:
            query = query.filter(Visit.created_at <= date_to)

        return query.order_by(Visit.created_at.desc()).limit(limit).all()

    async def cancel_visit(
        self,
        db: Session,
        visit_id: str
    ) -> Visit:
        """
        Cancel a visit.

        Args:
            db: Database session
            visit_id: Visit ID

        Returns:
            Updated Visit instance
        """
        visit = db.query(Visit).filter(Visit.id == visit_id).first()

        if not visit:
            raise ValueError(f"Visit {visit_id} not found")

        if visit.status == VisitStatus.COMPLETED:
            raise ValueError(f"Cannot cancel completed visit")

        visit.status = VisitStatus.CANCELLED

        db.commit()
        db.refresh(visit)

        logger.info(f"Cancelled visit {visit_id}")

        return visit


# Create service instance
visit_service = VisitService()
