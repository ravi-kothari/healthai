"""
Integration tests for CarePrep API endpoints.

Tests the complete request/response cycle for symptom analysis,
triage assessment, and questionnaire generation endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

# Mark all tests in this file
pytestmark = [pytest.mark.integration, pytest.mark.careprep]


class TestCarePrep SymptomAnalysisAPI:
    """Test suite for /api/careprep/analyze-symptoms endpoint."""

    def test_analyze_symptoms_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
    ):
        """Test successful symptom analysis."""
        # Arrange
        payload = {
            "symptoms": [
                {
                    "name": "Headache",
                    "severity": "moderate",
                    "duration": "2 days",
                    "description": "Throbbing pain in temples",
                }
            ],
            "patient_id": str(test_patient.id),
        }

        # Act
        response = client.post(
            "/api/careprep/analyze-symptoms",
            json=payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "urgency" in data
        assert "likely_conditions" in data
        assert "recommendations" in data
        assert "red_flags" in data
        assert data["urgency"] in ["routine", "moderate", "urgent", "emergency", "critical"]

    def test_analyze_symptoms_multiple(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
    ):
        """Test symptom analysis with multiple symptoms."""
        # Arrange
        payload = {
            "symptoms": [
                {
                    "name": "Fever",
                    "severity": "moderate",
                    "duration": "2 days",
                    "description": "Temperature 101°F",
                },
                {
                    "name": "Cough",
                    "severity": "moderate",
                    "duration": "3 days",
                    "description": "Persistent dry cough",
                },
                {
                    "name": "Fatigue",
                    "severity": "mild",
                    "duration": "3 days",
                    "description": "Feeling tired",
                },
            ],
            "patient_id": str(test_patient.id),
        }

        # Act
        response = client.post(
            "/api/careprep/analyze-symptoms",
            json=payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["likely_conditions"]) > 0
        assert len(data["recommendations"]) > 0

    def test_analyze_symptoms_unauthorized(
        self,
        client: TestClient,
        test_patient,
    ):
        """Test symptom analysis without authentication."""
        # Arrange
        payload = {
            "symptoms": [
                {
                    "name": "Headache",
                    "severity": "moderate",
                    "duration": "2 days",
                    "description": "Pain",
                }
            ],
            "patient_id": str(test_patient.id),
        }

        # Act
        response = client.post(
            "/api/careprep/analyze-symptoms",
            json=payload,
        )

        # Assert
        assert response.status_code == 401  # Unauthorized

    def test_analyze_symptoms_invalid_payload(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
    ):
        """Test symptom analysis with invalid payload."""
        # Arrange
        payload = {
            "symptoms": [],  # Empty symptoms list - should fail
        }

        # Act
        response = client.post(
            "/api/careprep/analyze-symptoms",
            json=payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 422  # Validation error

    def test_analyze_symptoms_missing_fields(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
    ):
        """Test symptom analysis with missing required fields."""
        # Arrange
        payload = {
            "symptoms": [
                {
                    "name": "Headache",
                    # Missing severity, duration, description
                }
            ],
        }

        # Act
        response = client.post(
            "/api/careprep/analyze-symptoms",
            json=payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 422  # Validation error


class TestCarePrepTriageAPI:
    """Test suite for /api/careprep/triage-assessment endpoint."""

    def test_triage_assessment_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
    ):
        """Test successful triage assessment."""
        # Arrange
        payload = {
            "chief_complaint": "Headache",
            "symptoms": [
                {
                    "name": "Headache",
                    "severity": "moderate",
                    "duration": "2 days",
                    "description": "Persistent headache",
                }
            ],
            "vital_signs": {
                "blood_pressure_systolic": 120,
                "blood_pressure_diastolic": 80,
                "heart_rate": 75,
                "temperature": 98.6,
                "respiratory_rate": 16,
            },
            "patient_id": str(test_patient.id),
        }

        # Act
        response = client.post(
            "/api/careprep/triage-assessment",
            json=payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "triage_level" in data
        assert "urgency" in data
        assert "severity_score" in data
        assert "red_flags" in data
        assert "recommended_action" in data
        assert data["triage_level"] in [1, 2, 3, 4, 5]
        assert data["urgency"] in ["routine", "moderate", "urgent", "emergency", "critical"]

    def test_triage_assessment_emergency(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
    ):
        """Test triage assessment for emergency case."""
        # Arrange
        payload = {
            "chief_complaint": "Severe chest pain",
            "symptoms": [
                {
                    "name": "Chest pain",
                    "severity": "severe",
                    "duration": "30 minutes",
                    "description": "Sharp pain radiating to left arm",
                }
            ],
            "vital_signs": {
                "blood_pressure_systolic": 160,
                "blood_pressure_diastolic": 100,
                "heart_rate": 120,
                "temperature": 98.6,
                "respiratory_rate": 24,
            },
            "patient_id": str(test_patient.id),
        }

        # Act
        response = client.post(
            "/api/careprep/triage-assessment",
            json=payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["urgency"] in ["emergency", "critical"]
        assert data["triage_level"] in [1, 2]  # High priority
        assert len(data["red_flags"]) > 0

    def test_triage_assessment_no_vitals(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
    ):
        """Test triage assessment without vital signs."""
        # Arrange
        payload = {
            "chief_complaint": "Headache",
            "symptoms": [
                {
                    "name": "Headache",
                    "severity": "moderate",
                    "duration": "2 days",
                    "description": "Persistent headache",
                }
            ],
            "patient_id": str(test_patient.id),
            # No vital_signs provided
        }

        # Act
        response = client.post(
            "/api/careprep/triage-assessment",
            json=payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200  # Should still work without vitals
        data = response.json()
        assert "triage_level" in data


class TestCarePrepQuestionnaireAPI:
    """Test suite for /api/careprep/generate-questionnaire endpoint."""

    def test_generate_questionnaire_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
    ):
        """Test successful questionnaire generation."""
        # Arrange
        payload = {
            "chief_complaint": "Headache",
            "symptoms": [],
        }

        # Act
        response = client.post(
            "/api/careprep/generate-questionnaire",
            json=payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert isinstance(data["questions"], list)
        assert len(data["questions"]) > 0

        # Verify question structure
        first_question = data["questions"][0]
        assert "id" in first_question
        assert "text" in first_question
        assert "type" in first_question
        assert first_question["type"] in ["text", "select", "multiselect", "number", "date"]

    def test_generate_questionnaire_with_symptoms(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
    ):
        """Test questionnaire generation with existing symptoms."""
        # Arrange
        payload = {
            "chief_complaint": "Headache",
            "symptoms": [
                {
                    "name": "Headache",
                    "severity": "moderate",
                    "duration": "2 days",
                    "description": "Throbbing temples",
                }
            ],
        }

        # Act
        response = client.post(
            "/api/careprep/generate-questionnaire",
            json=payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["questions"]) > 0


class TestCarePrepPatientSummaryAPI:
    """Test suite for /api/careprep/{patient_id}/summary endpoint."""

    def test_get_patient_summary_success(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
        test_appointment,
    ):
        """Test successful patient summary retrieval."""
        # Act
        response = client.get(
            f"/api/careprep/{test_patient.id}/summary",
            headers=auth_headers,
            params={"appointment_id": str(test_appointment.id)},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "patient" in data
        assert "appointment" in data
        assert "previsit_data" in data or "careprep_data" in data

    def test_get_patient_summary_not_found(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
    ):
        """Test patient summary for non-existent patient."""
        # Act
        response = client.get(
            "/api/careprep/non-existent-id/summary",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 404  # Not found

    def test_get_patient_summary_unauthorized(
        self,
        client: TestClient,
        test_patient,
    ):
        """Test patient summary without authentication."""
        # Act
        response = client.get(
            f"/api/careprep/{test_patient.id}/summary",
        )

        # Assert
        assert response.status_code == 401  # Unauthorized


class TestCarePrepEndToEnd:
    """End-to-end tests for complete CarePrep workflow."""

    def test_complete_careprep_flow(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        test_patient,
    ):
        """Test complete CarePrep workflow from symptom entry to triage."""
        # Step 1: Generate questionnaire
        questionnaire_payload = {
            "chief_complaint": "Fever and cough",
            "symptoms": [],
        }

        questionnaire_response = client.post(
            "/api/careprep/generate-questionnaire",
            json=questionnaire_payload,
            headers=auth_headers,
        )
        assert questionnaire_response.status_code == 200
        questionnaire = questionnaire_response.json()
        assert len(questionnaire["questions"]) > 0

        # Step 2: Analyze symptoms
        analysis_payload = {
            "symptoms": [
                {
                    "name": "Fever",
                    "severity": "moderate",
                    "duration": "2 days",
                    "description": "Temperature 101°F",
                },
                {
                    "name": "Cough",
                    "severity": "moderate",
                    "duration": "3 days",
                    "description": "Dry cough",
                },
            ],
            "patient_id": str(test_patient.id),
        }

        analysis_response = client.post(
            "/api/careprep/analyze-symptoms",
            json=analysis_payload,
            headers=auth_headers,
        )
        assert analysis_response.status_code == 200
        analysis = analysis_response.json()
        assert "urgency" in analysis

        # Step 3: Perform triage assessment
        triage_payload = {
            "chief_complaint": "Fever and cough",
            "symptoms": analysis_payload["symptoms"],
            "vital_signs": {
                "blood_pressure_systolic": 125,
                "blood_pressure_diastolic": 82,
                "heart_rate": 85,
                "temperature": 101.0,
                "respiratory_rate": 18,
            },
            "patient_id": str(test_patient.id),
        }

        triage_response = client.post(
            "/api/careprep/triage-assessment",
            json=triage_payload,
            headers=auth_headers,
        )
        assert triage_response.status_code == 200
        triage = triage_response.json()
        assert "triage_level" in triage
        assert "urgency" in triage

        # Verify consistency between analysis and triage
        # Both should indicate moderate urgency for this case
        assert analysis["urgency"] in ["moderate", "urgent"]
        assert triage["urgency"] in ["moderate", "urgent"]
