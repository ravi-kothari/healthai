"""
Data transformation service for patient-facing data.

This service implements the "API firewall" pattern, transforming clinical data
into patient-friendly language while hiding sensitive metrics and risk scores.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from src.api.schemas.unified_schemas import (
    PatientSummaryResponse,
    PatientBasicInfo,
    PatientSymptomSummary,
    DiscussionTopic,
    MedicationToConfirm,
    AllergyInfo,
    AppointmentPrepItem
)
from src.api.schemas.appoint_ready_schemas import (
    AppointmentContextResponse,
    RiskScore,
    CareGap
)
from src.api.schemas.previsit_schemas import SymptomAnalysisResponse

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    Transforms provider-facing clinical data into patient-friendly summaries.

    Key Principles:
    1. Hide clinical risk scores and detailed metrics
    2. Convert medical terminology to plain language
    3. Focus on actionable items for patients
    4. Maintain safety by always showing allergies
    5. Provide encouragement and clear next steps
    """

    def transform_to_patient_summary(
        self,
        patient_id: str,
        provider_context: Optional[AppointmentContextResponse] = None,
        symptom_analysis: Optional[SymptomAnalysisResponse] = None,
        risk_scores: Optional[List[RiskScore]] = None,
        care_gaps: Optional[List[CareGap]] = None,
        appointment_date: Optional[str] = None
    ) -> PatientSummaryResponse:
        """
        Transform comprehensive clinical data into patient-facing summary.

        Args:
            patient_id: Patient identifier
            provider_context: Full clinical context from Appoint-Ready
            symptom_analysis: PreVisit.ai symptom analysis
            risk_scores: Clinical risk assessments
            care_gaps: Identified care gaps
            appointment_date: Upcoming appointment date

        Returns:
            PatientSummaryResponse with patient-friendly data
        """
        logger.info(f"Transforming data for patient {patient_id}")

        # Extract basic patient info
        patient_info = self._extract_patient_info(provider_context)

        # Transform symptom analysis to patient-friendly format
        symptoms = self._transform_symptoms(symptom_analysis)

        # Convert risk scores to discussion topics
        topics_to_discuss = self._risk_scores_to_topics(risk_scores)

        # Add care gaps to discussion topics
        if care_gaps:
            topics_to_discuss.extend(self._care_gaps_to_topics(care_gaps))

        # Extract medications to confirm
        medications = self._extract_medications(provider_context)

        # Extract allergies (always show for safety)
        allergies = self._extract_allergies(provider_context)

        # Create appointment prep checklist
        appointment_prep = self._create_prep_checklist(care_gaps)

        # Generate personalized message
        message = self._generate_team_message(
            symptoms=symptom_analysis,
            has_risks=(len(topics_to_discuss) > 0),
            has_gaps=(len(appointment_prep) > 0)
        )

        return PatientSummaryResponse(
            patient_id=patient_id,
            generated_at=datetime.utcnow().isoformat() + "Z",
            appointment_date=appointment_date,
            patient_info=patient_info,
            symptoms=symptoms,
            topics_to_discuss=topics_to_discuss,
            medications_to_confirm=medications,
            allergies=allergies,
            appointment_prep=appointment_prep,
            message_from_team=message
        )

    def _extract_patient_info(
        self,
        context: Optional[Any]
    ) -> PatientBasicInfo:
        """Extract basic patient information."""
        if not context:
            return PatientBasicInfo(
                first_name="Patient",
                last_name="",
                age=None
            )

        # Handle both dict and Pydantic model
        if isinstance(context, dict):
            demo = context.get('demographics', {})
            if not demo:
                return PatientBasicInfo(
                    first_name="Patient",
                    last_name="",
                    age=None
                )
            return PatientBasicInfo(
                first_name=demo.get('first_name', 'Patient'),
                last_name=demo.get('last_name', ''),
                date_of_birth=demo.get('date_of_birth'),
                age=demo.get('age')
            )
        else:
            # Pydantic model
            if not context.demographics:
                return PatientBasicInfo(
                    first_name="Patient",
                    last_name="",
                    age=None
                )
            demo = context.demographics
            return PatientBasicInfo(
                first_name=demo.first_name,
                last_name=demo.last_name,
                date_of_birth=demo.date_of_birth,
                age=demo.age
            )

    def _transform_symptoms(
        self,
        analysis: Optional[SymptomAnalysisResponse]
    ) -> Optional[PatientSymptomSummary]:
        """
        Transform symptom analysis into patient-friendly summary.

        Hides triage levels and clinical metrics, shows only actionable info.
        """
        if not analysis:
            return None

        # Convert clinical urgency to patient-friendly message
        urgency_messages = {
            "emergency": "Seek immediate medical attention. Call 911 or go to the nearest emergency room.",
            "urgent": "Please see a healthcare provider as soon as possible, ideally today.",
            "high": "Your appointment is scheduled soon. Please arrive on time.",
            "moderate": "Your appointment is scheduled. Please arrive 15 minutes early.",
            "low": "Looking forward to seeing you at your scheduled appointment."
        }

        urgency_message = urgency_messages.get(
            analysis.urgency.value if hasattr(analysis.urgency, 'value') else analysis.urgency,
            "Your appointment is scheduled. Please arrive 15 minutes early."
        )

        # Extract actionable next steps from recommendations
        next_steps = []
        for rec in analysis.recommendations[:3]:  # Limit to top 3
            # Convert clinical recommendations to patient-friendly language
            patient_friendly = self._make_patient_friendly(rec)
            next_steps.append(patient_friendly)

        # Add standard prep items
        next_steps.append("Bring a list of current medications and supplements")
        next_steps.append("Write down any questions you have for your provider")

        return PatientSymptomSummary(
            chief_complaint=analysis.chief_complaint,
            urgency_message=urgency_message,
            next_steps=next_steps
        )

    def _risk_scores_to_topics(
        self,
        risk_scores: Optional[List[Any]]
    ) -> List[DiscussionTopic]:
        """
        Convert clinical risk scores to patient-friendly discussion topics.

        CRITICAL: This hides the actual risk scores and categories,
        showing only that "we'll discuss your [condition] management"
        """
        if not risk_scores:
            return []

        topics = []
        for idx, risk in enumerate(risk_scores):
            # Handle both dict and Pydantic model
            if isinstance(risk, dict):
                score = risk.get('score', 0)
                risk_type = risk.get('risk_type', 'general')
            else:
                score = risk.score
                risk_type = risk.risk_type

            # Skip low-risk items (score < 20)
            if score < 20:
                continue

            # Map risk types to patient-friendly language
            topic_text = self._risk_type_to_discussion_text(risk_type)

            # Determine priority based on score (hidden from patient)
            if score >= 60:
                priority = "high"
                icon = "alert-circle"
            elif score >= 40:
                priority = "high"
                icon = "heart"
            else:
                priority = "medium"
                icon = "clipboard"

            topics.append(DiscussionTopic(
                id=f"risk-{risk_type}-{idx}",
                text=topic_text,
                priority=priority,
                icon=icon
            ))

        return topics

    def _care_gaps_to_topics(
        self,
        care_gaps: Optional[List[Any]]
    ) -> List[DiscussionTopic]:
        """Convert high-priority care gaps to discussion topics."""
        if not care_gaps:
            return []

        topics = []

        for idx, gap in enumerate(care_gaps):
            # Handle both dict and Pydantic model
            if isinstance(gap, dict):
                priority = gap.get('priority', 'low')
                description = gap.get('description', 'health screening')
            else:
                priority = gap.priority
                description = gap.description

            # Only add high-priority gaps as discussion topics
            if priority != "high":
                continue

            topics.append(DiscussionTopic(
                id=f"gap-{idx}",
                text=f"Planning your {description.lower()}",
                priority=priority,
                icon="calendar"
            ))

        return topics

    def _extract_medications(
        self,
        context: Optional[Any]
    ) -> List[MedicationToConfirm]:
        """Extract active medications for patient confirmation."""
        if not context:
            return []

        medications = []

        # Handle dict
        if isinstance(context, dict):
            medical_history = context.get('medical_history', {})
            if not medical_history:
                return []

            meds_list = medical_history.get('medications', [])
            for med in meds_list:
                if isinstance(med, dict):
                    if not med.get('is_active', False):
                        continue
                    medications.append(MedicationToConfirm(
                        id=f"med-{med.get('name', 'unknown').replace(' ', '-').lower()}",
                        name=med.get('name', 'Unknown'),
                        instructions=None
                    ))
                else:
                    # Pydantic model
                    if not med.is_active:
                        continue
                    medications.append(MedicationToConfirm(
                        id=f"med-{med.name.replace(' ', '-').lower()}",
                        name=med.name,
                        instructions=None
                    ))
        else:
            # Pydantic model
            if not context.medical_history:
                return []

            for med in context.medical_history.medications:
                if not med.is_active:
                    continue
                medications.append(MedicationToConfirm(
                    id=f"med-{med.name.replace(' ', '-').lower()}",
                    name=med.name,
                    instructions=None
                ))

        return medications

    def _extract_allergies(
        self,
        context: Optional[Any]
    ) -> List[AllergyInfo]:
        """
        Extract allergies for patient review.

        ALWAYS show allergies for patient safety.
        """
        if not context:
            return []

        allergies = []

        # Handle dict
        if isinstance(context, dict):
            medical_history = context.get('medical_history', {})
            if not medical_history:
                return []

            allergies_list = medical_history.get('allergies', [])
            for allergy in allergies_list:
                if isinstance(allergy, dict):
                    # Map criticality to severity
                    severity_map = {
                        "low": "mild",
                        "medium": "moderate",
                        "high": "severe"
                    }
                    criticality = allergy.get('criticality', 'unknown')
                    severity = severity_map.get(
                        criticality.lower() if isinstance(criticality, str) else criticality,
                        criticality
                    )

                    allergies.append(AllergyInfo(
                        allergen=allergy.get('allergen', 'Unknown'),
                        severity=severity
                    ))
                else:
                    # Pydantic model
                    severity_map = {
                        "low": "mild",
                        "medium": "moderate",
                        "high": "severe"
                    }
                    severity = severity_map.get(
                        allergy.criticality.lower(),
                        allergy.criticality
                    )
                    allergies.append(AllergyInfo(
                        allergen=allergy.allergen,
                        severity=severity
                    ))
        else:
            # Pydantic model
            if not context.medical_history:
                return []

            for allergy in context.medical_history.allergies:
                severity_map = {
                    "low": "mild",
                    "medium": "moderate",
                    "high": "severe"
                }
                severity = severity_map.get(
                    allergy.criticality.lower(),
                    allergy.criticality
                )
                allergies.append(AllergyInfo(
                    allergen=allergy.allergen,
                    severity=severity
                ))

        return allergies

    def _create_prep_checklist(
        self,
        care_gaps: Optional[List[Any]]
    ) -> List[AppointmentPrepItem]:
        """Create appointment preparation checklist from care gaps."""
        if not care_gaps:
            return []

        prep_items = []
        for idx, gap in enumerate(care_gaps):
            # Handle both dict and Pydantic model
            if isinstance(gap, dict):
                gap_type = gap.get('gap_type', 'document')
                description = gap.get('description', 'health item')
                overdue = gap.get('overdue', False)
                recommendation = gap.get('recommendation', description)
                due_date = gap.get('due_date')
            else:
                gap_type = gap.gap_type
                description = gap.description
                overdue = gap.overdue
                recommendation = gap.recommendation
                due_date = gap.due_date

            # Map gap types to categories
            category_map = {
                "screening": "screening",
                "vaccination": "vaccination",
                "follow-up": "document",
                "lab": "screening"
            }
            category = category_map.get(gap_type, "document")

            # Create patient-friendly text
            if overdue:
                text = f"Schedule: {description}"
            else:
                text = recommendation

            prep_items.append(AppointmentPrepItem(
                id=f"prep-{idx}",
                category=category,
                text=text,
                completed=False,
                due_date=due_date
            ))

        return prep_items

    def _generate_team_message(
        self,
        symptoms: Optional[SymptomAnalysisResponse],
        has_risks: bool,
        has_gaps: bool
    ) -> str:
        """Generate personalized message from care team."""
        messages = []

        if symptoms:
            messages.append(
                "Our team has reviewed your recent symptoms and we're prepared "
                "to address your concerns."
            )

        if has_risks or has_gaps:
            messages.append(
                "We've identified some important topics to discuss during your visit "
                "to help you stay healthy."
            )

        messages.append(
            "We look forward to seeing you and are here to answer any questions you may have!"
        )

        return " ".join(messages)

    def _risk_type_to_discussion_text(self, risk_type: str) -> str:
        """Convert risk type to patient-friendly discussion text."""
        discussion_map = {
            "cardiovascular": "Discussing your heart health and blood pressure",
            "diabetes": "Reviewing your diabetes management plan",
            "fall": "Talking about fall prevention and safety",
            "obesity": "Discussing healthy lifestyle and weight management",
            "copd": "Reviewing your breathing and lung health",
            "kidney": "Discussing your kidney function",
            "osteoporosis": "Talking about bone health"
        }

        return discussion_map.get(
            risk_type.lower(),
            f"Reviewing your {risk_type} health"
        )

    def _make_patient_friendly(self, clinical_text: str) -> str:
        """
        Convert clinical language to patient-friendly language.

        Examples:
        - "Monitor vitals" → "Track your blood pressure and temperature at home"
        - "Increase hydration" → "Drink plenty of water throughout the day"
        - "Schedule follow-up" → "Make a follow-up appointment"
        """
        replacements = {
            "monitor vitals": "track your blood pressure and temperature at home",
            "increase hydration": "drink plenty of water throughout the day",
            "schedule follow-up": "make a follow-up appointment",
            "seek immediate medical attention": "go to the emergency room",
            "take prescribed medications": "take your medications as directed",
            "avoid strenuous activity": "take it easy and rest",
            "maintain bed rest": "rest in bed",
        }

        lower_text = clinical_text.lower()
        for clinical, friendly in replacements.items():
            if clinical in lower_text:
                return friendly.capitalize()

        return clinical_text


# Global singleton instance
data_transformer = DataTransformer()
