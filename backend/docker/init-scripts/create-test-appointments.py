#!/usr/bin/env python3
"""
Script to create test appointments in the database.
This links FHIR patients with providers and creates realistic appointment data.
"""

import os
import sys
from datetime import datetime, timedelta
from uuid import uuid4

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.api.models.appointment import Appointment, AppointmentStatus, AppointmentType
from src.api.models.patient import Patient
from src.api.models.user import User

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://healthcare_user:healthcare_pass@localhost:5433/healthcare_db")

print("=" * 50)
print("Creating Test Appointments")
print("=" * 50)
print(f"Database URL: {DATABASE_URL}")
print()

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Get test patient (from FHIR data)
    patient = db.query(Patient).filter(Patient.mrn == "MRN123456").first()
    if not patient:
        print("❌ Test patient not found. Please ensure FHIR test data is loaded first.")
        print("   Run: bash docker/init-scripts/load-fhir-test-data.sh")
        sys.exit(1)

    print(f"✅ Found test patient: {patient.first_name} {patient.last_name} (MRN: {patient.mrn})")

    # Get provider (doctor)
    provider = db.query(User).filter(User.username == "drjane2").first()
    if not provider:
        print("❌ Test provider 'drjane2' not found. Please ensure test users exist.")
        sys.exit(1)

    print(f"✅ Found test provider: {provider.full_name} ({provider.username})")
    print()

    # Create test appointments
    now = datetime.utcnow()

    appointments_data = [
        {
            "appointment_type": AppointmentType.FOLLOW_UP,
            "scheduled_start": now + timedelta(minutes=30),  # In 30 minutes
            "duration_minutes": 30,
            "status": AppointmentStatus.SCHEDULED,
            "chief_complaint": "Follow-up on diabetes management",
            "previsit_completed": "Y",
        },
        {
            "appointment_type": AppointmentType.ANNUAL_CHECKUP,
            "scheduled_start": now + timedelta(hours=2),  # In 2 hours
            "duration_minutes": 45,
            "status": AppointmentStatus.CONFIRMED,
            "chief_complaint": "Annual physical examination",
            "previsit_completed": "N",
        },
        {
            "appointment_type": AppointmentType.URGENT_CARE,
            "scheduled_start": now + timedelta(days=1),  # Tomorrow
            "duration_minutes": 20,
            "status": AppointmentStatus.SCHEDULED,
            "chief_complaint": "Chest pain and shortness of breath",
            "previsit_completed": "Y",
        },
    ]

    created_count = 0

    for appt_data in appointments_data:
        scheduled_start = appt_data["scheduled_start"]
        scheduled_end = scheduled_start + timedelta(minutes=appt_data["duration_minutes"])

        # Check if appointment already exists
        existing = db.query(Appointment).filter(
            Appointment.patient_id == patient.id,
            Appointment.provider_id == provider.id,
            Appointment.scheduled_start == scheduled_start
        ).first()

        if existing:
            print(f"⏭️  Appointment already exists: {appt_data['chief_complaint']}")
            continue

        appointment = Appointment(
            id=str(uuid4()),
            patient_id=patient.id,
            provider_id=provider.id,
            appointment_type=appt_data["appointment_type"],
            status=appt_data["status"],
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            duration_minutes=appt_data["duration_minutes"],
            chief_complaint=appt_data["chief_complaint"],
            previsit_completed=appt_data["previsit_completed"],
        )

        db.add(appointment)
        created_count += 1

        print(f"✅ Created appointment: {appt_data['chief_complaint']}")
        print(f"   Type: {appt_data['appointment_type'].value}")
        print(f"   Status: {appt_data['status'].value}")
        print(f"   Scheduled: {scheduled_start.strftime('%Y-%m-%d %H:%M')}")
        print(f"   PreVisit Complete: {appt_data['previsit_completed']}")
        print()

    # Commit all changes
    db.commit()

    print("=" * 50)
    print(f"✅ Successfully created {created_count} test appointments")
    print("=" * 50)
    print()
    print("You can now test the appointments endpoint:")
    print("  curl http://localhost:8000/api/appointments/next \\")
    print("       -H \"Authorization: Bearer <token>\"")
    print()

except Exception as e:
    print(f"❌ Error creating test appointments: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    sys.exit(1)
finally:
    db.close()
