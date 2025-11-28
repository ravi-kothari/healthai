"""
Unit tests for CarePrep services (symptom analysis, triage, questionnaires).

Tests symptom_analyzer, triage_engine, and questionnaire generation
with mocked OpenAI responses.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

from src.api.services.previsit.symptom_analyzer import symptom_analyzer, SymptomAnalyzer
from src.api.services.previsit.triage_engine import triage_engine, TriageEngine
from src.api.schemas.previsit_schemas import (
    Symptom,
    SymptomAnalysisRequest,
    TriageAssessmentRequest,
    VitalSigns,
)


# Mark all tests in this file
pytestmark = [pytest.mark.unit, pytest.mark.careprep]


class TestSymptomAnalyzer:
    """Test suite for SymptomAnalyzer service."""

    def test_symptom_analyzer_instance(self):
        """Test that symptom_analyzer is properly instantiated."""
        assert symptom_analyzer is not None
        assert isinstance(symptom_analyzer, SymptomAnalyzer)

    @pytest.mark.asyncio
    async def test_analyze_symptoms_basic(self, mock_openai_response):
        """Test basic symptom analysis with mocked OpenAI response."""
        # Arrange
        symptoms = [
            Symptom(
                name="Headache",
                severity="moderate",
                duration="2 days",
                description="Throbbing pain in temples"
            )
        ]

        # Mock the OpenAI service
        with patch.object(symptom_analyzer, 'openai_service') as mock_openai:
            mock_openai.generate_json_response = AsyncMock(return_value=mock_openai_response)

            # Act
            result = await symptom_analyzer.analyze_symptoms(symptoms)

            # Assert
            assert result is not None
            assert "urgency" in result
            assert "likely_conditions" in result
            assert "recommendations" in result
            assert result["urgency"] == "moderate"
            assert len(result["likely_conditions"]) > 0
            mock_openai.generate_json_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_symptoms_multiple(self):
        """Test symptom analysis with multiple symptoms."""
        # Arrange
        symptoms = [
            Symptom(
                name="Headache",
                severity="moderate",
                duration="2 days",
                description="Throbbing pain"
            ),
            Symptom(
                name="Fatigue",
                severity="mild",
                duration="1 week",
                description="Feeling tired"
            ),
            Symptom(
                name="Nausea",
                severity="mild",
                duration="1 day",
                description="Feeling queasy"
            ),
        ]

        mock_response = {
            "urgency": "moderate",
            "likely_conditions": ["Migraine", "Tension headache", "Flu"],
            "red_flags": [],
            "recommendations": ["Rest", "Hydration", "Over-the-counter pain relief"],
            "follow_up": "Monitor symptoms for 48 hours",
        }

        # Mock the OpenAI service
        with patch.object(symptom_analyzer, 'openai_service') as mock_openai:
            mock_openai.generate_json_response = AsyncMock(return_value=mock_response)

            # Act
            result = await symptom_analyzer.analyze_symptoms(symptoms)

            # Assert
            assert result["urgency"] == "moderate"
            assert len(result["likely_conditions"]) == 3
            assert "Migraine" in result["likely_conditions"]
            assert len(result["recommendations"]) == 3

    @pytest.mark.asyncio
    async def test_analyze_symptoms_red_flags(self):
        """Test symptom analysis with red flag symptoms."""
        # Arrange
        symptoms = [
            Symptom(
                name="Chest pain",
                severity="severe",
                duration="30 minutes",
                description="Sharp pain radiating to left arm"
            )
        ]

        mock_response = {
            "urgency": "emergency",
            "likely_conditions": ["Myocardial infarction", "Angina"],
            "red_flags": ["Chest pain with radiation", "Severe pain"],
            "recommendations": ["Seek immediate emergency care", "Call 911"],
            "follow_up": "Immediate medical attention required",
        }

        # Mock the OpenAI service
        with patch.object(symptom_analyzer, 'openai_service') as mock_openai:
            mock_openai.generate_json_response = AsyncMock(return_value=mock_response)

            # Act
            result = await symptom_analyzer.analyze_symptoms(symptoms)

            # Assert
            assert result["urgency"] == "emergency"
            assert len(result["red_flags"]) > 0
            assert "Chest pain with radiation" in result["red_flags"]

    @pytest.mark.asyncio
    async def test_build_symptom_prompt(self):
        """Test that symptom prompt is properly formatted."""
        # Arrange
        symptoms = [
            Symptom(
                name="Headache",
                severity="moderate",
                duration="2 days",
                description="Throbbing pain"
            )
        ]

        # Act
        prompt = symptom_analyzer._build_symptom_prompt(symptoms)

        # Assert
        assert "Headache" in prompt
        assert "moderate" in prompt
        assert "2 days" in prompt
        assert "Throbbing pain" in prompt
        assert "medical triage" in prompt.lower() or "symptom" in prompt.lower()

    @pytest.mark.asyncio
    async def test_analyze_symptoms_empty_list(self):
        """Test symptom analysis with empty symptoms list."""
        # Arrange
        symptoms = []

        # Act & Assert
        with pytest.raises(ValueError, match=".*symptoms.*"):
            await symptom_analyzer.analyze_symptoms(symptoms)

    @pytest.mark.asyncio
    async def test_generate_questionnaire_basic(self):
        """Test basic questionnaire generation."""
        # Arrange
        chief_complaint = "Headache"

        mock_questionnaire = {
            "questions": [
                {
                    "id": "q1",
                    "text": "Where is the headache located?",
                    "type": "select",
                    "options": ["Forehead", "Temples", "Back of head", "Entire head"],
                    "required": True,
                },
                {
                    "id": "q2",
                    "text": "How would you describe the pain?",
                    "type": "select",
                    "options": ["Throbbing", "Constant", "Sharp", "Dull"],
                    "required": True,
                },
                {
                    "id": "q3",
                    "text": "Any additional symptoms?",
                    "type": "multiselect",
                    "options": ["Nausea", "Sensitivity to light", "Sensitivity to sound", "Visual changes"],
                    "required": False,
                },
            ]
        }

        # Mock the OpenAI service
        with patch.object(symptom_analyzer, 'openai_service') as mock_openai:
            mock_openai.generate_json_response = AsyncMock(return_value=mock_questionnaire)

            # Act
            result = await symptom_analyzer.generate_questionnaire(chief_complaint)

            # Assert
            assert result is not None
            assert "questions" in result
            assert len(result["questions"]) == 3
            assert result["questions"][0]["text"] == "Where is the headache located?"
            assert result["questions"][0]["type"] == "select"
            assert len(result["questions"][0]["options"]) == 4

    @pytest.mark.asyncio
    async def test_generate_questionnaire_with_symptoms(self):
        """Test questionnaire generation with existing symptoms."""
        # Arrange
        chief_complaint = "Headache"
        symptoms = [
            Symptom(
                name="Headache",
                severity="moderate",
                duration="2 days",
                description="Throbbing temples"
            )
        ]

        mock_questionnaire = {
            "questions": [
                {
                    "id": "q1",
                    "text": "Have you taken any medication for the headache?",
                    "type": "select",
                    "options": ["Yes", "No"],
                    "required": True,
                },
            ]
        }

        # Mock the OpenAI service
        with patch.object(symptom_analyzer, 'openai_service') as mock_openai:
            mock_openai.generate_json_response = AsyncMock(return_value=mock_questionnaire)

            # Act
            result = await symptom_analyzer.generate_questionnaire(chief_complaint, symptoms)

            # Assert
            assert result is not None
            assert len(result["questions"]) == 1
            mock_openai.generate_json_response.assert_called_once()


class TestTriageEngine:
    """Test suite for TriageEngine service."""

    def test_triage_engine_instance(self):
        """Test that triage_engine is properly instantiated."""
        assert triage_engine is not None
        assert isinstance(triage_engine, TriageEngine)

    @pytest.mark.asyncio
    async def test_assess_triage_moderate_urgency(self):
        """Test triage assessment for moderate urgency case."""
        # Arrange
        chief_complaint = "Headache"
        symptoms = [
            Symptom(
                name="Headache",
                severity="moderate",
                duration="2 days",
                description="Persistent headache"
            )
        ]
        vital_signs = VitalSigns(
            blood_pressure_systolic=120,
            blood_pressure_diastolic=80,
            heart_rate=75,
            temperature=98.6,
            respiratory_rate=16,
        )

        # Act
        result = await triage_engine.assess_triage(
            chief_complaint=chief_complaint,
            symptoms=symptoms,
            vital_signs=vital_signs
        )

        # Assert
        assert result is not None
        assert "triage_level" in result
        assert "urgency" in result
        assert "severity_score" in result
        assert "red_flags" in result
        assert "recommended_action" in result
        assert result["triage_level"] in [1, 2, 3, 4, 5]
        assert result["urgency"] in ["routine", "moderate", "urgent", "emergency", "critical"]

    @pytest.mark.asyncio
    async def test_assess_triage_emergency(self):
        """Test triage assessment for emergency case."""
        # Arrange
        chief_complaint = "Severe chest pain"
        symptoms = [
            Symptom(
                name="Chest pain",
                severity="severe",
                duration="30 minutes",
                description="Sharp pain radiating to left arm"
            )
        ]
        vital_signs = VitalSigns(
            blood_pressure_systolic=160,
            blood_pressure_diastolic=100,
            heart_rate=120,
            temperature=98.6,
            respiratory_rate=24,
        )

        # Act
        result = await triage_engine.assess_triage(
            chief_complaint=chief_complaint,
            symptoms=symptoms,
            vital_signs=vital_signs
        )

        # Assert
        assert result["urgency"] in ["emergency", "critical"]
        assert result["triage_level"] in [1, 2]  # High priority
        assert len(result["red_flags"]) > 0

    @pytest.mark.asyncio
    async def test_assess_triage_routine(self):
        """Test triage assessment for routine case."""
        # Arrange
        chief_complaint = "Minor cough"
        symptoms = [
            Symptom(
                name="Cough",
                severity="mild",
                duration="3 days",
                description="Occasional dry cough"
            )
        ]
        vital_signs = VitalSigns(
            blood_pressure_systolic=118,
            blood_pressure_diastolic=78,
            heart_rate=70,
            temperature=98.4,
            respiratory_rate=14,
        )

        # Act
        result = await triage_engine.assess_triage(
            chief_complaint=chief_complaint,
            symptoms=symptoms,
            vital_signs=vital_signs
        )

        # Assert
        assert result["urgency"] in ["routine", "moderate"]
        assert result["triage_level"] in [3, 4, 5]  # Lower priority

    @pytest.mark.asyncio
    async def test_detect_red_flags(self):
        """Test red flag detection."""
        # Arrange
        symptoms = [
            Symptom(
                name="Chest pain",
                severity="severe",
                duration="30 minutes",
                description="radiating pain"
            ),
            Symptom(
                name="Shortness of breath",
                severity="severe",
                duration="30 minutes",
                description="difficulty breathing"
            ),
        ]

        # Act
        red_flags = triage_engine._detect_red_flags(symptoms)

        # Assert
        assert isinstance(red_flags, list)
        # Red flags should be detected for chest pain and breathing issues
        assert len(red_flags) > 0

    @pytest.mark.asyncio
    async def test_calculate_severity_score(self):
        """Test severity score calculation."""
        # Arrange
        symptoms = [
            Symptom(
                name="Headache",
                severity="moderate",
                duration="2 days",
                description="Persistent headache"
            )
        ]
        vital_signs = VitalSigns(
            blood_pressure_systolic=120,
            blood_pressure_diastolic=80,
            heart_rate=75,
            temperature=98.6,
            respiratory_rate=16,
        )

        # Act
        score = triage_engine._calculate_severity_score(symptoms, vital_signs)

        # Assert
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100  # Assuming score is 0-100 range

    @pytest.mark.asyncio
    async def test_assess_triage_no_vital_signs(self):
        """Test triage assessment without vital signs."""
        # Arrange
        chief_complaint = "Headache"
        symptoms = [
            Symptom(
                name="Headache",
                severity="moderate",
                duration="2 days",
                description="Persistent headache"
            )
        ]

        # Act
        result = await triage_engine.assess_triage(
            chief_complaint=chief_complaint,
            symptoms=symptoms,
            vital_signs=None
        )

        # Assert
        assert result is not None
        assert "triage_level" in result
        # Should still provide triage even without vitals

    @pytest.mark.asyncio
    async def test_assess_triage_empty_symptoms(self):
        """Test triage assessment with no symptoms."""
        # Arrange
        chief_complaint = "General checkup"
        symptoms = []

        # Act & Assert
        with pytest.raises(ValueError, match=".*symptoms.*"):
            await triage_engine.assess_triage(
                chief_complaint=chief_complaint,
                symptoms=symptoms,
                vital_signs=None
            )


class TestCarePreServiceIntegration:
    """Integration tests between CarePrep services."""

    @pytest.mark.asyncio
    async def test_symptom_analysis_to_triage_flow(self):
        """Test complete flow from symptom analysis to triage."""
        # Arrange
        symptoms = [
            Symptom(
                name="Fever",
                severity="moderate",
                duration="2 days",
                description="Temperature of 101°F"
            ),
            Symptom(
                name="Cough",
                severity="moderate",
                duration="3 days",
                description="Persistent dry cough"
            ),
        ]
        vital_signs = VitalSigns(
            blood_pressure_systolic=125,
            blood_pressure_diastolic=82,
            heart_rate=85,
            temperature=101.0,
            respiratory_rate=18,
        )

        mock_analysis = {
            "urgency": "moderate",
            "likely_conditions": ["Upper respiratory infection", "Flu"],
            "red_flags": [],
            "recommendations": ["Rest", "Fluids", "Monitor temperature"],
            "follow_up": "Contact doctor if symptoms worsen",
        }

        # Mock the OpenAI service
        with patch.object(symptom_analyzer, 'openai_service') as mock_openai:
            mock_openai.generate_json_response = AsyncMock(return_value=mock_analysis)

            # Act
            analysis_result = await symptom_analyzer.analyze_symptoms(symptoms)
            triage_result = await triage_engine.assess_triage(
                chief_complaint="Fever and cough",
                symptoms=symptoms,
                vital_signs=vital_signs
            )

            # Assert
            assert analysis_result["urgency"] == "moderate"
            assert triage_result["urgency"] in ["moderate", "urgent"]
            # Both services should provide consistent urgency assessment
