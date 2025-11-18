"""
Triage Engine for assessing patient urgency.
Combines rule-based and AI-based triage assessment.
"""

from typing import List, Dict, Any, Optional, Set
import logging

from src.api.schemas.previsit_schemas import (
    SymptomInput,
    TriageAssessmentResponse,
    UrgencyLevel
)

logger = logging.getLogger(__name__)


class TriageEngine:
    """
    Medical triage engine combining rule-based and AI-based assessment.

    Triage Levels:
    - Level 1 (Emergency): Life-threatening, immediate attention
    - Level 2 (Urgent): Serious, seen within 15-30 minutes
    - Level 3 (Moderate): Moderate severity, seen within 1-2 hours
    - Level 4 (Less Urgent): Minor issues, seen within 2-4 hours
    - Level 5 (Routine): Non-urgent, schedule appointment
    """

    # Red flag symptoms requiring emergency care
    RED_FLAG_SYMPTOMS = {
        "chest pain",
        "difficulty breathing",
        "severe bleeding",
        "loss of consciousness",
        "severe head injury",
        "stroke symptoms",
        "severe allergic reaction",
        "poisoning",
        "severe burns",
        "suicidal thoughts",
        "seizure",
        "severe abdominal pain"
    }

    # Symptoms suggesting urgent care
    URGENT_SYMPTOMS = {
        "high fever",
        "severe pain",
        "persistent vomiting",
        "confusion",
        "severe headache",
        "rapid heart rate",
        "shortness of breath"
    }

    def __init__(self):
        """Initialize triage engine."""
        pass

    async def assess_triage(
        self,
        symptoms: List[SymptomInput],
        vital_signs: Optional[Dict[str, Any]] = None,
        age: Optional[int] = None,
        existing_conditions: Optional[List[str]] = None
    ) -> TriageAssessmentResponse:
        """
        Assess patient triage level.

        Args:
            symptoms: List of patient symptoms
            vital_signs: Optional vital signs
            age: Patient age
            existing_conditions: List of existing medical conditions

        Returns:
            TriageAssessmentResponse: Triage assessment with level and recommendations
        """
        logger.info(f"Assessing triage for {len(symptoms)} symptoms")

        # Check for red flags
        emergency_flags = self._check_emergency_flags(symptoms, vital_signs)

        if emergency_flags:
            return self._create_emergency_response(emergency_flags)

        # Check for urgent symptoms
        urgent_flags = self._check_urgent_flags(symptoms, vital_signs, age, existing_conditions)

        if urgent_flags:
            return self._create_urgent_response(urgent_flags)

        # Assess severity score
        severity_score = self._calculate_severity_score(symptoms, vital_signs)

        # Determine triage level
        triage_level, urgency = self._determine_triage_level(
            severity_score,
            symptoms,
            age,
            existing_conditions
        )

        return self._create_triage_response(
            triage_level,
            urgency,
            severity_score,
            symptoms
        )

    def _check_emergency_flags(
        self,
        symptoms: List[SymptomInput],
        vital_signs: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Check for emergency red flags."""
        flags = []

        # Check symptom names
        for symptom in symptoms:
            symptom_lower = symptom.name.lower()

            # Check red flag symptoms
            for red_flag in self.RED_FLAG_SYMPTOMS:
                if red_flag in symptom_lower:
                    flags.append(f"{symptom.name} (severity: {symptom.severity})")
                    break

            # Severe symptoms are red flags
            if symptom.severity == "severe":
                flags.append(f"Severe {symptom.name}")

        # Check vital signs
        if vital_signs:
            # High temperature
            temp = vital_signs.get('temperature_f')
            if temp and temp >= 104:
                flags.append(f"Very high fever ({temp}°F)")

            # Blood pressure
            bp = vital_signs.get('blood_pressure', '')
            if '/' in bp:
                systolic = int(bp.split('/')[0])
                if systolic >= 180:
                    flags.append(f"Severely elevated blood pressure ({bp})")

            # Heart rate
            hr = vital_signs.get('heart_rate')
            if hr and (hr > 120 or hr < 50):
                flags.append(f"Abnormal heart rate ({hr} bpm)")

        return flags

    def _check_urgent_flags(
        self,
        symptoms: List[SymptomInput],
        vital_signs: Optional[Dict[str, Any]],
        age: Optional[int],
        existing_conditions: Optional[List[str]]
    ) -> List[str]:
        """Check for urgent care indicators."""
        flags = []

        # Check urgent symptoms
        for symptom in symptoms:
            symptom_lower = symptom.name.lower()

            for urgent in self.URGENT_SYMPTOMS:
                if urgent in symptom_lower:
                    flags.append(symptom.name)
                    break

        # Age considerations
        if age:
            if age < 2 and any("fever" in s.name.lower() for s in symptoms):
                flags.append("Fever in infant/young child")

            if age > 65 and len(symptoms) > 2:
                flags.append("Multiple symptoms in elderly patient")

        # Existing conditions
        if existing_conditions:
            high_risk_conditions = ["diabetes", "heart disease", "copd", "immunocompromised"]
            for condition in existing_conditions:
                if any(risk in condition.lower() for risk in high_risk_conditions):
                    flags.append(f"High-risk condition: {condition}")

        # Vital signs
        if vital_signs:
            temp = vital_signs.get('temperature_f')
            if temp and temp >= 102:
                flags.append(f"High fever ({temp}°F)")

        return flags

    def _calculate_severity_score(
        self,
        symptoms: List[SymptomInput],
        vital_signs: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate overall severity score (0-100).

        Higher score = more severe
        """
        score = 0.0

        # Symptom severity
        severity_weights = {"mild": 1, "moderate": 2, "severe": 3}

        for symptom in symptoms:
            score += severity_weights.get(symptom.severity, 1) * 10

        # Number of symptoms
        score += len(symptoms) * 5

        # Vital signs abnormality
        if vital_signs:
            temp = vital_signs.get('temperature_f', 0)
            if temp > 100.4:
                score += (temp - 100.4) * 3

        return min(score, 100)  # Cap at 100

    def _determine_triage_level(
        self,
        severity_score: float,
        symptoms: List[SymptomInput],
        age: Optional[int],
        existing_conditions: Optional[List[str]]
    ) -> tuple:
        """Determine triage level and urgency from severity score."""

        # Adjust for age
        if age:
            if age < 5 or age > 70:
                severity_score *= 1.2

        # Adjust for existing conditions
        if existing_conditions and len(existing_conditions) > 0:
            severity_score *= 1.1

        # Determine level
        if severity_score >= 70:
            return 2, UrgencyLevel.URGENT
        elif severity_score >= 50:
            return 3, UrgencyLevel.HIGH
        elif severity_score >= 30:
            return 4, UrgencyLevel.MODERATE
        else:
            return 5, UrgencyLevel.LOW

    def _create_emergency_response(self, flags: List[str]) -> TriageAssessmentResponse:
        """Create emergency triage response."""
        return TriageAssessmentResponse(
            triage_level=1,
            urgency=UrgencyLevel.EMERGENCY,
            recommended_action="Call 911 immediately or go to the nearest emergency room",
            time_to_see_provider="Immediate",
            rationale="Emergency symptoms detected requiring immediate medical attention",
            emergency_flags=flags
        )

    def _create_urgent_response(self, flags: List[str]) -> TriageAssessmentResponse:
        """Create urgent care response."""
        return TriageAssessmentResponse(
            triage_level=2,
            urgency=UrgencyLevel.URGENT,
            recommended_action="Seek urgent care or emergency department within 1-2 hours",
            time_to_see_provider="Within 1-2 hours",
            rationale="Urgent symptoms require prompt medical evaluation",
            emergency_flags=flags
        )

    def _create_triage_response(
        self,
        triage_level: int,
        urgency: UrgencyLevel,
        severity_score: float,
        symptoms: List[SymptomInput]
    ) -> TriageAssessmentResponse:
        """Create standard triage response."""

        time_recommendations = {
            3: "Within 2-4 hours",
            4: "Within 24 hours",
            5: "Schedule routine appointment within 3-7 days"
        }

        action_recommendations = {
            3: "Visit urgent care or contact your healthcare provider today",
            4: "Contact your healthcare provider to schedule appointment within 24 hours",
            5: "Schedule a routine appointment with your healthcare provider"
        }

        return TriageAssessmentResponse(
            triage_level=triage_level,
            urgency=urgency,
            recommended_action=action_recommendations.get(triage_level, "Consult healthcare provider"),
            time_to_see_provider=time_recommendations.get(triage_level, "Within 24-48 hours"),
            rationale=f"Based on symptom severity assessment (score: {severity_score:.1f}/100) and clinical guidelines",
            emergency_flags=[]
        )


# Global instance
triage_engine = TriageEngine()
