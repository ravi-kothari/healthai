"""
Unit tests for ContextAI services (context builder, risk calculator, care gap detector).

Tests appointment context building, risk assessment, and care gap detection
with mocked FHIR responses.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.api.services.appoint_ready.context_builder import context_builder, AppointReadyContextBuilder
from src.api.services.appoint_ready.risk_calculator import risk_calculator, RiskCalculator
from src.api.services.appoint_ready.care_gap_detector import care_gap_detector, CareGapDetector


# Mark all tests in this file
pytestmark = [pytest.mark.unit, pytest.mark.contextai]


class TestContextBuilder:
    """Test suite for AppointReadyContextBuilder service."""

    def test_context_builder_instance(self):
        """Test that context_builder is properly instantiated."""
        assert context_builder is not None
        assert isinstance(context_builder, AppointReadyContextBuilder)

    @pytest.mark.asyncio
    async def test_build_context_basic(
        self,
        test_patient,
        test_appointment,
        mock_fhir_patient_data,
        mock_fhir_medications,
        mock_fhir_conditions,
    ):
        """Test basic context building with mocked FHIR data."""
        # Arrange
        patient_id = str(test_patient.id)
        appointment_id = str(test_appointment.id)

        # Mock FHIR client
        with patch.object(context_builder, 'fhir_client') as mock_fhir:
            mock_fhir.get_patient = AsyncMock(return_value=mock_fhir_patient_data)
            mock_fhir.get_medications = AsyncMock(return_value=mock_fhir_medications)
            mock_fhir.get_conditions = AsyncMock(return_value=mock_fhir_conditions)
            mock_fhir.get_observations = AsyncMock(return_value=[])
            mock_fhir.get_allergies = AsyncMock(return_value=[])

            # Act
            result = await context_builder.build_context(
                patient_id=patient_id,
                appointment_id=appointment_id,
                include_medications=True,
                include_conditions=True,
                include_labs=False,
            )

            # Assert
            assert result is not None
            assert "patient_demographics" in result
            assert "medications" in result
            assert "conditions" in result
            assert len(result["medications"]) == 2
            assert len(result["conditions"]) == 2
            mock_fhir.get_patient.assert_called_once()
            mock_fhir.get_medications.assert_called_once()
            mock_fhir.get_conditions.assert_called_once()

    @pytest.mark.asyncio
    async def test_build_context_with_labs(
        self,
        test_patient,
        test_appointment,
        mock_fhir_patient_data,
        mock_fhir_observations,
    ):
        """Test context building including laboratory results."""
        # Arrange
        patient_id = str(test_patient.id)
        appointment_id = str(test_appointment.id)

        # Mock FHIR client
        with patch.object(context_builder, 'fhir_client') as mock_fhir:
            mock_fhir.get_patient = AsyncMock(return_value=mock_fhir_patient_data)
            mock_fhir.get_medications = AsyncMock(return_value=[])
            mock_fhir.get_conditions = AsyncMock(return_value=[])
            mock_fhir.get_observations = AsyncMock(return_value=mock_fhir_observations)
            mock_fhir.get_allergies = AsyncMock(return_value=[])

            # Act
            result = await context_builder.build_context(
                patient_id=patient_id,
                appointment_id=appointment_id,
                include_medications=False,
                include_conditions=False,
                include_labs=True,
            )

            # Assert
            assert "recent_labs" in result
            assert len(result["recent_labs"]) == 2
            # Check that A1c observation is included
            assert any("A1c" in str(obs.get("code", {}).get("text", "")) for obs in result["recent_labs"])
            mock_fhir.get_observations.assert_called_once()

    @pytest.mark.asyncio
    async def test_build_context_parallel_fetching(
        self,
        test_patient,
        test_appointment,
        mock_fhir_patient_data,
        mock_fhir_medications,
        mock_fhir_conditions,
        mock_fhir_observations,
    ):
        """Test that context data is fetched in parallel for performance."""
        # Arrange
        patient_id = str(test_patient.id)
        appointment_id = str(test_appointment.id)

        # Track call order to verify parallelism
        call_times = {}

        async def mock_get_patient(*args, **kwargs):
            call_times['patient'] = datetime.utcnow()
            return mock_fhir_patient_data

        async def mock_get_meds(*args, **kwargs):
            call_times['medications'] = datetime.utcnow()
            return mock_fhir_medications

        async def mock_get_conds(*args, **kwargs):
            call_times['conditions'] = datetime.utcnow()
            return mock_fhir_conditions

        # Mock FHIR client
        with patch.object(context_builder, 'fhir_client') as mock_fhir:
            mock_fhir.get_patient = mock_get_patient
            mock_fhir.get_medications = mock_get_meds
            mock_fhir.get_conditions = mock_get_conds
            mock_fhir.get_observations = AsyncMock(return_value=[])
            mock_fhir.get_allergies = AsyncMock(return_value=[])

            # Act
            result = await context_builder.build_context(
                patient_id=patient_id,
                appointment_id=appointment_id,
                include_medications=True,
                include_conditions=True,
                include_labs=False,
            )

            # Assert
            assert len(call_times) >= 3  # At least patient, meds, conditions called
            # All calls should be within a short time window (parallel execution)
            if len(call_times) > 1:
                times = list(call_times.values())
                time_diff = max(times) - min(times)
                assert time_diff.total_seconds() < 0.5  # Should complete within 500ms

    @pytest.mark.asyncio
    async def test_build_context_missing_patient(self, test_appointment):
        """Test context building when patient not found."""
        # Arrange
        patient_id = "non-existent-patient-id"
        appointment_id = str(test_appointment.id)

        # Mock FHIR client to return None
        with patch.object(context_builder, 'fhir_client') as mock_fhir:
            mock_fhir.get_patient = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(ValueError, match=".*patient.*not found.*"):
                await context_builder.build_context(
                    patient_id=patient_id,
                    appointment_id=appointment_id,
                )


class TestRiskCalculator:
    """Test suite for RiskCalculator service."""

    def test_risk_calculator_instance(self):
        """Test that risk_calculator is properly instantiated."""
        assert risk_calculator is not None
        assert isinstance(risk_calculator, RiskCalculator)

    @pytest.mark.asyncio
    async def test_calculate_risk_low(
        self,
        test_patient,
        mock_fhir_patient_data,
    ):
        """Test risk calculation for low-risk patient."""
        # Arrange
        patient_id = str(test_patient.id)

        # Mock patient data with no chronic conditions
        healthy_patient = mock_fhir_patient_data.copy()

        # Mock FHIR client
        with patch.object(risk_calculator, 'fhir_client') as mock_fhir:
            mock_fhir.get_patient = AsyncMock(return_value=healthy_patient)
            mock_fhir.get_conditions = AsyncMock(return_value=[])
            mock_fhir.get_medications = AsyncMock(return_value=[])
            mock_fhir.get_observations = AsyncMock(return_value=[])

            # Act
            result = await risk_calculator.calculate_risk(patient_id=patient_id)

            # Assert
            assert result is not None
            assert "risk_score" in result
            assert "risk_level" in result
            assert "risk_factors" in result
            assert result["risk_level"] in ["low", "moderate", "high", "critical"]
            assert result["risk_level"] == "low"
            assert 0 <= result["risk_score"] <= 100

    @pytest.mark.asyncio
    async def test_calculate_risk_high(
        self,
        test_patient,
        mock_fhir_patient_data,
        mock_fhir_conditions,
        mock_fhir_medications,
        mock_fhir_observations,
    ):
        """Test risk calculation for high-risk patient with multiple conditions."""
        # Arrange
        patient_id = str(test_patient.id)

        # Mock FHIR client with high-risk data
        with patch.object(risk_calculator, 'fhir_client') as mock_fhir:
            mock_fhir.get_patient = AsyncMock(return_value=mock_fhir_patient_data)
            mock_fhir.get_conditions = AsyncMock(return_value=mock_fhir_conditions)
            mock_fhir.get_medications = AsyncMock(return_value=mock_fhir_medications)
            mock_fhir.get_observations = AsyncMock(return_value=mock_fhir_observations)

            # Act
            result = await risk_calculator.calculate_risk(patient_id=patient_id)

            # Assert
            assert result["risk_level"] in ["moderate", "high", "critical"]
            assert result["risk_score"] > 30  # Should have elevated risk
            assert len(result["risk_factors"]) > 0
            # Should detect diabetes and hypertension as risk factors
            risk_factor_text = " ".join([rf.get("description", "") for rf in result["risk_factors"]])
            assert "diabetes" in risk_factor_text.lower() or "hypertension" in risk_factor_text.lower()

    @pytest.mark.asyncio
    async def test_calculate_risk_factors_identification(
        self,
        test_patient,
        mock_fhir_conditions,
    ):
        """Test that risk factors are properly identified."""
        # Arrange
        patient_id = str(test_patient.id)

        # Mock FHIR client
        with patch.object(risk_calculator, 'fhir_client') as mock_fhir:
            mock_fhir.get_patient = AsyncMock(return_value={})
            mock_fhir.get_conditions = AsyncMock(return_value=mock_fhir_conditions)
            mock_fhir.get_medications = AsyncMock(return_value=[])
            mock_fhir.get_observations = AsyncMock(return_value=[])

            # Act
            result = await risk_calculator.calculate_risk(patient_id=patient_id)

            # Assert
            assert len(result["risk_factors"]) >= 2  # Diabetes and Hypertension
            risk_factors = [rf.get("factor") for rf in result["risk_factors"]]
            assert any("diabetes" in str(rf).lower() for rf in risk_factors)
            assert any("hypertension" in str(rf).lower() for rf in risk_factors)

    @pytest.mark.asyncio
    async def test_calculate_risk_with_abnormal_labs(
        self,
        test_patient,
        mock_fhir_observations,
    ):
        """Test risk calculation considering abnormal lab values."""
        # Arrange
        patient_id = str(test_patient.id)

        # Mock FHIR client
        with patch.object(risk_calculator, 'fhir_client') as mock_fhir:
            mock_fhir.get_patient = AsyncMock(return_value={})
            mock_fhir.get_conditions = AsyncMock(return_value=[])
            mock_fhir.get_medications = AsyncMock(return_value=[])
            mock_fhir.get_observations = AsyncMock(return_value=mock_fhir_observations)

            # Act
            result = await risk_calculator.calculate_risk(patient_id=patient_id)

            # Assert
            # Should detect elevated A1c (7.2%) and high blood pressure (140/90)
            assert result["risk_score"] > 20  # Abnormal labs should increase risk


class TestCareGapDetector:
    """Test suite for CareGapDetector service."""

    def test_care_gap_detector_instance(self):
        """Test that care_gap_detector is properly instantiated."""
        assert care_gap_detector is not None
        assert isinstance(care_gap_detector, CareGapDetector)

    @pytest.mark.asyncio
    async def test_detect_care_gaps_diabetic_patient(
        self,
        test_patient,
        mock_fhir_conditions,
    ):
        """Test care gap detection for diabetic patient."""
        # Arrange
        patient_id = str(test_patient.id)

        # Mock FHIR client
        with patch.object(care_gap_detector, 'fhir_client') as mock_fhir:
            mock_fhir.get_conditions = AsyncMock(return_value=mock_fhir_conditions)
            mock_fhir.get_observations = AsyncMock(return_value=[])

            # Act
            result = await care_gap_detector.detect_care_gaps(patient_id=patient_id)

            # Assert
            assert result is not None
            assert "care_gaps" in result
            assert isinstance(result["care_gaps"], list)
            # Should detect missing A1c test for diabetic patient
            care_gap_descriptions = [gap.get("description", "") for gap in result["care_gaps"]]
            assert any("A1c" in desc or "diabetes" in desc.lower() for desc in care_gap_descriptions)

    @pytest.mark.asyncio
    async def test_detect_care_gaps_hypertensive_patient(
        self,
        test_patient,
        mock_fhir_conditions,
    ):
        """Test care gap detection for patient with hypertension."""
        # Arrange
        patient_id = str(test_patient.id)

        # Mock FHIR client with hypertension
        hypertension_conditions = [
            {
                "resourceType": "Condition",
                "id": "cond-1",
                "code": {"text": "Hypertension"},
                "clinicalStatus": {"coding": [{"code": "active"}]},
            }
        ]

        with patch.object(care_gap_detector, 'fhir_client') as mock_fhir:
            mock_fhir.get_conditions = AsyncMock(return_value=hypertension_conditions)
            mock_fhir.get_observations = AsyncMock(return_value=[])

            # Act
            result = await care_gap_detector.detect_care_gaps(patient_id=patient_id)

            # Assert
            # Should detect missing blood pressure monitoring
            assert len(result["care_gaps"]) > 0
            gap_text = " ".join([gap.get("description", "") for gap in result["care_gaps"]])
            assert "blood pressure" in gap_text.lower() or "hypertension" in gap_text.lower()

    @pytest.mark.asyncio
    async def test_detect_care_gaps_preventive_screenings(
        self,
        test_patient,
    ):
        """Test detection of missing preventive screenings."""
        # Arrange
        patient_id = str(test_patient.id)

        # Mock FHIR client with older patient (eligible for screenings)
        patient_data = {
            "resourceType": "Patient",
            "id": patient_id,
            "birthDate": "1960-01-01",  # 64 years old
            "gender": "male",
        }

        with patch.object(care_gap_detector, 'fhir_client') as mock_fhir:
            mock_fhir.get_patient = AsyncMock(return_value=patient_data)
            mock_fhir.get_conditions = AsyncMock(return_value=[])
            mock_fhir.get_observations = AsyncMock(return_value=[])

            # Act
            result = await care_gap_detector.detect_care_gaps(patient_id=patient_id)

            # Assert
            # Should detect missing age-appropriate screenings
            assert len(result["care_gaps"]) > 0

    @pytest.mark.asyncio
    async def test_detect_care_gaps_no_gaps(
        self,
        test_patient,
        mock_fhir_observations,
    ):
        """Test care gap detection when patient is up to date."""
        # Arrange
        patient_id = str(test_patient.id)

        # Mock FHIR client with recent labs
        with patch.object(care_gap_detector, 'fhir_client') as mock_fhir:
            mock_fhir.get_conditions = AsyncMock(return_value=[])
            mock_fhir.get_observations = AsyncMock(return_value=mock_fhir_observations)

            # Act
            result = await care_gap_detector.detect_care_gaps(patient_id=patient_id)

            # Assert
            assert "care_gaps" in result
            # May have some gaps, but recent labs should reduce them
            assert isinstance(result["care_gaps"], list)

    @pytest.mark.asyncio
    async def test_prioritize_care_gaps(
        self,
        test_patient,
        mock_fhir_conditions,
    ):
        """Test that care gaps are prioritized by severity."""
        # Arrange
        patient_id = str(test_patient.id)

        # Mock FHIR client
        with patch.object(care_gap_detector, 'fhir_client') as mock_fhir:
            mock_fhir.get_conditions = AsyncMock(return_value=mock_fhir_conditions)
            mock_fhir.get_observations = AsyncMock(return_value=[])

            # Act
            result = await care_gap_detector.detect_care_gaps(patient_id=patient_id)

            # Assert
            if len(result["care_gaps"]) > 1:
                # Care gaps should have priority field
                assert all("priority" in gap for gap in result["care_gaps"])
                priorities = [gap.get("priority") for gap in result["care_gaps"]]
                assert all(p in ["low", "medium", "high", "critical"] for p in priorities)


class TestContextAIServiceIntegration:
    """Integration tests between ContextAI services."""

    @pytest.mark.asyncio
    async def test_full_context_with_risk_and_gaps(
        self,
        test_patient,
        test_appointment,
        mock_fhir_patient_data,
        mock_fhir_conditions,
        mock_fhir_medications,
        mock_fhir_observations,
    ):
        """Test complete ContextAI workflow: context + risk + care gaps."""
        # Arrange
        patient_id = str(test_patient.id)
        appointment_id = str(test_appointment.id)

        # Mock FHIR client for all services
        with patch.object(context_builder, 'fhir_client') as mock_context_fhir, \
             patch.object(risk_calculator, 'fhir_client') as mock_risk_fhir, \
             patch.object(care_gap_detector, 'fhir_client') as mock_gap_fhir:

            # Set up mocks for context builder
            mock_context_fhir.get_patient = AsyncMock(return_value=mock_fhir_patient_data)
            mock_context_fhir.get_medications = AsyncMock(return_value=mock_fhir_medications)
            mock_context_fhir.get_conditions = AsyncMock(return_value=mock_fhir_conditions)
            mock_context_fhir.get_observations = AsyncMock(return_value=mock_fhir_observations)
            mock_context_fhir.get_allergies = AsyncMock(return_value=[])

            # Set up mocks for risk calculator
            mock_risk_fhir.get_patient = AsyncMock(return_value=mock_fhir_patient_data)
            mock_risk_fhir.get_conditions = AsyncMock(return_value=mock_fhir_conditions)
            mock_risk_fhir.get_medications = AsyncMock(return_value=mock_fhir_medications)
            mock_risk_fhir.get_observations = AsyncMock(return_value=mock_fhir_observations)

            # Set up mocks for care gap detector
            mock_gap_fhir.get_conditions = AsyncMock(return_value=mock_fhir_conditions)
            mock_gap_fhir.get_observations = AsyncMock(return_value=mock_fhir_observations)

            # Act - Execute all three services
            context = await context_builder.build_context(
                patient_id=patient_id,
                appointment_id=appointment_id,
                include_medications=True,
                include_conditions=True,
                include_labs=True,
            )
            risk = await risk_calculator.calculate_risk(patient_id=patient_id)
            gaps = await care_gap_detector.detect_care_gaps(patient_id=patient_id)

            # Assert - All services should provide complementary data
            assert context is not None
            assert risk is not None
            assert gaps is not None

            # Context should include patient data
            assert len(context["medications"]) == 2
            assert len(context["conditions"]) == 2

            # Risk should reflect chronic conditions
            assert risk["risk_level"] in ["moderate", "high", "critical"]
            assert len(risk["risk_factors"]) > 0

            # Care gaps should be detected for chronic disease management
            assert len(gaps["care_gaps"]) > 0
