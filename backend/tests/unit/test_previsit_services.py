"""
Unit tests for PreVisit.ai services (symptom analyzer, triage engine).
Tests AI-powered symptom analysis and triage functionality.
"""

import pytest
import json
from unittest.mock import AsyncMock, Mock, patch

from src.api.services.previsit.symptom_analyzer import SymptomAnalyzer, symptom_analyzer
from src.api.services.previsit.triage_engine import TriageEngine, triage_engine
from src.api.schemas.previsit_schemas import (
    SymptomInput,
    SymptomAnalysisResponse,
    UrgencyLevel,
    QuestionnaireQuestion,
    QuestionType,
)


@pytest.mark.unit
@pytest.mark.previsit
class TestSymptomAnalyzer:
    """Test SymptomAnalyzer service."""

    @pytest.fixture
    def analyzer(self):
        """Create symptom analyzer instance."""
        return SymptomAnalyzer()

    @pytest.fixture
    def sample_symptoms(self):
        """Create sample symptoms for testing."""
        return [
            SymptomInput(
                name="Headache",
                severity="moderate",
                duration="2 days",
                description="Throbbing pain in temples"
            ),
            SymptomInput(
                name="Fatigue",
                severity="mild",
                duration="1 week",
                description="Feeling tired"
            )
        ]

    @pytest.fixture
    def mock_openai_analysis_response(self):
        """Mock OpenAI response for symptom analysis."""
        return {
            'content': json.dumps({
                "urgency": "moderate",
                "severity": "moderate",
                "triage_level": 3,
                "chief_complaint": "Headache with fatigue",
                "summary": "Patient presents with moderate headache and mild fatigue.",
                "possible_conditions": ["Tension headache", "Migraine", "Stress-related symptoms"],
                "recommendations": [
                    "Stay hydrated",
                    "Get adequate rest",
                    "Monitor symptoms"
                ],
                "red_flags": [
                    "Sudden severe headache",
                    "Vision changes",
                    "Neck stiffness"
                ],
                "follow_up": "If symptoms persist for more than 3 days, schedule appointment"
            })
        }

    @pytest.mark.asyncio
    async def test_analyze_symptoms_success(
        self, analyzer, sample_symptoms, mock_openai_analysis_response
    ):
        """Test successful symptom analysis."""
        # Mock OpenAI service
        with patch.object(
            analyzer.openai,
            'chat_completion',
            new=AsyncMock(return_value=mock_openai_analysis_response)
        ):
            result = await analyzer.analyze_symptoms(sample_symptoms)

            # Verify result type
            assert isinstance(result, SymptomAnalysisResponse)

            # Verify result content
            assert result.urgency == UrgencyLevel.MODERATE
            assert result.severity == "moderate"
            assert result.triage_level == 3
            assert len(result.possible_conditions) > 0
            assert len(result.recommendations) > 0

    @pytest.mark.asyncio
    async def test_analyze_symptoms_with_patient_context(self, analyzer, sample_symptoms):
        """Test symptom analysis with patient context."""
        patient_context = {
            "age": 45,
            "existing_conditions": ["Hypertension", "Diabetes"],
            "vital_signs": {
                "blood_pressure": "140/90",
                "heart_rate": 85
            }
        }

        mock_response = {
            'content': json.dumps({
                "urgency": "moderate",
                "severity": "moderate",
                "triage_level": 3,
                "chief_complaint": "Headache",
                "summary": "Analysis considering patient context",
                "possible_conditions": ["Tension headache"],
                "recommendations": ["Monitor blood pressure"],
                "red_flags": ["Severe headache"],
                "follow_up": "Schedule appointment"
            })
        }

        with patch.object(
            analyzer.openai,
            'chat_completion',
            new=AsyncMock(return_value=mock_response)
        ):
            result = await analyzer.analyze_symptoms(sample_symptoms, patient_context)

            assert isinstance(result, SymptomAnalysisResponse)
            assert result.urgency == UrgencyLevel.MODERATE

    @pytest.mark.asyncio
    async def test_analyze_symptoms_handles_error(self, analyzer, sample_symptoms):
        """Test that symptom analysis handles errors gracefully."""
        # Mock OpenAI service to raise an error
        with patch.object(
            analyzer.openai,
            'chat_completion',
            new=AsyncMock(side_effect=Exception("API Error"))
        ):
            result = await analyzer.analyze_symptoms(sample_symptoms)

            # Should return default analysis instead of raising error
            assert isinstance(result, SymptomAnalysisResponse)
            assert result.urgency == UrgencyLevel.MODERATE
            assert "professional evaluation" in result.summary.lower()

    @pytest.mark.asyncio
    async def test_generate_questionnaire_success(self, analyzer):
        """Test successful questionnaire generation."""
        mock_response = {
            'content': json.dumps({
                "questions": [
                    {
                        "id": "q1",
                        "type": "scale",
                        "question": "On a scale of 1-10, how severe is your pain?",
                        "options": list(range(1, 11)),
                        "required": True
                    },
                    {
                        "id": "q2",
                        "type": "select",
                        "question": "When did symptoms start?",
                        "options": ["Today", "Yesterday", "This week"],
                        "required": True
                    }
                ]
            })
        }

        with patch.object(
            analyzer.openai,
            'chat_completion',
            new=AsyncMock(return_value=mock_response)
        ):
            questions = await analyzer.generate_questionnaire(
                chief_complaint="Headache",
                symptoms=["Headache", "Dizziness"]
            )

            # Verify questions returned
            assert len(questions) == 2
            assert all(isinstance(q, QuestionnaireQuestion) for q in questions)
            assert questions[0].type == QuestionType.SCALE
            assert questions[1].type == QuestionType.SELECT

    @pytest.mark.asyncio
    async def test_generate_questionnaire_handles_error(self, analyzer):
        """Test that questionnaire generation handles errors gracefully."""
        with patch.object(
            analyzer.openai,
            'chat_completion',
            new=AsyncMock(side_effect=Exception("API Error"))
        ):
            questions = await analyzer.generate_questionnaire("Headache")

            # Should return default questionnaire
            assert len(questions) > 0
            assert all(isinstance(q, QuestionnaireQuestion) for q in questions)

    def test_build_analysis_prompt(self, analyzer, sample_symptoms):
        """Test building analysis prompt."""
        patient_context = {"age": 30}
        prompt = analyzer._build_analysis_prompt(sample_symptoms, patient_context)

        # Verify prompt contains symptom information
        assert "Headache" in prompt
        assert "Fatigue" in prompt
        assert "moderate" in prompt
        assert "2 days" in prompt
        assert "Age: 30" in prompt

    def test_build_questionnaire_prompt(self, analyzer):
        """Test building questionnaire prompt."""
        prompt = analyzer._build_questionnaire_prompt(
            chief_complaint="Fever",
            symptoms=["Fever", "Chills"]
        )

        assert "Fever" in prompt
        assert "Chills" in prompt
        assert "JSON format" in prompt

    def test_get_default_analysis(self, analyzer, sample_symptoms):
        """Test default analysis generation."""
        result = analyzer._get_default_analysis(sample_symptoms)

        assert isinstance(result, SymptomAnalysisResponse)
        assert result.urgency == UrgencyLevel.MODERATE
        assert len(result.recommendations) > 0
        assert len(result.red_flags) > 0

    def test_get_default_questionnaire(self, analyzer):
        """Test default questionnaire generation."""
        questions = analyzer._get_default_questionnaire("Headache")

        assert len(questions) > 0
        assert all(isinstance(q, QuestionnaireQuestion) for q in questions)


@pytest.mark.unit
@pytest.mark.previsit
class TestTriageEngine:
    """Test TriageEngine service."""

    @pytest.fixture
    def engine(self):
        """Create triage engine instance."""
        return TriageEngine()

    @pytest.fixture
    def sample_chief_complaint(self):
        """Sample chief complaint."""
        return "Chest pain"

    @pytest.fixture
    def sample_symptoms_mild(self):
        """Sample mild symptoms."""
        return [
            SymptomInput(
                name="Headache",
                severity="mild",
                duration="1 day",
                description="Mild headache"
            )
        ]

    @pytest.fixture
    def sample_symptoms_severe(self):
        """Sample severe symptoms."""
        return [
            SymptomInput(
                name="Chest pain",
                severity="severe",
                duration="30 minutes",
                description="Sharp pain radiating to left arm"
            )
        ]

    @pytest.fixture
    def sample_vital_signs_normal(self):
        """Normal vital signs."""
        return {
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80,
            "heart_rate": 70,
            "temperature": 98.6,
            "respiratory_rate": 16
        }

    @pytest.fixture
    def sample_vital_signs_abnormal(self):
        """Abnormal vital signs."""
        return {
            "blood_pressure_systolic": 180,
            "blood_pressure_diastolic": 110,
            "heart_rate": 120,
            "temperature": 103.0,
            "respiratory_rate": 28
        }

    @pytest.mark.asyncio
    async def test_assess_triage_level_routine(
        self, engine, sample_symptoms_mild, sample_vital_signs_normal
    ):
        """Test triage assessment for routine case."""
        result = await engine.assess_triage(
            chief_complaint="Mild headache",
            symptoms=sample_symptoms_mild,
            vital_signs=sample_vital_signs_normal
        )

        # Routine case should have lower urgency
        assert result.triage_level in [4, 5]
        assert result.urgency in [UrgencyLevel.LOW, UrgencyLevel.MODERATE]

    @pytest.mark.asyncio
    async def test_assess_triage_level_emergency(
        self, engine, sample_symptoms_severe, sample_vital_signs_abnormal
    ):
        """Test triage assessment for emergency case."""
        result = await engine.assess_triage(
            chief_complaint="Severe chest pain",
            symptoms=sample_symptoms_severe,
            vital_signs=sample_vital_signs_abnormal
        )

        # Emergency case should have high urgency
        assert result.triage_level in [1, 2]
        assert result.urgency in [UrgencyLevel.URGENT, UrgencyLevel.EMERGENCY]

    @pytest.mark.asyncio
    async def test_detect_red_flags_chest_pain(self, engine):
        """Test red flag detection for chest pain."""
        symptoms = [
            SymptomInput(
                name="Chest pain",
                severity="severe",
                duration="30 minutes",
                description="Pressure in chest"
            )
        ]

        result = await engine.assess_triage(
            chief_complaint="Chest pain",
            symptoms=symptoms
        )

        # Chest pain should trigger red flags
        assert len(result.red_flags) > 0
        assert result.immediate_action_required is True

    @pytest.mark.asyncio
    async def test_detect_red_flags_difficulty_breathing(self, engine):
        """Test red flag detection for difficulty breathing."""
        symptoms = [
            SymptomInput(
                name="Difficulty breathing",
                severity="severe",
                duration="1 hour",
                description="Can't catch breath"
            )
        ]

        result = await engine.assess_triage(
            chief_complaint="Shortness of breath",
            symptoms=symptoms
        )

        # Breathing difficulty should trigger red flags
        assert len(result.red_flags) > 0
        assert result.immediate_action_required is True

    @pytest.mark.asyncio
    async def test_vital_signs_assessment_normal(self, engine, sample_vital_signs_normal):
        """Test vital signs assessment with normal values."""
        abnormal = engine._assess_vital_signs(sample_vital_signs_normal)

        # Normal vital signs should return empty or minimal abnormalities
        assert len(abnormal) == 0

    @pytest.mark.asyncio
    async def test_vital_signs_assessment_abnormal(self, engine, sample_vital_signs_abnormal):
        """Test vital signs assessment with abnormal values."""
        abnormal = engine._assess_vital_signs(sample_vital_signs_abnormal)

        # Abnormal vital signs should be detected
        assert len(abnormal) > 0

    def test_calculate_severity_score_mild(self, engine, sample_symptoms_mild):
        """Test severity score calculation for mild symptoms."""
        score = engine._calculate_severity_score(sample_symptoms_mild)

        # Mild symptoms should have low score
        assert score < 5

    def test_calculate_severity_score_severe(self, engine, sample_symptoms_severe):
        """Test severity score calculation for severe symptoms."""
        score = engine._calculate_severity_score(sample_symptoms_severe)

        # Severe symptoms should have high score
        assert score >= 7

    def test_triage_level_to_urgency(self, engine):
        """Test conversion from triage level to urgency."""
        assert engine._triage_level_to_urgency(1) == UrgencyLevel.EMERGENCY
        assert engine._triage_level_to_urgency(2) == UrgencyLevel.URGENT
        assert engine._triage_level_to_urgency(3) == UrgencyLevel.HIGH
        assert engine._triage_level_to_urgency(4) == UrgencyLevel.MODERATE
        assert engine._triage_level_to_urgency(5) == UrgencyLevel.LOW


@pytest.mark.unit
@pytest.mark.previsit
class TestPreVisitIntegration:
    """Integration tests for PreVisit services working together."""

    @pytest.mark.asyncio
    async def test_symptom_analysis_and_triage_workflow(self):
        """Test complete workflow from symptom analysis to triage."""
        symptoms = [
            SymptomInput(
                name="Fever",
                severity="moderate",
                duration="2 days",
                description="Fever around 101°F"
            ),
            SymptomInput(
                name="Cough",
                severity="mild",
                duration="3 days",
                description="Dry cough"
            )
        ]

        # Mock symptom analyzer
        mock_analysis_response = {
            'content': json.dumps({
                "urgency": "moderate",
                "severity": "moderate",
                "triage_level": 3,
                "chief_complaint": "Fever and cough",
                "summary": "Possible respiratory infection",
                "possible_conditions": ["Upper respiratory infection", "Flu"],
                "recommendations": ["Rest", "Hydrate", "Monitor temperature"],
                "red_flags": ["Difficulty breathing", "High fever >103°F"],
                "follow_up": "Schedule appointment if symptoms worsen"
            })
        }

        with patch.object(
            symptom_analyzer.openai,
            'chat_completion',
            new=AsyncMock(return_value=mock_analysis_response)
        ):
            # Analyze symptoms
            analysis = await symptom_analyzer.analyze_symptoms(symptoms)
            assert analysis.urgency == UrgencyLevel.MODERATE

            # Triage assessment
            triage = await triage_engine.assess_triage(
                chief_complaint="Fever and cough",
                symptoms=symptoms,
                vital_signs={
                    "temperature": 101.0,
                    "heart_rate": 85,
                    "respiratory_rate": 18
                }
            )

            # Verify triage is consistent with analysis
            assert triage.triage_level in [3, 4]
            assert triage.urgency in [UrgencyLevel.MODERATE, UrgencyLevel.HIGH]
