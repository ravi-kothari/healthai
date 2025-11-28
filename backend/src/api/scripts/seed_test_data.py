"""
Seed script to create test data for development and testing.

Creates:
- 1 test provider (doctor)
- 2 test patients
- 2 test appointments with CarePrep tokens
- Sample medical history and symptoms data

Usage:
    python -m src.api.scripts.seed_test_data
"""

import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import base64

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from src.api.database import SessionLocal, engine
from src.api.models.user import User, UserRole
from src.api.models.patient import Patient, Gender, BloodType
from src.api.models.appointment import Appointment, AppointmentStatus, AppointmentType
from src.api.models.careprep import CarePrepResponse
from src.api.models.tenant import Tenant, TenantStatus
from src.api.auth.password import hash_password


def create_test_tenant(db: Session):
    """Create default test tenant if it doesn't exist."""
    tenant_id = "defa0000-0000-0000-0000-000000000001"

    existing = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if existing:
        print(f"✓ Tenant already exists: {existing.name}")
        return existing

    tenant = Tenant(
        id=tenant_id,
        name="Default Organization",
        slug="default",
        subscription_plan="professional",
        status=TenantStatus.ACTIVE.value,
        is_active=True
    )
    db.add(tenant)
    db.commit()
    print(f"✓ Created tenant: {tenant.name}")
    return tenant


def create_test_provider(db: Session, tenant_id: str):
    """Create a test provider (doctor) user."""
    email = "doctor@healthai.com"

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"✓ Provider already exists: {existing.email}")
        return existing

    provider = User(
        email=email,
        username="doctor_smith",
        hashed_password=hash_password("Doctor123!"),
        full_name="Dr. Sarah Smith",
        phone="+1-555-0100",
        role=UserRole.DOCTOR,
        tenant_id=tenant_id,
        is_active=True,
        is_verified=True
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    print(f"✓ Created provider: {provider.email} (password: Doctor123!)")
    return provider


def create_test_patients(db: Session, tenant_id: str):
    """Create test patient users and patient records."""
    patients_data = [
        {
            "email": "patient1@example.com",
            "username": "john_patient",
            "password": "Patient123!",
            "full_name": "John Doe",
            "phone": "+1-555-0201",
            "first_name": "John",
            "last_name": "Doe",
            "mrn": "MRN001",
            "dob": datetime(1985, 5, 15).date(),
            "gender": Gender.MALE,
            "blood_type": BloodType.O_POSITIVE,
            "address": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94102",
            "allergies": ["Penicillin", "Peanuts"],
            "chronic_conditions": ["Hypertension", "Type 2 Diabetes"],
            "current_medications": ["Metformin 500mg", "Lisinopril 10mg"]
        },
        {
            "email": "patient2@example.com",
            "username": "jane_patient",
            "password": "Patient123!",
            "full_name": "Jane Smith",
            "phone": "+1-555-0202",
            "first_name": "Jane",
            "last_name": "Smith",
            "mrn": "MRN002",
            "dob": datetime(1990, 8, 22).date(),
            "gender": Gender.FEMALE,
            "blood_type": BloodType.A_POSITIVE,
            "address": "456 Oak Ave",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90001",
            "allergies": ["Sulfa drugs"],
            "chronic_conditions": ["Asthma"],
            "current_medications": ["Albuterol inhaler"]
        }
    ]

    created_patients = []

    for patient_data in patients_data:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == patient_data["email"]).first()
        if existing_user:
            print(f"✓ Patient user already exists: {existing_user.email}")
            # Get the patient record
            existing_patient = db.query(Patient).filter(Patient.user_id == existing_user.id).first()
            if existing_patient:
                created_patients.append(existing_patient)
                continue

        # Create user account
        user = User(
            email=patient_data["email"],
            username=patient_data["username"],
            hashed_password=hash_password(patient_data["password"]),
            full_name=patient_data["full_name"],
            phone=patient_data["phone"],
            role=UserRole.PATIENT,
            tenant_id=tenant_id,
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.flush()  # Get the user ID

        # Create patient record
        patient = Patient(
            user_id=user.id,
            mrn=patient_data["mrn"],
            first_name=patient_data["first_name"],
            last_name=patient_data["last_name"],
            date_of_birth=patient_data["dob"],
            gender=patient_data["gender"],
            blood_type=patient_data["blood_type"],
            address=patient_data["address"],
            city=patient_data["city"],
            state=patient_data["state"],
            zip_code=patient_data["zip_code"],
            emergency_contact_name=f"{patient_data['first_name']}'s Emergency Contact",
            emergency_contact_phone="+1-555-9999",
            emergency_contact_relationship="Spouse",
            insurance_provider="Blue Cross Blue Shield",
            insurance_policy_number=f"BCBS{patient_data['mrn']}",
            # Note: allergies, chronic_conditions, current_medications relationships handled separately
            notes=f"Test patient with allergies: {', '.join(patient_data['allergies'])}"
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        created_patients.append(patient)

        print(f"✓ Created patient: {user.email} (password: {patient_data['password']})")

    return created_patients


def create_test_appointments(db: Session, provider: User, patients: list):
    """Create test appointments with CarePrep tokens."""
    appointments_data = [
        {
            "patient": patients[0],
            "type": AppointmentType.FOLLOW_UP,
            "status": AppointmentStatus.SCHEDULED,
            "days_from_now": 3,
            "duration": 30,
            "chief_complaint": "Follow-up for diabetes management and blood pressure check",
            "token": "test_token_patient1_appt1"  # Simple token for testing
        },
        {
            "patient": patients[1],
            "type": AppointmentType.INITIAL_CONSULTATION,
            "status": AppointmentStatus.SCHEDULED,
            "days_from_now": 5,
            "duration": 45,
            "chief_complaint": "New patient consultation - asthma and seasonal allergies",
            "token": "test_token_patient2_appt1"  # Simple token for testing
        }
    ]

    created_appointments = []

    for appt_data in appointments_data:
        # Check if appointment already exists by checking for careprep token
        # For now, we'll just create new ones each time

        scheduled_start = datetime.now() + timedelta(days=appt_data["days_from_now"])
        scheduled_start = scheduled_start.replace(hour=10, minute=0, second=0, microsecond=0)
        scheduled_end = scheduled_start + timedelta(minutes=appt_data["duration"])

        appointment = Appointment(
            patient_id=appt_data["patient"].id,
            provider_id=provider.id,
            appointment_type=appt_data["type"],
            status=appt_data["status"],
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            duration_minutes=appt_data["duration"],
            chief_complaint=appt_data["chief_complaint"],
            previsit_completed="N"
        )
        db.add(appointment)
        db.flush()  # Get the appointment ID

        # Create CarePrepResponse with token
        careprep_response = CarePrepResponse(
            appointment_id=appointment.id,
            patient_id=appt_data["patient"].id,
            medical_history_completed=False,
            symptom_checker_completed=False,
            all_tasks_completed=False
        )
        db.add(careprep_response)

        db.commit()
        db.refresh(appointment)

        # Generate the token (base64 encoded appointment ID)
        token = base64.b64encode(appointment.id.encode()).decode()

        created_appointments.append({
            "appointment": appointment,
            "patient": appt_data["patient"],
            "token": token,
            "simple_token": appt_data["token"]
        })

        print(f"✓ Created appointment for {appt_data['patient'].full_name}")
        print(f"  - Scheduled: {scheduled_start.strftime('%Y-%m-%d %H:%M')}")
        print(f"  - Type: {appt_data['type'].value}")
        print(f"  - Token (base64): {token}")
        print(f"  - CarePrep URL: http://localhost:3000/careprep/{token}")
        print()

    return created_appointments


def print_summary(provider: User, patients: list, appointments: list):
    """Print summary of created test data."""
    print("\n" + "="*80)
    print("TEST DATA CREATED SUCCESSFULLY")
    print("="*80)

    print(f"\n📋 PROVIDER CREDENTIALS:")
    print(f"  Email: doctor@healthai.com")
    print(f"  Password: Doctor123!")
    print(f"  Login URL: http://localhost:3000/login")

    print(f"\n👥 PATIENT CREDENTIALS:")
    for i, patient in enumerate(patients, 1):
        print(f"\n  Patient {i}: {patient.full_name}")
        print(f"  Email: {patient.user.email}")
        print(f"  Password: Patient123!")
        print(f"  MRN: {patient.mrn}")

    print(f"\n📅 APPOINTMENTS & CAREPREP LINKS:")
    for i, appt_data in enumerate(appointments, 1):
        appt = appt_data["appointment"]
        patient = appt_data["patient"]
        token = appt_data["token"]

        print(f"\n  Appointment {i}:")
        print(f"  Patient: {patient.full_name}")
        print(f"  Date: {appt.scheduled_start.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Type: {appt.appointment_type.value}")
        print(f"  Chief Complaint: {appt.chief_complaint}")
        print(f"  CarePrep URL: http://localhost:3000/careprep/{token}")

    print("\n" + "="*80)
    print("TESTING INSTRUCTIONS:")
    print("="*80)
    print("\n1. PROVIDER SIGNUP & LOGIN:")
    print("   - Go to: http://localhost:3000/signup")
    print("   - Or login with: doctor@healthai.com / Doctor123!")

    print("\n2. PATIENT CAREPREP (Token-based access):")
    print("   - Copy one of the CarePrep URLs above")
    print("   - Open in browser (no login required)")
    print("   - Complete medical history and symptom checker")

    print("\n3. PROVIDER DASHBOARD:")
    print("   - After login, view appointments")
    print("   - See patient CarePrep responses")
    print("   - Review ContextAI analysis")

    print("\n" + "="*80 + "\n")


def main():
    """Main seed function."""
    print("Starting test data seed script...")
    print("="*80)

    db = SessionLocal()

    try:
        # Create test tenant
        print("\n1. Creating test tenant...")
        tenant = create_test_tenant(db)

        # Create test provider
        print("\n2. Creating test provider...")
        provider = create_test_provider(db, tenant.id)

        # Create test patients
        print("\n3. Creating test patients...")
        patients = create_test_patients(db, tenant.id)

        # Create test appointments
        print("\n4. Creating test appointments with CarePrep tokens...")
        appointments = create_test_appointments(db, provider, patients)

        # Print summary
        print_summary(provider, patients, appointments)

        print("✅ Test data seeded successfully!")

    except Exception as e:
        print(f"\n❌ Error seeding test data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
