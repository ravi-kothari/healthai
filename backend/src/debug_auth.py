import sys
import os
sys.path.append('/app')

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.main import app
from src.api.config import settings
from src.api.database import Base, get_db
from src.api.models.user import User, UserRole
from src.api.auth.password import hash_password
from src.api.auth.jwt_handler import create_access_token, verify_token

from sqlalchemy.pool import StaticPool

# Use in-memory DB
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def debug_auth():
    print(f"DEBUG: JWT_SECRET: {settings.JWT_SECRET}")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Create user
        user = User(
            email="test_auth@example.com",
            username="test_auth",
            hashed_password=hash_password("password"),
            full_name="Test Auth",
            role=UserRole.DOCTOR,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"DEBUG: Created user: {user.id}, role: {user.role}")
        
        # Generate token
        token_data = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "role": user.role
        }
        token = create_access_token(token_data)
        print(f"DEBUG: Generated token: {token[:20]}...")
        
        # Verify token manually
        payload = verify_token(token)
        print(f"DEBUG: Verified payload: {payload}")
        
        # Test API endpoint
        client = TestClient(app)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try a real protected endpoint
        response = client.post(
            "/api/careprep/generate-questionnaire",
            headers=headers,
            json={
                "patient_id": "some-id", 
                "chief_complaint": "Headache",
                "symptoms": [{"name": "Headache", "severity": "moderate", "duration": "1 day"}]
            }
        )
        print(f"DEBUG: API Response Status: {response.status_code}")
        print(f"DEBUG: API Response Body: {response.json()}")
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_auth()
