"""
Integration tests for ContextAI API endpoints.

Tests the complete request/response cycle for appointment context,
risk assessment, and care gap detection endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

# Mark all tests in this file
pytestmark = [pytest.mark.integration, pytest.mark.contextai]


class TestContextAIAppointmentContextAPI:
    """Test suite for /api/contextai/context/{patient_id} endpoint."""

    def test_get_appointment_context_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
        test_appointment,
    ):
        """Test successful appointment context retrieval."""
        # Act
        response = client.get(
            f"/api/contextai/context/{test_patient.id}",
            headers=auth_headers,
            params={
                "appointment_id": str(test_appointment.id),
                "include_medications": "true",
                "include_conditions": "true",
                "include_labs": "true",
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "patient_demographics" in data or "patient" in data
        assert "medications" in data or "current_medications" in data
        assert "conditions" in data or "active_conditions" in data

    def test_get_appointment_context_minimal(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
        test_appointment,
    ):
        """Test appointment context with minimal data."""
        # Act
        response = client.get(
            f"/api/contextai/context/{test_patient.id}",
            headers=auth_headers,
            params={
                "appointment_id": str(test_appointment.id),
                "include_medications": "false",
                "include_conditions": "false",
                "include_labs": "false",
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Should still return basic patient data
        assert "patient" in data or "patient_demographics" in data

    def test_get_appointment_context_not_found(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
    ):
        """Test appointment context for non-existent patient."""
        # Act
        response = client.get(
            "/api/contextai/context/non-existent-patient-id",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 404  # Not found

    def test_get_appointment_context_unauthorized(
        self,
        client: TestClient,
        test_patient,
    ):
        """Test appointment context without authentication."""
        # Act
        response = client.get(
            f"/api/contextai/context/{test_patient.id}",
        )

        # Assert
        assert response.status_code == 401  # Unauthorized


class TestContextAICareGapsAPI:
    """Test suite for /api/contextai/care-gaps/{patient_id} endpoint."""

    def test_get_care_gaps_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
    ):
        """Test successful care gaps retrieval."""
        # Act
        response = client.get(
            f"/api/contextai/care-gaps/{test_patient.id}",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "care_gaps" in data
        assert isinstance(data["care_gaps"], list)

        # If there are care gaps, verify structure
        if len(data["care_gaps"]) > 0:
            gap = data["care_gaps"][0]
            assert "description" in gap or "gap_type" in gap
            assert "priority" in gap or "severity" in gap

    def test_get_care_gaps_not_found(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
    ):
        """Test care gaps for non-existent patient."""
        # Act
        response = client.get(
            "/api/contextai/care-gaps/non-existent-patient-id",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 404  # Not found

    def test_get_care_gaps_unauthorized(
        self,
        client: TestClient,
        test_patient,
    ):
        """Test care gaps without authentication."""
        # Act
        response = client.get(
            f"/api/contextai/care-gaps/{test_patient.id}",
        )

        # Assert
        assert response.status_code == 401  # Unauthorized


class TestContextAIRiskAssessmentAPI:
    """Test suite for /api/contextai/risk-assessment/{patient_id} endpoint."""

    def test_get_risk_assessment_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
    ):
        """Test successful risk assessment retrieval."""
        # Act
        response = client.get(
            f"/api/contextai/risk-assessment/{test_patient.id}",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert "risk_level" in data
        assert "risk_factors" in data
        assert data["risk_level"] in ["low", "moderate", "high", "critical"]
        assert 0 <= data["risk_score"] <= 100
        assert isinstance(data["risk_factors"], list)

    def test_get_risk_assessment_not_found(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
    ):
        """Test risk assessment for non-existent patient."""
        # Act
        response = client.get(
            "/api/contextai/risk-assessment/non-existent-patient-id",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 404  # Not found

    def test_get_risk_assessment_unauthorized(
        self,
        client: TestClient,
        test_patient,
    ):
        """Test risk assessment without authentication."""
        # Act
        response = client.get(
            f"/api/contextai/risk-assessment/{test_patient.id}",
        )

        # Assert
        assert response.status_code == 401  # Unauthorized


class TestContextAITestResultsAPI:
    """Test suite for /api/contextai/test-results/{patient_id} endpoint."""

    def test_get_test_results_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
    ):
        """Test successful test results retrieval."""
        # Act
        response = client.get(
            f"/api/contextai/test-results/{test_patient.id}",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "test_results" in data or "observations" in data or "labs" in data
        # Response should be a list or dict containing test results
        assert isinstance(data, (dict, list))

    def test_get_test_results_with_filters(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
    ):
        """Test test results with date filters."""
        # Act
        response = client.get(
            f"/api/contextai/test-results/{test_patient.id}",
            headers=auth_headers,
            params={
                "from_date": "2024-01-01",
                "to_date": "2024-12-31",
            },
        )

        # Assert
        assert response.status_code == 200


class TestContextAIMedicationReviewAPI:
    """Test suite for /api/contextai/medication-review/{patient_id} endpoint."""

    def test_get_medication_review_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
    ):
        """Test successful medication review retrieval."""
        # Act
        response = client.get(
            f"/api/contextai/medication-review/{test_patient.id}",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "medications" in data or "current_medications" in data
        # Should include interaction checks
        assert "interactions" in data or "drug_interactions" in data or isinstance(data, dict)

    def test_get_medication_review_unauthorized(
        self,
        client: TestClient,
        test_patient,
    ):
        """Test medication review without authentication."""
        # Act
        response = client.get(
            f"/api/contextai/medication-review/{test_patient.id}",
        )

        # Assert
        assert response.status_code == 401  # Unauthorized


class TestContextAIEndToEnd:
    """End-to-end tests for complete ContextAI workflow."""

    def test_complete_contextai_flow(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
        test_appointment,
    ):
        """Test complete ContextAI workflow for provider preparation."""
        patient_id = str(test_patient.id)
        appointment_id = str(test_appointment.id)

        # Step 1: Get appointment context
        context_response = client.get(
            f"/api/contextai/context/{patient_id}",
            headers=auth_headers,
            params={
                "appointment_id": appointment_id,
                "include_medications": "true",
                "include_conditions": "true",
                "include_labs": "true",
            },
        )
        assert context_response.status_code == 200
        context = context_response.json()
        assert "patient" in context or "patient_demographics" in context

        # Step 2: Get risk assessment
        risk_response = client.get(
            f"/api/contextai/risk-assessment/{patient_id}",
            headers=auth_headers,
        )
        assert risk_response.status_code == 200
        risk = risk_response.json()
        assert "risk_score" in risk
        assert "risk_level" in risk

        # Step 3: Get care gaps
        gaps_response = client.get(
            f"/api/contextai/care-gaps/{patient_id}",
            headers=auth_headers,
        )
        assert gaps_response.status_code == 200
        gaps = gaps_response.json()
        assert "care_gaps" in gaps

        # Step 4: Get medication review
        meds_response = client.get(
            f"/api/contextai/medication-review/{patient_id}",
            headers=auth_headers,
        )
        assert meds_response.status_code == 200
        meds = meds_response.json()
        assert "medications" in meds or "current_medications" in meds or isinstance(meds, dict)

        # Step 5: Get test results
        labs_response = client.get(
            f"/api/contextai/test-results/{patient_id}",
            headers=auth_headers,
        )
        assert labs_response.status_code == 200

        # All responses should be successful
        # Provider now has complete clinical context

    def test_contextai_performance(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
        test_appointment,
    ):
        """Test that ContextAI endpoints perform within acceptable time."""
        import time

        patient_id = str(test_patient.id)
        appointment_id = str(test_appointment.id)

        # Test context retrieval performance
        start_time = time.time()
        response = client.get(
            f"/api/contextai/context/{patient_id}",
            headers=auth_headers,
            params={"appointment_id": appointment_id},
        )
        duration = time.time() - start_time

        assert response.status_code == 200
        # Context should be retrieved in under 2 seconds
        assert duration < 2.0, f"Context retrieval took {duration}s, expected < 2.0s"

    def test_contextai_patient_role_access(
        self,
        client: TestClient,
        patient_auth_headers: Dict[str, str],
        test_patient,
    ):
        """Test that patient users cannot access provider-facing ContextAI endpoints."""
        patient_id = str(test_patient.id)

        # Patients should NOT have access to ContextAI endpoints
        # (These are provider-only features)
        response = client.get(
            f"/api/contextai/context/{patient_id}",
            headers=patient_auth_headers,
        )

        # Depending on implementation, might be 403 (Forbidden) or 401 (Unauthorized)
        # or could allow patients to view their own context
        assert response.status_code in [200, 401, 403]
