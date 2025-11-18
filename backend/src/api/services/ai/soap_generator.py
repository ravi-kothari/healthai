"""
SOAP Notes Generator Service.
Converts clinical visit transcriptions into structured SOAP notes using AI.
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

from src.api.services.ai.openai_service import openai_service

logger = logging.getLogger(__name__)


class SOAPGeneratorService:
    """Service for generating SOAP notes from transcriptions using AI."""

    def __init__(self):
        """Initialize SOAP generator service."""
        self.openai = openai_service

    async def generate_soap_from_transcription(
        self,
        transcription_text: str,
        patient_context: Optional[Dict[str, Any]] = None,
        visit_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate SOAP notes from transcription text.

        Args:
            transcription_text: Raw transcription text
            patient_context: Optional patient demographic and medical history
            visit_context: Optional visit information (chief complaint, etc.)

        Returns:
            Dict with structured SOAP notes
        """
        try:
            # Build context-aware system prompt
            system_prompt = self._build_system_prompt(patient_context, visit_context)

            # Build user prompt with transcription
            user_prompt = self._build_user_prompt(transcription_text)

            # Call OpenAI service
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = await self.openai.chat_completion(
                messages=messages,
                model="gpt-4o",
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            # Parse response
            soap_notes = json.loads(response['content'])

            # Add metadata
            soap_notes['generated_at'] = datetime.utcnow().isoformat()
            soap_notes['model'] = response.get('model', 'gpt-4o')
            soap_notes['token_usage'] = response.get('usage', {})

            logger.info("SOAP notes generated successfully")

            return soap_notes

        except Exception as e:
            logger.error(f"Error generating SOAP notes: {e}")
            raise

    async def refine_soap_section(
        self,
        section: str,
        original_text: str,
        refinement_instructions: str
    ) -> str:
        """
        Refine a specific SOAP section based on user instructions.

        Args:
            section: SOAP section name (subjective, objective, assessment, plan)
            original_text: Original section text
            refinement_instructions: User instructions for refinement

        Returns:
            str: Refined section text
        """
        system_prompt = f"""You are a medical documentation specialist helping to refine {section.upper()} sections of SOAP notes.

Your task is to:
1. Maintain medical accuracy and completeness
2. Follow the user's refinement instructions
3. Keep the clinical tone professional
4. Ensure proper medical terminology
5. Return ONLY the refined text, no explanations"""

        user_prompt = f"""Original {section.upper()} section:
{original_text}

Refinement instructions:
{refinement_instructions}

Please provide the refined {section.upper()} section:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await self.openai.chat_completion(
            messages=messages,
            model="gpt-4o",
            temperature=0.5,
            max_tokens=1000
        )

        return response['content'].strip()

    async def suggest_icd_codes(
        self,
        assessment: str,
        diagnoses: list[str]
    ) -> list[Dict[str, Any]]:
        """
        Suggest ICD-10 codes based on assessment and diagnoses.

        Args:
            assessment: Assessment section text
            diagnoses: List of diagnosis descriptions

        Returns:
            List of suggested ICD-10 codes with descriptions
        """
        system_prompt = """You are a medical coding specialist expert in ICD-10 coding.

Your task is to suggest appropriate ICD-10 codes based on clinical documentation.

Return a JSON array of objects with this structure:
[
  {
    "code": "ICD-10 code",
    "description": "Code description",
    "diagnosis": "Matching diagnosis from input",
    "confidence": "high/medium/low"
  }
]"""

        user_prompt = f"""Assessment:
{assessment}

Diagnoses:
{', '.join(diagnoses)}

Please suggest appropriate ICD-10 codes:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await self.openai.chat_completion(
            messages=messages,
            model="gpt-4o",
            temperature=0.2,
            max_tokens=800,
            response_format={"type": "json_object"}
        )

        result = json.loads(response['content'])
        return result.get('codes', [])

    def _build_system_prompt(
        self,
        patient_context: Optional[Dict] = None,
        visit_context: Optional[Dict] = None
    ) -> str:
        """Build context-aware system prompt for SOAP generation."""
        base_prompt = """You are an expert medical documentation assistant specializing in SOAP note generation.

Your task is to convert clinical visit transcriptions into structured, professional SOAP notes.

SOAP Format:
- **Subjective (S)**: Patient's symptoms, concerns, and history in their own words
- **Objective (O)**: Clinical findings, vital signs, physical examination results
- **Assessment (A)**: Medical diagnoses and clinical interpretation
- **Plan (P)**: Treatment plan, medications, follow-up, patient education

Guidelines:
1. Extract and organize information accurately from the transcription
2. Use proper medical terminology
3. Be concise but comprehensive
4. Identify key clinical findings and red flags
5. Structure information logically
6. If information is missing, note it explicitly"""

        context_info = []

        if patient_context:
            context_info.append(f"\nPatient Context:")
            if 'age' in patient_context:
                context_info.append(f"- Age: {patient_context['age']}")
            if 'gender' in patient_context:
                context_info.append(f"- Gender: {patient_context['gender']}")
            if 'allergies' in patient_context and patient_context['allergies']:
                context_info.append(f"- Allergies: {', '.join(patient_context['allergies'])}")
            if 'chronic_conditions' in patient_context and patient_context['chronic_conditions']:
                context_info.append(f"- Chronic Conditions: {', '.join(patient_context['chronic_conditions'])}")

        if visit_context:
            context_info.append(f"\nVisit Context:")
            if 'chief_complaint' in visit_context:
                context_info.append(f"- Chief Complaint: {visit_context['chief_complaint']}")
            if 'visit_type' in visit_context:
                context_info.append(f"- Visit Type: {visit_context['visit_type']}")

        context_section = '\n'.join(context_info) if context_info else ""

        response_format = """

Return a JSON object with this exact structure:
{
  "subjective": "Subjective section text",
  "objective": "Objective section text",
  "assessment": "Assessment section text",
  "plan": "Plan section text",
  "diagnoses": ["Diagnosis 1", "Diagnosis 2"],
  "medications": [
    {
      "name": "Medication name",
      "dosage": "Dosage",
      "frequency": "Frequency",
      "duration": "Duration"
    }
  ],
  "follow_up": "Follow-up instructions",
  "red_flags": ["Red flag 1", "Red flag 2"],
  "vitals": {
    "blood_pressure": "120/80",
    "heart_rate": 72,
    "temperature": 98.6,
    "respiratory_rate": 16,
    "oxygen_saturation": 98
  }
}"""

        return base_prompt + context_section + response_format

    def _build_user_prompt(self, transcription_text: str) -> str:
        """Build user prompt with transcription."""
        return f"""Please convert the following clinical visit transcription into a structured SOAP note:

TRANSCRIPTION:
{transcription_text}

Generate the SOAP note following the specified JSON format:"""


# Global service instance
soap_generator = SOAPGeneratorService()
