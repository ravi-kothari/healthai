import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.api.main import app
from src.api.models.user import User, UserRole
from src.api.models.patient import Patient, Gender
from src.api.models.careprep import CarePrepResponse
from src.api.auth.dependencies import get_db
from src.api.database import Base
from datetime import datetime
import uuid



@pytest.fixture
def doctor_token(db_session):
    # Create a doctor user and return a token (mocked or real if using full auth flow)
    # For this test, we might need to mock the auth dependency or use a real token generator
    # Assuming we can mock the dependency override for simplicity in this unit/integration test
    pass

def test_context_rbac_denies_patient(client, db_session):
    # Create a patient user
    patient_user = User(
        id=str(uuid.uuid4()),
        email="patient@example.com",
        username="patient_user",
        full_name="Patient User",
        hashed_password="hashed",
        role=UserRole.PATIENT,
        is_active=True
    )
    db_session.add(patient_user)
    db_session.commit()

    # Mock authentication to return this patient
    app.dependency_overrides[get_db] = lambda: db_session
    
    # We need to override get_current_user or the permission checker
    # Since we want to test the permission checker, we should override get_current_user
    from src.api.auth.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: patient_user

    response = client.get(f"/api/contextai/context/{uuid.uuid4()}")
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

    # Clean up
    app.dependency_overrides = {}

def test_context_rbac_allows_doctor(client, db_session):
    # Create a doctor user
    doctor_user = User(
        id=str(uuid.uuid4()),
        email="doctor@example.com",
        username="doctor_user",
        full_name="Doctor User",
        hashed_password="hashed",
        role=UserRole.DOCTOR,
        is_active=True
    )
    db_session.add(doctor_user)
    db_session.commit()

    # Create a dummy patient
    patient = Patient(
        id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        first_name="Test",
        last_name="Patient",
        date_of_birth=datetime(1980, 1, 1),
        gender=Gender.MALE,
        mrn="MRN-TEST"
    )
    db_session.add(patient)
    db_session.commit()

    # Mock authentication
    from src.api.auth.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: doctor_user
    app.dependency_overrides[get_db] = lambda: db_session

    response = client.get(f"/api/contextai/context/{patient.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == patient.id
    assert "demographics" in data

    # Clean up
    app.dependency_overrides = {}

def test_context_includes_previsit_data(client, db_session):
    # Setup doctor and patient
    doctor_user = User(id=str(uuid.uuid4()), email="doc@test.com", username="doc_test", full_name="Doc Test", role=UserRole.DOCTOR, is_active=True, hashed_password="pw")
    patient = Patient(id=str(uuid.uuid4()), user_id=str(uuid.uuid4()), first_name="P", last_name="T", date_of_birth=datetime(1990, 1, 1), gender=Gender.FEMALE, mrn="MRN-PREVISIT")
    db_session.add_all([doctor_user, patient])
    db_session.commit()

    # Create a completed CarePrep response
    careprep = CarePrepResponse(
        id=str(uuid.uuid4()),
        patient_id=patient.id,
        appointment_id=str(uuid.uuid4()),
        all_tasks_completed=True,
        completed_at=datetime.utcnow(),
        symptom_checker_data={
            "chief_complaint": "Severe Headache",
            "analysis": {
                "triage_level": 2,
                "urgency": "urgent"
            },
            "symptoms": [{"name": "Headache"}]
        }
    )
    db_session.add(careprep)
    db_session.commit()

    # Mock auth
    from src.api.auth.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: doctor_user
    app.dependency_overrides[get_db] = lambda: db_session

    response = client.get(f"/api/contextai/context/{patient.id}?include_previsit=true")
    assert response.status_code == 200
    data = response.json()
    
    assert "previsit" in data
    assert data["previsit"]["has_responses"] is True
    assert data["previsit"]["chief_complaint"] == "Severe Headache"
    assert data["previsit"]["triage_level"] == 2

    # Clean up
    app.dependency_overrides = {}
