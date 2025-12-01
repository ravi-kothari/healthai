import pytest
from datetime import datetime, timedelta
from src.api.models.tenant import Tenant, SubscriptionPlan, SubscriptionStatus
from src.api.models.user import User, UserRole
from src.api.models.patient import Patient, Gender
from src.api.models.clinical import ClinicalDocument, DocumentType
from src.api.auth.jwt_handler import create_access_token

@pytest.fixture
def analytics_setup(db_session, test_tenant):
    """Setup data for analytics test."""
    # Create tenant admin
    admin = User(
        email="admin@analytics.com",
        username="admin_analytics",
        hashed_password="hashed_password",
        full_name="Admin Analytics",
        role=UserRole.ADMIN,
        tenant_id=test_tenant.id,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    
    # Create patient linked to admin
    patient = Patient(
        user_id=admin.id,
        mrn="MRN-ANALYTICS-001",
        first_name="Analytics",
        last_name="Patient",
        date_of_birth=datetime(1990, 1, 1).date(),
        gender=Gender.MALE
    )
    db_session.add(patient)
    db_session.commit()
    
    # Create documents
    docs = []
    # 2 Transcripts
    for i in range(2):
        doc = ClinicalDocument(
            patient_id=patient.id,
            title=f"Transcript {i}",
            document_type=DocumentType.CONSULTATION, # Using Consultation as proxy for transcript if not exact
            file_name=f"transcript_{i}.txt",
            file_size=1024,
            file_type="text/plain",
            uploaded_by="admin_analytics"
        )
        docs.append(doc)
        
    # 3 SOAP Notes (Other)
    for i in range(3):
        doc = ClinicalDocument(
            patient_id=patient.id,
            title=f"SOAP Note {i}",
            document_type=DocumentType.OTHER, # Using Other/Consultation
            file_name=f"soap_{i}.txt",
            file_size=2048,
            file_type="text/plain",
            uploaded_by="admin_analytics"
        )
        docs.append(doc)
        
    db_session.add_all(docs)
    db_session.commit()
    
    return {
        "tenant": test_tenant,
        "admin": admin,
        "patient": patient
    }

def test_get_tenant_analytics(client, analytics_setup):
    """Test getting tenant analytics."""
    setup = analytics_setup
    admin = setup["admin"]
    tenant = setup["tenant"]
    
    # Login as admin
    token = create_access_token(data={"sub": admin.id})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(f"/api/tenants/{tenant.id}/analytics", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["tenant_id"] == tenant.id
    assert data["period"] == "30d"
    
    # Check metrics
    metrics = data["metrics"]
    
    # Documents
    # We created 2 Consultation and 3 Other
    assert metrics["documents"]["consultation"] == 2
    assert metrics["documents"]["other"] == 3
    
    # Patients
    assert metrics["patients"]["total"] >= 1
    assert metrics["patients"]["new"] >= 1
