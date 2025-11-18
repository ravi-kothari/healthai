"""
Appointment Context Builder Service.

Aggregates patient data from multiple sources to create comprehensive
appointment context for healthcare providers.

Data Sources:
- PostgreSQL database (demographics, patient record)
- FHIR server (conditions, medications, allergies, observations)
- PreVisit.ai responses (symptom analysis, triage)
- Recent visit history
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.api.models.patient import Patient
from src.api.models.user import User
from src.api.services.fhir.fhir_client import fhir_client

logger = logging.getLogger(__name__)


class AppointmentContextBuilder:
    """
    Builds comprehensive appointment context for providers.

    Combines data from multiple sources:
    - Patient demographics
    - Medical history (FHIR)
    - Current medications
    - Known allergies
    - Recent vitals
    - PreVisit responses
    - Visit history
    """

    def __init__(self):
        """Initialize context builder."""
        self.fhir = fhir_client

    async def build_context(
        self,
        patient_id: str,
        db: Session,
        include_fhir: bool = True,
        include_previsit: bool = True
    ) -> Dict[str, Any]:
        """
        Build comprehensive appointment context for a patient.

        Args:
            patient_id: Patient ID (UUID)
            db: Database session
            include_fhir: Whether to include FHIR data
            include_previsit: Whether to include PreVisit.ai data

        Returns:
            dict: Comprehensive appointment context
        """
        logger.info(f"Building appointment context for patient {patient_id}")

        context = {
            "patient_id": patient_id,
            "generated_at": datetime.utcnow().isoformat(),
            "data_sources": []
        }

        # 1. Get patient demographics from database
        demographics = await self._get_demographics(patient_id, db)
        if demographics:
            context["demographics"] = demographics
            context["data_sources"].append("database")

        # 2. Get FHIR data if enabled
        if include_fhir and demographics:
            fhir_data = await self._get_fhir_data(patient_id, demographics.get("mrn"))
            if fhir_data:
                context["medical_history"] = fhir_data
                context["data_sources"].append("fhir")

        # 3. Get PreVisit.ai data if enabled
        if include_previsit:
            previsit_data = await self._get_previsit_data(patient_id, db)
            if previsit_data:
                context["previsit"] = previsit_data
                context["data_sources"].append("previsit")

        # 4. Generate summary
        context["summary"] = self._generate_summary(context)

        logger.info(f"Context built with {len(context['data_sources'])} data sources")
        return context

    async def _get_demographics(
        self,
        patient_id: str,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        Get patient demographics from database.

        Args:
            patient_id: Patient UUID
            db: Database session

        Returns:
            dict: Patient demographics
        """
        try:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if not patient:
                logger.warning(f"Patient not found: {patient_id}")
                return None

            # Get associated user
            user = db.query(User).filter(User.id == patient.user_id).first()

            demographics = {
                "patient_id": str(patient.id),
                "mrn": patient.mrn,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                "age": patient.age if hasattr(patient, 'age') else None,
                "gender": patient.gender,
                "phone": None,  # Phone not in Patient model
                "email": user.email if user else None,
                "address": {
                    "street": patient.address,
                    "city": patient.city,
                    "state": patient.state,
                    "zip_code": patient.zip_code
                } if patient.address else None,
                "emergency_contact": {
                    "name": patient.emergency_contact_name,
                    "phone": patient.emergency_contact_phone
                } if patient.emergency_contact_name else None
            }

            return demographics

        except Exception as e:
            logger.error(f"Error fetching demographics: {e}")
            return None

    async def _get_fhir_data(
        self,
        patient_id: str,
        mrn: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Get medical history from FHIR server.

        Args:
            patient_id: Patient UUID
            mrn: Medical Record Number

        Returns:
            dict: FHIR medical data
        """
        try:
            # Search for FHIR patient by MRN
            if mrn:
                fhir_patients = self.fhir.search_patients(identifier=mrn)
                if fhir_patients:
                    fhir_patient_id = fhir_patients[0]['id']
                else:
                    logger.info(f"No FHIR patient found for MRN {mrn}")
                    return None
            else:
                logger.warning("No MRN available for FHIR lookup")
                return None

            # Get comprehensive summary
            summary = self.fhir.get_patient_summary(fhir_patient_id)

            # Transform to appointment context format
            fhir_data = {
                "conditions": self._format_conditions(summary.get('conditions', [])),
                "medications": self._format_medications(summary.get('medications', [])),
                "allergies": self._format_allergies(summary.get('allergies', [])),
                "recent_vitals": self._format_observations(summary.get('observations', []))
            }

            return fhir_data

        except Exception as e:
            logger.error(f"Error fetching FHIR data: {e}")
            return None

    async def _get_previsit_data(
        self,
        patient_id: str,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        Get PreVisit.ai responses for this patient.

        Args:
            patient_id: Patient UUID
            db: Database session

        Returns:
            dict: PreVisit.ai data
        """
        try:
            # TODO: Query previsit_responses table when implemented
            # For now, return placeholder
            logger.info(f"PreVisit data lookup for {patient_id} (not yet implemented)")
            return {
                "has_responses": False,
                "last_response_date": None,
                "chief_complaint": None,
                "triage_level": None,
                "urgency": None
            }

        except Exception as e:
            logger.error(f"Error fetching PreVisit data: {e}")
            return None

    def _format_conditions(self, conditions: List[Dict]) -> List[Dict[str, Any]]:
        """Format FHIR conditions for appointment context."""
        formatted = []
        for cond in conditions:
            try:
                coding = cond.get('code', {}).get('coding', [{}])[0]
                status = cond.get('clinicalStatus', {}).get('coding', [{}])[0].get('code', 'unknown')

                formatted.append({
                    "name": coding.get('display', 'Unknown condition'),
                    "code": coding.get('code'),
                    "code_system": coding.get('system'),
                    "status": status,
                    "recorded_date": cond.get('recordedDate'),
                    "is_active": status == 'active'
                })
            except Exception as e:
                logger.warning(f"Error formatting condition: {e}")
                continue

        return formatted

    def _format_medications(self, medications: List[Dict]) -> List[Dict[str, Any]]:
        """Format FHIR medications for appointment context."""
        formatted = []
        for med in medications:
            try:
                coding = med.get('medicationCodeableConcept', {}).get('coding', [{}])[0]
                status = med.get('status', 'unknown')

                formatted.append({
                    "name": coding.get('display', 'Unknown medication'),
                    "code": coding.get('code'),
                    "status": status,
                    "is_active": status == 'active'
                })
            except Exception as e:
                logger.warning(f"Error formatting medication: {e}")
                continue

        return formatted

    def _format_allergies(self, allergies: List[Dict]) -> List[Dict[str, Any]]:
        """Format FHIR allergies for appointment context."""
        formatted = []
        for allergy in allergies:
            try:
                coding = allergy.get('code', {}).get('coding', [{}])[0]
                criticality = allergy.get('criticality', 'unable-to-assess')

                formatted.append({
                    "allergen": coding.get('display', 'Unknown allergen'),
                    "code": coding.get('code'),
                    "criticality": criticality,
                    "is_high_risk": criticality == 'high'
                })
            except Exception as e:
                logger.warning(f"Error formatting allergy: {e}")
                continue

        return formatted

    def _format_observations(self, observations: List[Dict]) -> List[Dict[str, Any]]:
        """Format FHIR observations (vitals) for appointment context."""
        formatted = []
        for obs in observations[:10]:  # Limit to 10 most recent
            try:
                coding = obs.get('code', {}).get('coding', [{}])[0]
                value_quantity = obs.get('valueQuantity', {})

                formatted.append({
                    "name": coding.get('display', 'Unknown observation'),
                    "code": coding.get('code'),
                    "value": value_quantity.get('value'),
                    "unit": value_quantity.get('unit'),
                    "date": obs.get('effectiveDateTime'),
                    "status": obs.get('status')
                })
            except Exception as e:
                logger.warning(f"Error formatting observation: {e}")
                continue

        return formatted

    def _generate_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate high-level summary from context data.

        Args:
            context: Full appointment context

        Returns:
            dict: Summary highlights
        """
        summary = {
            "has_data": len(context.get("data_sources", [])) > 0,
            "data_completeness": len(context.get("data_sources", [])) / 3 * 100,  # Out of 3 sources
            "alerts": [],
            "highlights": []
        }

        # Check for high-risk allergies
        allergies = context.get("medical_history", {}).get("allergies", [])
        high_risk_allergies = [a for a in allergies if a.get("is_high_risk")]
        if high_risk_allergies:
            summary["alerts"].append({
                "type": "allergy",
                "severity": "high",
                "message": f"HIGH-RISK ALLERGIES: {', '.join([a['allergen'] for a in high_risk_allergies])}"
            })

        # Check for active chronic conditions
        conditions = context.get("medical_history", {}).get("conditions", [])
        active_conditions = [c for c in conditions if c.get("is_active")]
        if active_conditions:
            summary["highlights"].append({
                "type": "conditions",
                "count": len(active_conditions),
                "items": [c["name"] for c in active_conditions[:3]]  # Top 3
            })

        # Check for active medications
        medications = context.get("medical_history", {}).get("medications", [])
        active_meds = [m for m in medications if m.get("is_active")]
        if active_meds:
            summary["highlights"].append({
                "type": "medications",
                "count": len(active_meds),
                "items": [m["name"] for m in active_meds[:5]]  # Top 5
            })

        # Check for PreVisit triage
        previsit = context.get("previsit", {})
        if previsit and previsit.get("has_responses"):
            urgency = previsit.get("urgency")
            if urgency in ["emergency", "urgent"]:
                summary["alerts"].append({
                    "type": "previsit_triage",
                    "severity": "high" if urgency == "emergency" else "medium",
                    "message": f"PreVisit Triage: {urgency.upper()}"
                })

        return summary


# Global instance
context_builder = AppointmentContextBuilder()
