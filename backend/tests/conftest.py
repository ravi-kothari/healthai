"""
Pytest configuration and fixtures for backend testing.
Provides test database, client, authentication, and data fixtures.
"""

import os
import sys
import pytest
from typing import Generator, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, date

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.main import app
from src.api.database import Base, get_db
from src.api.config import Settings, settings
from src.api.auth.jwt_handler import create_access_token
from src.api.auth.password import hash_password
from src.api.models.user import User, UserRole
from src.api.models.patient import Patient, Gender
from src.api.models.appointment import Appointment, AppointmentType, AppointmentStatus
from src.api.models.tenant import Tenant, TenantStatus

# Test settings override
@pytest.fixture(scope="session")
def test_settings():
    """Override settings for testing."""
    return Settings(
        ENVIRONMENT="test",
        LOG_LEVEL="DEBUG",
        DATABASE_URL="sqlite:///:memory:",  # In-memory SQLite for tests
        REDIS_URL="redis://localhost:6379/1",  # Separate Redis DB for tests
        FHIR_SERVER_URL="http://localhost:8080/fhir",
        USE_MOCK_OPENAI=True,
        USE_MOCK_SPEECH=True,
        USE_MOCK_AUTH=True,
        JWT_SECRET="test-secret-key-change-in-production",
        JWT_ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        ENABLE_PREVISIT=True,
        ENABLE_APPOINT_READY=True,
        ENABLE_TRANSCRIPTION=True,
        ENABLE_FHIR=True,
    )






@pytest.fixture(scope="session")
def test_engine(test_settings):
    """Create test database engine."""
    engine = create_engine(
        test_settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


# Test database session factory
@pytest.fixture(scope="session")
def TestSessionLocal(test_engine):
    """Create test session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Database setup and teardown
@pytest.fixture(scope="function")
def db_session(test_engine, TestSessionLocal) -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    Rolls back changes after test completes.
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create a new session for the test
    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)

# ... (skip client fixture)

@pytest.fixture(scope="function")
def test_tenant(db_session: Session) -> Tenant:
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Organization",
        slug="test-org",
        email="admin@test-org.com",
        subscription_plan="professional",
        status=TenantStatus.ACTIVE,
        is_active=True
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant

@pytest.fixture
def test_user(db_session: Session, test_user_data: Dict[str, Any]) -> User:
    """
    Create a test provider user in the database.

    Returns:
        User: Created user object
    """
    user = User(
        email=test_user_data["email"],
        hashed_password=hash_password(test_user_data["password"]),
        full_name=test_user_data["full_name"],
        role=test_user_data["role"],
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# Override database dependency
@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create FastAPI test client with overridden database dependency.

    Usage:
        def test_endpoint(client):
            response = client.get("/api/patients")
            assert response.status_code == 200
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()


import uuid

# ... imports ...

import logging

# ... imports ...

# Test user fixtures
@pytest.fixture(scope="function")
def test_user_data() -> Dict[str, Any]:
    """Sample user data for testing."""
    uid = uuid.uuid4()
    email = f"test_{uid}@example.com"
    username = f"test_user_{uid}"
    logging.warning(f"DEBUG: Generated test_user_data email: {email}")
    return {
        "email": email,
        "username": username,
        "password": "TestPassword123!",
        "full_name": "Test User",
        "role": UserRole.DOCTOR,
    }


@pytest.fixture(scope="function")
def test_patient_user_data() -> Dict[str, Any]:
    """Sample patient user data for testing."""
    uid = uuid.uuid4()
    email = f"patient_{uid}@example.com"
    username = f"patient_user_{uid}"
    logging.warning(f"DEBUG: Generated test_patient_user_data email: {email}")
    return {
        "email": email,
        "username": username,
        "password": "PatientPass123!",
        "full_name": "Test Patient",
        "role": UserRole.PATIENT,
    }


@pytest.fixture(scope="function")
def test_user(db_session: Session, test_user_data: Dict[str, Any]) -> User:
    """
    Create a test provider user in the database.

    Returns:
        User: Created user object
    """
    # Check if user already exists
    existing_user = db_session.query(User).filter(User.email == test_user_data["email"]).first()
    if existing_user:
        return existing_user

    user = User(
        email=test_user_data["email"],
        username=test_user_data["username"],
        hashed_password=hash_password(test_user_data["password"]),
        full_name=test_user_data["full_name"],
        role=test_user_data["role"],
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_patient_user(db_session: Session, test_patient_user_data: Dict[str, Any]) -> User:
    """
    Create a test patient user in the database.

    Returns:
        User: Created patient user object
    """
    # Check if user already exists
    existing_user = db_session.query(User).filter(User.email == test_patient_user_data["email"]).first()
    if existing_user:
        return existing_user

    user = User(
        email=test_patient_user_data["email"],
        username=test_patient_user_data["username"],
        hashed_password=hash_password(test_patient_user_data["password"]),
        full_name=test_patient_user_data["full_name"],
        role=test_patient_user_data["role"],
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# Authentication fixtures
@pytest.fixture
def auth_token(test_user: User) -> str:
    """
    Generate JWT token for test provider user.

    Returns:
        str: JWT access token
    """
    token_data = {
        "sub": str(test_user.id),
        "user_id": str(test_user.id),
        "role": test_user.role,
    }
    print(f"DEBUG: auth_token using secret: {settings.JWT_SECRET}", flush=True)
    return create_access_token(token_data)


@pytest.fixture
def patient_auth_token(test_patient_user: User) -> str:
    """
    Generate JWT token for test patient user.

    Returns:
        str: JWT access token
    """
    token_data = {
        "sub": str(test_patient_user.id),
        "user_id": str(test_patient_user.id),
        "role": test_patient_user.role,
    }
    return create_access_token(token_data)


@pytest.fixture
def auth_headers(auth_token: str) -> Dict[str, str]:
    """
    Create authorization headers for provider user.

    Returns:
        dict: Headers with Bearer token
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def patient_auth_headers(patient_auth_token: str) -> Dict[str, str]:
    """
    Create authorization headers for patient user.

    Returns:
        dict: Headers with Bearer token
    """
    return {"Authorization": f"Bearer {patient_auth_token}"}


# Patient data fixtures
@pytest.fixture
def test_patient_data() -> Dict[str, Any]:
    """Sample patient data for testing."""
    return {
        "mrn": f"MRN-{uuid.uuid4()}",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": date(1980, 1, 15),
        "gender": Gender.MALE,
        "email": "john.doe@example.com",
        "address": "123 Main St",
        "city": "Boston",
        "state": "MA",
        "zip_code": "02101",
        "insurance_provider": "Blue Cross",
        "insurance_policy_number": "BC123456789",
    }


@pytest.fixture
def test_patient(db_session: Session, test_patient_data: Dict[str, Any], test_patient_user: User) -> Patient:
    """
    Create a test patient in the database.

    Returns:
        Patient: Created patient object
    """
    # Remove email if present as it's not in Patient model
    patient_data = test_patient_data.copy()
    if "email" in patient_data:
        patient_data.pop("email")
    
    patient = Patient(**patient_data)
    patient.user_id = test_patient_user.id
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


@pytest.fixture
def multiple_test_patients(db_session: Session) -> list[Patient]:
    """
    Create multiple test patients for list/pagination testing.

    Returns:
        list[Patient]: List of created patients
    """
    patients = []
    for i in range(5):
        patient = Patient(
            mrn=f"MRN-{i}-{uuid.uuid4()}",
            first_name=f"Patient{i}",
            last_name=f"Test{i}",
            date_of_birth=date(1980 + i, 1, 1),
            gender=Gender.MALE if i % 2 == 0 else Gender.FEMALE,
            # email and phone removed as they are not in Patient model
        )
        # Create user for patient
        user = User(
            email=f"patient{i}_{uuid.uuid4()}@test.com",
            username=f"patient_user{i}_{uuid.uuid4()}",
            hashed_password=hash_password("password"),
            full_name=f"Patient{i} Test{i}",
            role=UserRole.PATIENT,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        patient.user_id = user.id
        db_session.add(patient)
        patients.append(patient)

    db_session.commit()
    for patient in patients:
        db_session.refresh(patient)

    return patients


# Appointment fixtures
@pytest.fixture
def test_appointment_data(test_patient: Patient, test_user: User) -> Dict[str, Any]:
    """Sample appointment data for testing."""
    return {
        "patient_id": test_patient.id,
        "provider_id": test_user.id,
        "appointment_type": AppointmentType.ANNUAL_CHECKUP,
        "scheduled_start": datetime.utcnow() + timedelta(days=7),
        "scheduled_end": datetime.utcnow() + timedelta(days=7, minutes=30),
        "status": AppointmentStatus.SCHEDULED,
        "notes": "Patient requested morning appointment",
    }


@pytest.fixture
def test_appointment(
    db_session: Session,
    test_patient: Patient,
    test_user: User,
    test_appointment_data: Dict[str, Any]
) -> Appointment:
    """
    Create a test appointment in the database.

    Returns:
        Appointment: Created appointment object
    """

    
    appointment = Appointment(**test_appointment_data)
    db_session.add(appointment)
    db_session.commit()
    db_session.refresh(appointment)
    return appointment


# CarePrep fixtures
@pytest.fixture
def test_symptoms_data() -> Dict[str, Any]:
    """Sample symptoms data for CarePrep testing."""
    return {
        "symptoms": [
            {
                "name": "Headache",
                "severity": "moderate",
                "duration": "2 days",
                "description": "Throbbing pain in temples, worse in the morning",
            },
            {
                "name": "Fatigue",
                "severity": "mild",
                "duration": "1 week",
                "description": "Feeling tired throughout the day",
            },
        ],
        "patient_id": None,  # Will be set in tests
    }


@pytest.fixture
def test_triage_data() -> Dict[str, Any]:
    """Sample triage assessment data."""
    return {
        "chief_complaint": "Severe chest pain",
        "symptoms": [
            {
                "name": "Chest pain",
                "severity": "severe",
                "duration": "30 minutes",
                "description": "Sharp pain in center of chest, radiating to left arm",
            }
        ],
        "vital_signs": {
            "blood_pressure_systolic": 150,
            "blood_pressure_diastolic": 95,
            "heart_rate": 110,
            "temperature": 98.6,
            "respiratory_rate": 22,
        },
        "patient_id": None,  # Will be set in tests
    }


# Mock responses
@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for testing."""
    return {
        "urgency": "moderate",
        "likely_conditions": ["Tension headache", "Migraine"],
        "red_flags": [],
        "recommendations": [
            "Stay hydrated",
            "Get adequate rest",
            "Consider over-the-counter pain relief",
        ],
        "follow_up": "If symptoms persist for more than 3 days or worsen, schedule an appointment.",
    }


@pytest.fixture
def mock_openai_symptom_response():
    """Mock OpenAI response for symptom analysis."""
    import json
    return {
        'content': json.dumps({
            "urgency": "moderate",
            "severity": "moderate",
            "triage_level": 3,
            "chief_complaint": "Headache and fever",
            "summary": "Patient presents with moderate headache and mild fever. Possible viral infection.",
            "possible_conditions": [
                "Viral infection",
                "Tension headache",
                "Flu"
            ],
            "recommendations": [
                "Rest and stay hydrated",
                "Monitor temperature",
                "Take over-the-counter pain relief if needed",
                "Avoid strenuous activity"
            ],
            "red_flags": [
                "Fever above 103°F",
                "Severe headache",
                "Stiff neck",
                "Confusion"
            ],
            "follow_up": "If symptoms persist for more than 3 days or worsen, schedule an appointment"
        })
    }


@pytest.fixture
def mock_openai_questionnaire_response():
    """Mock OpenAI response for questionnaire generation."""
    import json
    return {
        'content': json.dumps({
            "questions": [
                {
                    "id": "q1",
                    "type": "scale",
                    "question": "On a scale of 1-10, how severe is your headache?",
                    "options": list(range(1, 11)),
                    "required": True
                },
                {
                    "id": "q2",
                    "type": "select",
                    "question": "Where is the pain located?",
                    "options": ["Front of head", "Back of head", "Temples", "All over"],
                    "required": True
                },
                {
                    "id": "q3",
                    "type": "multiselect",
                    "question": "What makes your headache worse?",
                    "options": ["Light", "Sound", "Movement", "Stress"],
                    "required": False
                },
                {
                    "id": "q4",
                    "type": "text",
                    "question": "Please describe any other symptoms you're experiencing",
                    "required": False
                }
            ]
        })
    }


@pytest.fixture
def mock_fhir_patient_data():
    """Mock FHIR Patient resource."""
    return {
        "resourceType": "Patient",
        "id": "example-123",
        "name": [{"given": ["John"], "family": "Doe"}],
        "gender": "male",
        "birthDate": "1980-01-15",
    }


# ContextAI fixtures
@pytest.fixture
def test_context_request_data(test_patient: Patient, test_appointment: Appointment) -> Dict[str, Any]:
    """Sample context request data for ContextAI testing."""
    return {
        "patient_id": str(test_patient.id),
        "appointment_id": str(test_appointment.id),
        "include_medications": True,
        "include_conditions": True,
        "include_labs": True,
        "include_care_gaps": True,
    }


@pytest.fixture
def mock_fhir_medications():
    """Mock FHIR MedicationStatement resources."""
    return [
        {
            "resourceType": "MedicationStatement",
            "id": "med-1",
            "medicationCodeableConcept": {
                "text": "Lisinopril 10mg"
            },
            "status": "active",
        },
        {
            "resourceType": "MedicationStatement",
            "id": "med-2",
            "medicationCodeableConcept": {
                "text": "Metformin 500mg"
            },
            "status": "active",
        },
    ]


@pytest.fixture
def mock_fhir_conditions():
    """Mock FHIR Condition resources."""
    return [
        {
            "resourceType": "Condition",
            "id": "cond-1",
            "code": {
                "text": "Type 2 Diabetes Mellitus"
            },
            "clinicalStatus": {
                "coding": [{"code": "active"}]
            },
        },
        {
            "resourceType": "Condition",
            "id": "cond-2",
            "code": {
                "text": "Hypertension"
            },
            "clinicalStatus": {
                "coding": [{"code": "active"}]
            },
        },
    ]


@pytest.fixture
def mock_fhir_observations():
    """Mock FHIR Observation resources (labs)."""
    return [
        {
            "resourceType": "Observation",
            "id": "obs-1",
            "code": {
                "text": "Hemoglobin A1c"
            },
            "valueQuantity": {
                "value": 7.2,
                "unit": "%"
            },
            "issued": "2024-10-15",
        },
        {
            "resourceType": "Observation",
            "id": "obs-2",
            "code": {
                "text": "Blood Pressure"
            },
            "component": [
                {"valueQuantity": {"value": 140, "unit": "mmHg"}},
                {"valueQuantity": {"value": 90, "unit": "mmHg"}},
            ],
            "issued": "2024-11-01",
        },
    ]


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, no external dependencies)")
    config.addinivalue_line("markers", "integration: Integration tests (may use database, external services)")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "auth: Authentication and authorization tests")
    config.addinivalue_line("markers", "careprep: CarePrep feature tests (patient preparation)")
    config.addinivalue_line("markers", "previsit: PreVisit feature tests")
    config.addinivalue_line("markers", "contextai: ContextAI feature tests (provider context)")
    config.addinivalue_line("markers", "fhir: FHIR integration tests")
