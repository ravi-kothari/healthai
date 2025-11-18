"""
Symptom Analyzer service using Azure OpenAI.
Analyzes patient symptoms and provides medical insights.
"""

from typing import List, Dict, Any, Optional
import json
import logging

from src.api.services.ai.openai_service import openai_service
from src.api.schemas.previsit_schemas import (
    SymptomInput,
    SymptomAnalysisResponse,
    UrgencyLevel,
    QuestionnaireQuestion,
    QuestionType
)

logger = logging.getLogger(__name__)


class SymptomAnalyzer:
    """
    Analyzes patient symptoms using AI.

    Uses Azure OpenAI (or mock service) to:
    - Analyze symptom combinations
    - Assess urgency and severity
    - Suggest possible conditions
    - Provide recommendations
    """

    def __init__(self):
        """Initialize symptom analyzer."""
        self.openai = openai_service

    async def analyze_symptoms(
        self,
        symptoms: List[SymptomInput],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> SymptomAnalysisResponse:
        """
        Analyze patient symptoms and provide assessment.

        Args:
            symptoms: List of patient symptoms
            patient_context: Optional patient context (age, conditions, etc.)

        Returns:
            SymptomAnalysisResponse: Comprehensive symptom analysis

        Example:
            >>> symptoms = [
            ...     SymptomInput(name="Headache", severity="moderate", duration="2 days"),
            ...     SymptomInput(name="Fever", severity="mild", duration="1 day")
            ... ]
            >>> result = await analyzer.analyze_symptoms(symptoms)
        """
        logger.info(f"Analyzing {len(symptoms)} symptoms")

        # Build prompt for analysis
        prompt = self._build_analysis_prompt(symptoms, patient_context)

        # Get AI analysis
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        try:
            response = await self.openai.chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for medical accuracy
                response_format={"type": "json_object"}
            )

            # Parse response
            analysis_data = json.loads(response['content'])

            # Convert to response model
            return SymptomAnalysisResponse(**analysis_data)

        except Exception as e:
            logger.error(f"Error analyzing symptoms: {e}")
            # Return safe default analysis
            return self._get_default_analysis(symptoms)

    async def generate_questionnaire(
        self,
        chief_complaint: str,
        symptoms: Optional[List[str]] = None
    ) -> List[QuestionnaireQuestion]:
        """
        Generate a dynamic questionnaire based on chief complaint.

        Args:
            chief_complaint: Main complaint/reason for visit
            symptoms: Optional list of known symptoms

        Returns:
            List[QuestionnaireQuestion]: List of relevant questions

        Example:
            >>> questions = await analyzer.generate_questionnaire(
            ...     chief_complaint="Headache and fever"
            ... )
        """
        logger.info(f"Generating questionnaire for: {chief_complaint}")

        prompt = self._build_questionnaire_prompt(chief_complaint, symptoms)

        messages = [
            {
                "role": "system",
                "content": "You are a medical questionnaire generator. Create relevant, focused questions to gather information about the patient's condition. Return questions in JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        try:
            response = await self.openai.chat_completion(
                messages=messages,
                temperature=0.5,
                response_format={"type": "json_object"}
            )

            logger.debug(f"OpenAI response for questionnaire: {response['content'][:200]}")
            data = json.loads(response['content'])
            logger.debug(f"Parsed data keys: {data.keys()}")
            questions = [QuestionnaireQuestion(**q) for q in data.get('questions', [])]

            return questions

        except Exception as e:
            logger.error(f"Error generating questionnaire: {e}", exc_info=True)
            return self._get_default_questionnaire(chief_complaint)

    def _get_system_prompt(self) -> str:
        """Get system prompt for symptom analysis."""
        return """You are an AI medical assistant specializing in symptom analysis and triage.

Your role is to:
1. Analyze patient symptoms objectively
2. Assess urgency and severity
3. Suggest possible conditions (differential diagnosis)
4. Provide clear recommendations
5. Identify red flags that require immediate attention

Important guidelines:
- You are assisting in triage, not providing diagnoses
- Always err on the side of caution
- Recommend professional medical evaluation when appropriate
- Be clear about emergency situations
- Use plain language patients can understand

Return your analysis in JSON format with these fields:
- urgency: (low/moderate/high/urgent/emergency)
- severity: (mild/moderate/severe)
- triage_level: (1-5, where 1=emergency, 5=routine)
- chief_complaint: (brief summary)
- summary: (detailed analysis)
- possible_conditions: (list of possible conditions)
- recommendations: (list of specific actions)
- red_flags: (warning signs to watch for)
- follow_up: (when to seek care)"""

    def _build_analysis_prompt(
        self,
        symptoms: List[SymptomInput],
        patient_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for symptom analysis."""
        prompt_parts = ["Please analyze the following symptoms:\n"]

        for i, symptom in enumerate(symptoms, 1):
            prompt_parts.append(f"{i}. {symptom.name}")
            prompt_parts.append(f"   - Severity: {symptom.severity}")
            prompt_parts.append(f"   - Duration: {symptom.duration}")
            if symptom.description:
                prompt_parts.append(f"   - Details: {symptom.description}")

        if patient_context:
            prompt_parts.append("\nPatient Context:")
            if patient_context.get('age'):
                prompt_parts.append(f"- Age: {patient_context['age']}")
            if patient_context.get('existing_conditions'):
                prompt_parts.append(f"- Existing Conditions: {', '.join(patient_context['existing_conditions'])}")
            if patient_context.get('vital_signs'):
                prompt_parts.append(f"- Vital Signs: {json.dumps(patient_context['vital_signs'])}")

        prompt_parts.append("\nProvide a comprehensive analysis in JSON format.")

        return "\n".join(prompt_parts)

    def _build_questionnaire_prompt(
        self,
        chief_complaint: str,
        symptoms: Optional[List[str]]
    ) -> str:
        """Build prompt for questionnaire generation."""
        prompt = f"Chief Complaint: {chief_complaint}\n"

        if symptoms:
            prompt += f"Known Symptoms: {', '.join(symptoms)}\n"

        prompt += "\nGenerate 4-6 relevant questions to gather more information. "
        prompt += "Include questions about severity, duration, triggers, and associated symptoms. "
        prompt += "Return in JSON format with 'questions' array containing objects with: id, type, question, options (if applicable), required."

        return prompt

    def _get_default_analysis(self, symptoms: List[SymptomInput]) -> SymptomAnalysisResponse:
        """Return safe default analysis when AI fails."""
        return SymptomAnalysisResponse(
            urgency=UrgencyLevel.MODERATE,
            severity="moderate",
            triage_level=3,
            chief_complaint=", ".join([s.name for s in symptoms]),
            summary="Please consult with a healthcare provider for proper evaluation of your symptoms.",
            possible_conditions=["Requires professional evaluation"],
            recommendations=[
                "Monitor your symptoms",
                "Stay hydrated",
                "Get adequate rest",
                "Consult a healthcare provider"
            ],
            red_flags=[
                "Severe or worsening symptoms",
                "Difficulty breathing",
                "Chest pain",
                "High fever (>103°F)"
            ],
            follow_up="Schedule an appointment with your healthcare provider"
        )

    def _get_default_questionnaire(self, chief_complaint: str) -> List[QuestionnaireQuestion]:
        """Return default questionnaire when AI fails."""
        return [
            QuestionnaireQuestion(
                id="q1",
                type=QuestionType.SCALE,
                question=f"On a scale of 1-10, how severe is your {chief_complaint}?",
                options=list(range(1, 11)),
                required=True
            ),
            QuestionnaireQuestion(
                id="q2",
                type=QuestionType.SELECT,
                question="When did your symptoms start?",
                options=["Less than 24 hours ago", "1-3 days ago", "4-7 days ago", "More than a week ago"],
                required=True
            ),
            QuestionnaireQuestion(
                id="q3",
                type=QuestionType.TEXT,
                question="Please describe any additional symptoms or details.",
                required=False
            )
        ]


# Global instance
symptom_analyzer = SymptomAnalyzer()
