import sys
import os
from sqlalchemy import text
from src.api.database import SessionLocal
from src.api.models.user import User
from src.api.models.patient import Patient
from src.api.models.appointment import Appointment
from src.api.models.careprep import CarePrepResponse
from src.api.auth.password import hash_password

def check_create_patient():
    db = SessionLocal()
    try:
        # Check if user exists
        user = db.query(User).filter(User.username == "newpatient").first()
        if not user:
            print("Creating newpatient user...")
            user = User(
                email="newpatient@example.com",
                username="newpatient",
                hashed_password=hash_password("SecurePass123!"),
                full_name="New Patient",
                role="patient",
                is_active=True,
                tenant_id="default" # Assuming default tenant for now, or we might need to fetch one
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"User created with ID: {user.id}")
        else:
            print(f"User newpatient already exists with ID: {user.id}")

        # Check if patient record exists (linked to user)
        # Note: Patient model might not have user_id if it's not fully linked yet, 
        # but let's assume standard linkage or create a standalone patient if needed.
        # Actually, looking at previous files, Patient model might be separate.
        # Let's just ensure the User exists for login purposes first.
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_create_patient()
