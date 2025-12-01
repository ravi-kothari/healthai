"""
Integration tests for complete PreVisit.ai workflow.
Tests the full flow from patient symptom submission to analysis and triage.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import AsyncMock, patch
import json

from src.api.models.user import User
from src.api.models.patient import Patient
from src.api.services.previsit.symptom_analyzer import symptom_analyzer


@pytest.mark.integration
@pytest.mark.previsit
class TestPreVisitCompleteFlow:
    """Integration tests for complete PreVisit.ai workflow."""



    @pytest.mark.asyncio
    async def test_complete_previsit_symptom_analysis_flow(
        self,
        client: TestClient,
        db_session: Session,
        test_patient: Patient,
        patient_auth_headers: dict,
        mock_openai_symptom_response: dict
    ):
        """Test complete flow: patient submits symptoms and receives analysis."""

        # Step 1: Patient submits symptoms
        symptom_data = {
            "symptoms": [
                {
                    "name": "Headache",
                    "severity": "moderate",
                    "duration": "2 days",
                    "description": "Throbbing pain in temples"
                },
                {
                    "name": "Fever",
                    "severity": "mild",
                    "duration": "1 day",
                    "description": "Low-grade fever around 100°F"
                }
            ],
            "patient_id": str(test_patient.id)
        }

        # Mock OpenAI service for symptom analysis
        with patch.object(
            symptom_analyzer.openai,
            'chat_completion',
            new=AsyncMock(return_value=mock_openai_symptom_response)
        ):
            response = client.post(
                "/api/careprep/analyze-symptoms",
                json=symptom_data,
                headers=patient_auth_headers
            )

        # Step 2: Verify response
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        # Verify analysis results
        assert data["urgency"] == "moderate"
        assert data["severity"] == "moderate"
        assert data["triage_level"] == 3
        assert "chief_complaint" in data
        assert len(data["possible_conditions"]) > 0
        assert len(data["recommendations"]) > 0
        assert len(data["red_flags"]) > 0

    @pytest.mark.asyncio
    async def test_complete_triage_assessment_flow(
        self,
        client: TestClient,
        db_session: Session,
        test_patient: Patient,
        patient_auth_headers: dict
    ):
        """Test complete triage assessment flow with vital signs."""

        triage_data = {
            "chief_complaint": "Chest pain",
            "symptoms": [
                {
                    "name": "Chest pain",
                    "severity": "moderate",
                    "duration": "1 hour",
                    "description": "Dull ache in center of chest"
                }
            ],
            "vital_signs": {
                "blood_pressure_systolic": 130,
                "blood_pressure_diastolic": 85,
                "heart_rate": 90,
                "temperature": 98.6,
                "respiratory_rate": 18
            },
            "patient_id": str(test_patient.id)
        }

        response = client.post(
            "/api/careprep/triage-assessment",
            json=triage_data,
            headers=patient_auth_headers
        )

        # Verify response
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        # Verify triage results
        assert "triage_level" in data
        assert "urgency" in data
        # assert "severity_score" in data
        assert isinstance(data["emergency_flags"], list)
        assert "recommended_action" in data

    @pytest.mark.asyncio
    async def test_questionnaire_generation_flow(
        self,
        client: TestClient,
        db_session: Session,
        patient_auth_headers: dict,
        mock_openai_questionnaire_response: dict
    ):
        """Test questionnaire generation based on chief complaint."""

        questionnaire_request = {
            "chief_complaint": "Headache and fever",
            "symptoms": ["Headache", "Fever", "Fatigue"]
        }

        # Mock OpenAI service for questionnaire generation
        with patch.object(
            symptom_analyzer.openai,
            'chat_completion',
            new=AsyncMock(return_value=mock_openai_questionnaire_response)
        ):
            response = client.post(
                "/api/careprep/generate-questionnaire",
                json=questionnaire_request,
                headers=patient_auth_headers
            )

        # Verify response
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        # Verify questionnaire
        assert "questions" in data
        questions = data["questions"]
        assert len(questions) > 0

        # Verify question structure
        for question in questions:
            assert "id" in question
            assert "type" in question
            assert "question" in question
            assert "required" in question

    @pytest.mark.asyncio
    async def test_unauthorized_access_to_previsit(self, client: TestClient):
        """Test that unauthenticated users cannot access PreVisit endpoints."""

        symptom_data = {
            "symptoms": [
                {
                    "name": "Headache",
                    "severity": "moderate",
                    "duration": "1 day"
                }
            ]
        }

        # No auth headers
        response = client.post("/api/careprep/analyze-symptoms", json=symptom_data)

        # Should return 401 Unauthorized
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @pytest.mark.asyncio
    async def test_invalid_symptom_data(
        self,
        client: TestClient,
        patient_auth_headers: dict
    ):
        """Test validation of invalid symptom data."""

        # Missing required fields
        invalid_data = {
            "symptoms": [
                {
                    "name": "Headache",
                    # Missing severity and duration
                }
            ]
        }

        response = client.post(
            "/api/careprep/analyze-symptoms",
            json=invalid_data,
            headers=patient_auth_headers
        )

        # Should return 422 Unprocessable Entity (validation error)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_empty_symptoms_list(
        self,
        client: TestClient,
        patient_auth_headers: dict
    ):
        """Test handling of empty symptoms list."""

        data = {
            "symptoms": []
        }

        response = client.post(
            "/api/careprep/analyze-symptoms",
            json=data,
            headers=patient_auth_headers
        )

        # Should return 400 Bad Request or 422
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


@pytest.mark.integration
@pytest.mark.previsit
class TestPreVisitPatientContext:
    """Test PreVisit functionality with patient context."""

    @pytest.mark.asyncio
    async def test_symptom_analysis_with_existing_patient(
        self,
        client: TestClient,
        db_session: Session,
        test_patient: Patient,
        patient_auth_headers: dict,
        mock_openai_symptom_response: dict
    ):
        """Test symptom analysis for existing patient with medical history."""

        symptom_data = {
            "symptoms": [
                {
                    "name": "Dizziness",
                    "severity": "moderate",
                    "duration": "2 hours",
                    "description": "Feeling lightheaded"
                }
            ],
            "patient_id": str(test_patient.id)
        }

        with patch.object(
            symptom_analyzer.openai,
            'chat_completion',
            new=AsyncMock(return_value=mock_openai_symptom_response)
        ):
            response = client.post(
                "/api/careprep/analyze-symptoms",
                json=symptom_data,
                headers=patient_auth_headers
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify analysis considers patient context
        assert "urgency" in data
        assert "recommendations" in data


@pytest.mark.integration
@pytest.mark.previsit
@pytest.mark.slow
class TestPreVisitPerformance:
    """Performance tests for PreVisit functionality."""

    @pytest.mark.asyncio
    async def test_symptom_analysis_response_time(
        self,
        client: TestClient,
        patient_auth_headers: dict,
        mock_openai_symptom_response: dict
    ):
        """Test that symptom analysis responds within acceptable time."""
        import time

        symptom_data = {
            "symptoms": [
                {
                    "name": "Headache",
                    "severity": "moderate",
                    "duration": "1 day"
                }
            ]
        }

        with patch.object(
            symptom_analyzer.openai,
            'chat_completion',
            new=AsyncMock(return_value=mock_openai_symptom_response)
        ):
            start_time = time.time()
            response = client.post(
                "/api/careprep/analyze-symptoms",
                json=symptom_data,
                headers=patient_auth_headers
            )
            end_time = time.time()

        # Response should be fast (under 2 seconds for mocked)
        response_time = end_time - start_time
        assert response_time < 2.0
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_multiple_concurrent_analyses(
        self,
        client: TestClient,
        patient_auth_headers: dict,
        mock_openai_symptom_response: dict
    ):
        """Test handling multiple concurrent symptom analyses."""
        import asyncio

        symptom_data = {
            "symptoms": [
                {
                    "name": "Cough",
                    "severity": "mild",
                    "duration": "2 days"
                }
            ]
        }

        with patch.object(
            symptom_analyzer.openai,
            'chat_completion',
            new=AsyncMock(return_value=mock_openai_symptom_response)
        ):
            # Simulate 5 concurrent requests
            responses = []
            for _ in range(5):
                response = client.post(
                    "/api/careprep/analyze-symptoms",
                    json=symptom_data,
                    headers=patient_auth_headers
                )
                responses.append(response)

        # All requests should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
