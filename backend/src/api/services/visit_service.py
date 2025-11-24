"""
Visit Management Service.
Handles clinical visit sessions, SOAP notes, and visit lifecycle.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.api.models.visit import Visit, VisitStatus, VisitType
from src.api.models.patient import Patient
from src.api.models.user import User
from src.api.models.appointment import Appointment
from src.api.models.careprep import CarePrepResponse

logger = logging.getLogger(__name__)


class VisitService:
    """Service for managing clinical visits."""

    async def create_visit_from_appointment(
        self,
        db: Session,
        appointment_id: str,
        provider_id: str
    ) -> Visit:
        """
        Create a new visit from an appointment with CarePrep data auto-populated.

        Args:
            db: Database session
            appointment_id: Appointment ID
            provider_id: Provider (doctor/nurse) user ID

        Returns:
            Visit model instance with CarePrep data in subjective field
        """
        # Verify appointment exists
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")

        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
        if not patient:
            raise ValueError(f"Patient {appointment.patient_id} not found")

        # Verify provider exists and has appropriate role
        provider = db.query(User).filter(User.id == provider_id).first()
        if not provider:
            raise ValueError(f"Provider {provider_id} not found")

        if provider.role not in ["doctor", "nurse", "admin", "staff"]:
            raise ValueError(f"User {provider_id} is not a provider")

        # Get CarePrep response data
        careprep_response = db.query(CarePrepResponse).filter(
            CarePrepResponse.appointment_id == appointment_id
        ).first()

        # Build subjective notes from CarePrep data
        subjective_notes = self._build_subjective_from_careprep(appointment, careprep_response)

        # Create visit
        visit = Visit(
            patient_id=appointment.patient_id,
            provider_id=provider_id,
            appointment_id=appointment_id,
            visit_type=self._map_appointment_type_to_visit_type(appointment.appointment_type),
            status=VisitStatus.IN_PROGRESS,
            chief_complaint=appointment.chief_complaint,
            reason_for_visit=appointment.notes,
            scheduled_start=appointment.scheduled_start,
            actual_start=datetime.now(timezone.utc),
            subjective=subjective_notes
        )

        db.add(visit)
        db.commit()
        db.refresh(visit)

        logger.info(f"Created visit {visit.id} from appointment {appointment_id}")

        return visit

    def _map_appointment_type_to_visit_type(self, appointment_type) -> VisitType:
        """Map appointment type to visit type."""
        mapping = {
            "initial_consultation": VisitType.INITIAL,
            "follow_up": VisitType.FOLLOW_UP,
            "urgent_care": VisitType.URGENT,
            "annual_checkup": VisitType.ROUTINE,
            "telemedicine": VisitType.TELEHEALTH,
        }
        return mapping.get(appointment_type.value if hasattr(appointment_type, 'value') else appointment_type, VisitType.ROUTINE)

    def _build_subjective_from_careprep(self, appointment, careprep_response: Optional[CarePrepResponse]) -> str:
        """Build subjective notes from CarePrep data."""
        sections = []

        # Add chief complaint
        if appointment.chief_complaint:
            sections.append(f"Chief Complaint: {appointment.chief_complaint}\n")

        if careprep_response:
            # Add symptom checker data
            if careprep_response.symptom_checker_data:
                sections.append("Symptom Information (from CarePrep):")
                symptom_data = careprep_response.symptom_checker_data

                if isinstance(symptom_data, dict):
                    if symptom_data.get('symptoms'):
                        sections.append("\nReported Symptoms:")
                        for symptom in symptom_data['symptoms']:
                            if isinstance(symptom, dict):
                                name = symptom.get('name', 'Unknown')
                                severity = symptom.get('severity', 'N/A')
                                duration = symptom.get('duration', 'N/A')
                                sections.append(f"- {name} (Severity: {severity}, Duration: {duration})")
                            else:
                                sections.append(f"- {symptom}")

                    if symptom_data.get('analysis'):
                        sections.append(f"\nPatient-Reported Analysis: {symptom_data['analysis']}")

                sections.append("")

            # Add medical history data
            if careprep_response.medical_history_data:
                sections.append("\nMedical History Updates (from CarePrep):")
                history_data = careprep_response.medical_history_data

                if isinstance(history_data, dict):
                    if history_data.get('medications'):
                        sections.append("\nCurrent Medications:")
                        for med in history_data['medications']:
                            if isinstance(med, dict):
                                sections.append(f"- {med.get('name', 'Unknown')} ({med.get('dosage', 'N/A')})")
                            else:
                                sections.append(f"- {med}")

                    if history_data.get('allergies'):
                        sections.append("\nAllergies:")
                        for allergy in history_data['allergies']:
                            sections.append(f"- {allergy}")

                    if history_data.get('conditions'):
                        sections.append("\nChronic Conditions:")
                        for condition in history_data['conditions']:
                            sections.append(f"- {condition}")

                    if history_data.get('recent_changes'):
                        sections.append(f"\nRecent Health Changes: {history_data['recent_changes']}")

                sections.append("")

        if not sections:
            sections.append("Patient presents for scheduled appointment.")

        return "\n".join(sections)

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
        visit.actual_start = datetime.now(timezone.utc)

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
        visit.actual_end = datetime.now(timezone.utc)

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
