"""
Unit tests for CarePrep services (symptom analysis, triage, questionnaires).

Tests symptom_analyzer, triage_engine, and questionnaire generation
with mocked OpenAI responses.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

from src.api.services.previsit.symptom_analyzer import symptom_analyzer, SymptomAnalyzer
from src.api.services.previsit.triage_engine import triage_engine, TriageEngine
from src.api.schemas.previsit_schemas import (
    SymptomInput,
    SymptomAnalysisRequest,
    TriageAssessmentRequest,
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
            SymptomInput(
                name="Headache",
                severity="moderate",
                duration="2 days",
                description="Throbbing pain in temples"
            )
        ]

        # Mock the OpenAI service
        with patch.object(symptom_analyzer, 'openai') as mock_openai:
            mock_openai.chat_completion = AsyncMock(return_value={"content": json.dumps(mock_openai_response)})

            # Act
            result = await symptom_analyzer.analyze_symptoms(symptoms)

            # Assert
            # Assert
            assert result is not None
            assert result.urgency is not None
            assert result.possible_conditions is not None
            assert result.recommendations is not None
            assert result.urgency == "moderate"
            assert len(result.possible_conditions) > 0
            mock_openai.chat_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_symptoms_multiple(self):
        """Test symptom analysis with multiple symptoms."""
        # Arrange
        symptoms = [
            SymptomInput(
                name="Headache",
                severity="moderate",
                duration="2 days",
                description="Throbbing pain"
            ),
            SymptomInput(
                name="Fatigue",
                severity="mild",
                duration="1 week",
                description="Feeling tired"
            ),
            SymptomInput(
                name="Nausea",
                severity="mild",
                duration="1 day",
                description="Feeling queasy"
            ),
        ]

        mock_response = {
            "urgency": "moderate",
            "severity": "moderate",
            "triage_level": 3,
            "chief_complaint": "Headache",
            "summary": "Patient has headache",
            "possible_conditions": ["Migraine", "Tension headache", "Flu"],
            "red_flags": [],
            "recommendations": ["Rest", "Hydration", "Over-the-counter pain relief"],
            "follow_up": "Monitor symptoms for 48 hours",
        }

        # Mock the OpenAI service
        with patch.object(symptom_analyzer, 'openai') as mock_openai:
            mock_openai.chat_completion = AsyncMock(return_value={"content": json.dumps(mock_response)})

            # Act
            result = await symptom_analyzer.analyze_symptoms(symptoms)

            # Assert
            # Assert
            assert result.urgency == "moderate"
            assert len(result.possible_conditions) == 3
            assert "Migraine" in result.possible_conditions
            assert len(result.recommendations) == 3

    @pytest.mark.asyncio
    async def test_analyze_symptoms_red_flags(self):
        """Test symptom analysis with red flag symptoms."""
        # Arrange
        symptoms = [
            SymptomInput(
                name="Chest pain",
                severity="severe",
                duration="30 minutes",
                description="Sharp pain radiating to left arm"
            )
        ]

        mock_response = {
            "urgency": "emergency",
            "severity": "severe",
            "triage_level": 1,
            "chief_complaint": "Chest pain",
            "summary": "Patient has chest pain",
            "possible_conditions": ["Myocardial infarction", "Angina"],
            "red_flags": ["Chest pain with radiation", "Severe pain"],
            "recommendations": ["Seek immediate emergency care", "Call 911"],
            "follow_up": "Immediate medical attention required",
        }

        # Mock the OpenAI service
        with patch.object(symptom_analyzer, 'openai') as mock_openai:
            mock_openai.chat_completion = AsyncMock(return_value={"content": json.dumps(mock_response)})

            # Act
            result = await symptom_analyzer.analyze_symptoms(symptoms)

            # Assert
            # Assert
            assert result.urgency == "emergency"
            assert len(result.red_flags) > 0
            assert "Chest pain with radiation" in result.red_flags

    @pytest.mark.asyncio
    async def test_build_symptom_prompt(self):
        """Test that symptom prompt is properly formatted."""
        # Arrange
        symptoms = [
            SymptomInput(
                name="Headache",
                severity="moderate",
                duration="1 day",
                description="Frontal"
            )
        ]

        # Act
        # Act
        prompt = symptom_analyzer._build_analysis_prompt(symptoms, None)

        # Assert
        assert "Headache" in prompt
        assert "MODERATE" in prompt or "moderate" in prompt
        assert "1 day" in prompt
        assert "Frontal" in prompt
        assert "medical triage" in prompt.lower() or "symptom" in prompt.lower()

    @pytest.mark.asyncio
    async def test_analyze_symptoms_empty_list(self):
        """Test symptom analysis with empty symptoms list."""
        # Arrange
        symptoms = []

        # Act & Assert
        # Act
        # Should handle empty list gracefully without raising error
        # We mock openai to return something generic if called, or it might just return default
        with patch.object(symptom_analyzer, 'openai') as mock_openai:
            mock_openai.chat_completion = AsyncMock(return_value={"content": json.dumps({
                "urgency": "low",
                "severity": "mild",
                "triage_level": 5,
                "chief_complaint": "None",
                "summary": "No symptoms provided",
                "possible_conditions": [],
                "recommendations": [],
                "red_flags": [],
                "follow_up": "None"
            })})
            
            result = await symptom_analyzer.analyze_symptoms(symptoms)
            
        # Assert
        assert result is not None
        assert result.urgency == "low" or result.urgency == "moderate" # Default might be moderate

    @pytest.mark.asyncio
    async def test_generate_questionnaire_basic(self):
        """Test basic questionnaire generation."""
        # Arrange
        chief_complaint = "Headache"

        mock_questionnaire = {
            "questions": [
                {
                    "id": "q1",
                    "question": "Where is the headache located?",
                    "type": "select",
                    "options": ["Forehead", "Temples", "Back of head", "Entire head"],
                    "required": True,
                },
                {
                    "id": "q2",
                    "question": "How would you describe the pain?",
                    "type": "select",
                    "options": ["Throbbing", "Constant", "Sharp", "Dull"],
                    "required": True,
                },
                {
                    "id": "q3",
                    "question": "Any additional symptoms?",
                    "type": "multiselect",
                    "options": ["Nausea", "Sensitivity to light", "Sensitivity to sound", "Visual changes"],
                    "required": False,
                },
            ],
            "estimated_time_minutes": 5
        }

        # Mock the OpenAI service
        with patch.object(symptom_analyzer, 'openai') as mock_openai:
            mock_openai.chat_completion = AsyncMock(return_value={"content": json.dumps(mock_questionnaire)})

            # Act
            result = await symptom_analyzer.generate_questionnaire(chief_complaint)

            # Assert
            assert result is not None
            # Assert
            assert result is not None
            assert isinstance(result, list)
            assert len(result) == 3
            assert result[0].question == "Where is the headache located?"
            assert result[0].type == "select"
            assert len(result[0].options) == 4

    @pytest.mark.asyncio
    async def test_generate_questionnaire_with_symptoms(self):
        """Test questionnaire generation with existing symptoms."""
        # Arrange
        chief_complaint = "Headache"
        symptoms = [
            SymptomInput(
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
                    "question": "Have you taken any medication for the headache?",
                    "type": "select",
                    "options": ["Yes", "No"],
                    "required": True,
                },
            ],
            "estimated_time_minutes": 2
        }

        # Mock the OpenAI service
        with patch.object(symptom_analyzer, 'openai') as mock_openai:
            mock_openai.chat_completion = AsyncMock(return_value={"content": json.dumps(mock_questionnaire)})

            # Act
            result = await symptom_analyzer.generate_questionnaire(chief_complaint, symptoms)

            # Assert
            # Assert
            assert result is not None
            assert len(result) == 1
            mock_openai.chat_completion.assert_called_once()


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
            SymptomInput(
                name="Headache",
                severity="moderate",
                duration="2 days",
                description="Persistent headache"
            )
        ]
        vital_signs = {
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80,
            "heart_rate": 75,
            "temperature": 98.6,
            "respiratory_rate": 16,
        }

        # Act
        result = await triage_engine.assess_triage(
            symptoms=symptoms,
            vital_signs=vital_signs
        )

        # Assert
        assert result is not None
        assert result.triage_level is not None
        assert result.urgency is not None
        assert result.emergency_flags is not None
        assert result.recommended_action is not None
        assert result.triage_level in [1, 2, 3, 4, 5]
        assert result.urgency in ["low", "routine", "moderate", "urgent", "emergency", "critical"]

    @pytest.mark.asyncio
    async def test_assess_triage_emergency(self):
        """Test triage assessment for emergency case."""
        # Arrange
        chief_complaint = "Severe chest pain"
        symptoms = [
            SymptomInput(
                name="Chest pain",
                severity="severe",
                duration="30 minutes",
                description="Sharp pain radiating to left arm"
            )
        ]
        vital_signs = {
            "blood_pressure_systolic": 160,
            "blood_pressure_diastolic": 100,
            "heart_rate": 120,
            "temperature": 98.6,
            "respiratory_rate": 24,
        }

        # Act
        result = await triage_engine.assess_triage(
            symptoms=symptoms,
            vital_signs=vital_signs
        )

        # Assert
        assert result.urgency in ["emergency", "critical"]
        assert result.triage_level in [1, 2]  # High priority
        assert len(result.emergency_flags) > 0

    @pytest.mark.asyncio
    async def test_assess_triage_routine(self):
        """Test triage assessment for routine case."""
        # Arrange
        chief_complaint = "Minor cough"
        symptoms = [
            SymptomInput(
                name="Cough",
                severity="mild",
                duration="3 days",
                description="Occasional dry cough"
            )
        ]
        vital_signs = {
            "blood_pressure_systolic": 118,
            "blood_pressure_diastolic": 78,
            "heart_rate": 70,
            "temperature": 98.4,
            "respiratory_rate": 14,
        }

        # Act
        result = await triage_engine.assess_triage(
            symptoms=symptoms,
            vital_signs=vital_signs
        )

        # Assert
        assert result.urgency in ["low", "routine", "moderate"]
        assert result.triage_level in [3, 4, 5]  # Lower priority

    @pytest.mark.asyncio
    async def test_detect_red_flags(self):
        """Test red flag detection."""
        # Arrange
        symptoms = [
            SymptomInput(
                name="Chest pain",
                severity="severe",
                duration="30 minutes",
                description="radiating pain"
            ),
            SymptomInput(
                name="Shortness of breath",
                severity="severe",
                duration="30 minutes",
                description="difficulty breathing"
            ),
        ]

        # Act
        # Act
        red_flags = triage_engine._check_emergency_flags(symptoms, None)

        # Assert
        assert isinstance(red_flags, list)
        # Red flags should be detected for chest pain and breathing issues
        assert len(red_flags) > 0

    @pytest.mark.asyncio
    async def test_calculate_severity_score(self):
        """Test severity score calculation."""
        # Arrange
        symptoms = [
            SymptomInput(
                name="Headache",
                severity="moderate",
                duration="2 days",
                description="Persistent headache"
            )
        ]
        vital_signs = {
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80,
            "heart_rate": 75,
            "temperature": 98.6,
            "respiratory_rate": 16,
        }

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
            SymptomInput(
                name="Headache",
                severity="moderate",
                duration="2 days",
                description="Persistent headache"
            )
        ]

        # Act
        result = await triage_engine.assess_triage(
            symptoms=symptoms,
            vital_signs=None
        )

        # Assert
        assert result is not None
        assert result.triage_level is not None
        # Should still provide triage even without vitals

    @pytest.mark.asyncio
    async def test_assess_triage_empty_symptoms(self):
        """Test triage assessment with no symptoms."""
        # Arrange
        symptoms = []

        # Act
        result = await triage_engine.assess_triage(
            symptoms=symptoms,
            vital_signs=None
        )

        # Assert
        assert result is not None
        assert result.triage_level == 5  # Routine
        assert result.urgency == "low"


class TestCarePreServiceIntegration:
    """Integration tests between CarePrep services."""

    @pytest.mark.asyncio
    async def test_symptom_analysis_to_triage_flow(self):
        """Test complete flow from symptom analysis to triage."""
        # Arrange
        symptoms = [
            SymptomInput(
                name="Fever",
                severity="moderate",
                duration="2 days",
                description="101F"
            ),
            SymptomInput(
                name="Cough",
                severity="moderate",
                duration="2 days",
                description="Productive"
            ),
        ]
        vital_signs = {
            "blood_pressure_systolic": 125,
            "blood_pressure_diastolic": 82,
            "heart_rate": 85,
            "temperature": 101.0,
            "respiratory_rate": 18,
        }

        mock_analysis = {
            "urgency": "moderate",
            "severity": "moderate",
            "triage_level": 3,
            "chief_complaint": "Fever and cough",
            "summary": "Patient has fever and cough",
            "possible_conditions": ["Upper respiratory infection", "Flu"],
            "red_flags": [],
            "recommendations": ["Rest", "Fluids", "Monitor temperature"],
            "follow_up": "Contact doctor if symptoms worsen",
        }

        # Mock the OpenAI service
        with patch.object(symptom_analyzer, 'openai') as mock_openai:
            mock_openai.chat_completion = AsyncMock(return_value={"content": json.dumps(mock_analysis)})

            # Act
            analysis_result = await symptom_analyzer.analyze_symptoms(symptoms)
            triage_result = await triage_engine.assess_triage(
                symptoms=symptoms,
                vital_signs=vital_signs
            )

            # Assert
            # Assert
            assert analysis_result.urgency == "moderate"
            assert triage_result.urgency in ["low", "moderate", "urgent", "high"]
            # Both services should provide consistent urgency assessment
