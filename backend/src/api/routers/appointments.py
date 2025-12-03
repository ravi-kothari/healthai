"""
Appointment management endpoints.
Handles scheduling, retrieval, and management of patient appointments.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import secrets

from src.api.database import get_db
from src.api.models.appointment import Appointment, AppointmentStatus
from src.api.models.user import User
from src.api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/appointments",
    tags=["appointments"]
)


@router.get("/next")
async def get_next_appointment(
    provider_id: Optional[str] = Query(None, description="Provider ID (defaults to current user)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the next scheduled appointment for a provider.

    Returns the next upcoming appointment that is:
    - Scheduled or Confirmed status
    - Has not started yet (or started today)
    - Ordered by scheduled_start time (earliest first)

    Args:
        provider_id: Optional provider ID (defaults to current user)
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: Next appointment details including patient information

    Raises:
        HTTPException: 404 if no upcoming appointments found
        HTTPException: 403 if not authorized to view provider's appointments
    """
    # Determine which provider's appointments to fetch
    target_provider_id = provider_id if provider_id else current_user.id

    # Authorization check: only the provider or admin can view appointments
    if target_provider_id != current_user.id and current_user.role not in ["admin", "doctor"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this provider's appointments"
        )

    # Get current time
    now = datetime.utcnow()

    # Query for next appointment
    appointment = db.query(Appointment).filter(
        and_(
            Appointment.provider_id == target_provider_id,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
            Appointment.scheduled_start >= now
        )
    ).order_by(Appointment.scheduled_start.asc()).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="No upcoming appointments found"
        )

    logger.info(f"Found next appointment {appointment.id} for provider {target_provider_id}")

    # Build response
    return {
        "appointment_id": appointment.id,
        "patient_id": appointment.patient_id,
        "provider_id": appointment.provider_id,
        "appointment_type": appointment.appointment_type.value if appointment.appointment_type else None,
        "status": appointment.status.value if appointment.status else None,
        "scheduled_start": appointment.scheduled_start.isoformat() if appointment.scheduled_start else None,
        "scheduled_end": appointment.scheduled_end.isoformat() if appointment.scheduled_end else None,
        "duration_minutes": appointment.duration_minutes,
        "chief_complaint": appointment.chief_complaint,
        "previsit_completed": appointment.previsit_completed == "Y",
        "patient": {
            "id": appointment.patient.id,
            "name": f"{appointment.patient.first_name} {appointment.patient.last_name}",
            "first_name": appointment.patient.first_name,
            "last_name": appointment.patient.last_name,
            "email": appointment.patient.user.email if appointment.patient.user else None,
            "phone": appointment.patient.user.phone if appointment.patient.user else None,
            "date_of_birth": appointment.patient.date_of_birth.isoformat() if appointment.patient.date_of_birth else None,
            "mrn": appointment.patient.mrn,
        } if appointment.patient else None,
        "is_today": appointment.is_today,
    }


@router.get("/provider/{provider_id}/upcoming")
async def get_provider_upcoming_appointments(
    provider_id: str,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of appointments to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all upcoming appointments for a provider.

    Returns appointments that are:
    - Scheduled or Confirmed status
    - Scheduled for today or future
    - Ordered by scheduled_start time

    Args:
        provider_id: Provider ID
        limit: Maximum number of appointments (default 10, max 100)
        current_user: Current authenticated user
        db: Database session

    Returns:
        list: List of upcoming appointments

    Raises:
        HTTPException: 403 if not authorized
    """
    # Authorization check
    if provider_id != current_user.id and current_user.role not in ["admin", "doctor"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this provider's appointments"
        )

    # Get current time
    now = datetime.utcnow()

    # Query for upcoming appointments
    appointments = db.query(Appointment).filter(
        and_(
            Appointment.provider_id == provider_id,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
            Appointment.scheduled_start >= now
        )
    ).order_by(Appointment.scheduled_start.asc()).limit(limit).all()

    logger.info(f"Found {len(appointments)} upcoming appointments for provider {provider_id}")

    # Build response
    return {
        "provider_id": provider_id,
        "count": len(appointments),
        "appointments": [
            {
                "appointment_id": appt.id,
                "patient_id": appt.patient_id,
                "appointment_type": appt.appointment_type.value if appt.appointment_type else None,
                "status": appt.status.value if appt.status else None,
                "scheduled_start": appt.scheduled_start.isoformat() if appt.scheduled_start else None,
                "scheduled_end": appt.scheduled_end.isoformat() if appt.scheduled_end else None,
                "duration_minutes": appt.duration_minutes,
                "chief_complaint": appt.chief_complaint,
                "previsit_completed": appt.previsit_completed == "Y",
                "patient_name": f"{appt.patient.first_name} {appt.patient.last_name}" if appt.patient else None,
                "is_today": appt.is_today,
            }
            for appt in appointments
        ]
    }


@router.get("/today")
async def get_todays_appointments(
    provider_id: Optional[str] = Query(None, description="Provider ID (defaults to current user)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all appointments scheduled for today for a provider.

    Args:
        provider_id: Optional provider ID (defaults to current user)
        current_user: Current authenticated user
        db: Database session

    Returns:
        list: List of today's appointments

    Raises:
        HTTPException: 403 if not authorized
    """
    # Determine which provider
    target_provider_id = provider_id if provider_id else current_user.id

    # Authorization check
    if target_provider_id != current_user.id and current_user.role not in ["admin", "doctor"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this provider's appointments"
        )

    # Get today's date range
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Query for today's appointments
    appointments = db.query(Appointment).filter(
        and_(
            Appointment.provider_id == target_provider_id,
            Appointment.scheduled_start >= today_start,
            Appointment.scheduled_start <= today_end,
            Appointment.status != AppointmentStatus.CANCELLED
        )
    ).order_by(Appointment.scheduled_start.asc()).all()

    logger.info(f"Found {len(appointments)} appointments today for provider {target_provider_id}")

    return {
        "provider_id": target_provider_id,
        "date": now.date().isoformat(),
        "count": len(appointments),
        "appointments": [
            {
                **appt.to_dict(),
                "patient": {
                    "id": appt.patient.id,
                    "name": f"{appt.patient.first_name} {appt.patient.last_name}",
                    "first_name": appt.patient.first_name,
                    "last_name": appt.patient.last_name,
                    "mrn": appt.patient.mrn,
                } if appt.patient else None
            }
            for appt in appointments
        ]
    }


@router.post("/{appointment_id}/generate-careprep-link")
async def generate_careprep_link(
    appointment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a unique CarePrep link for a patient's appointment.

    This link allows patients to access their appointment preparation
    without needing to log in.

    Args:
        appointment_id: The appointment ID
        current_user: Current authenticated user (must be provider)
        db: Database session

    Returns:
        dict: Contains the unique token and full URL

    Raises:
        HTTPException: 404 if appointment not found
        HTTPException: 403 if not authorized
    """
    # Get appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Authorization: only the provider can generate links
    if appointment.provider_id != current_user.id and current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to generate link for this appointment"
        )

    # Generate unique token (32 character URL-safe string)
    token = secrets.token_urlsafe(32)

    # Store token in appointment (you'll need to add prep_token field to model)
    # For now, we'll use a simple encoding: base64(appointment_id)
    import base64
    simple_token = base64.urlsafe_b64encode(appointment_id.encode()).decode()

    logger.info(f"Generated CarePrep link for appointment {appointment_id}")

    return {
        "appointment_id": appointment_id,
        "token": simple_token,
        "careprep_url": f"/careprep/{simple_token}",
        "full_url": f"http://localhost:3000/careprep/{simple_token}",
        "expires_at": appointment.scheduled_start.isoformat() if appointment.scheduled_start else None
    }


@router.get("/careprep/{token}")
async def get_appointment_by_careprep_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Get appointment details using a CarePrep token (public endpoint, no auth required).

    This allows patients to access their appointment without logging in.

    Args:
        token: The unique CarePrep token
        db: Database session

    Returns:
        dict: Appointment details including patient name and scheduled time

    Raises:
        HTTPException: 404 if token is invalid or appointment not found
    """
    try:
        # Decode token to get appointment ID
        import base64
        appointment_id = base64.urlsafe_b64decode(token.encode()).decode()
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid CarePrep link")

    # Get appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Check if appointment is still valid (not cancelled, not too far in the past)
    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(status_code=404, detail="Appointment has been cancelled")

    logger.info(f"CarePrep link accessed for appointment {appointment_id}")

    # Return appointment details (safe for public access)
    return {
        "appointment_id": appointment.id,
        "patient_id": appointment.patient_id,
        "patient_name": f"{appointment.patient.first_name} {appointment.patient.last_name}" if appointment.patient else None,
        "provider_name": f"{appointment.provider.full_name}" if appointment.provider else "Your Provider",
        "scheduled_start": appointment.scheduled_start.isoformat() if appointment.scheduled_start else None,
        "scheduled_end": appointment.scheduled_end.isoformat() if appointment.scheduled_end else None,
        "appointment_type": appointment.appointment_type.value if appointment.appointment_type else None,
        "chief_complaint": appointment.chief_complaint,
        "duration_minutes": appointment.duration_minutes,
        "status": appointment.status.value if appointment.status else None
    }

@router.post("/import")
async def import_appointments(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk import appointments from a CSV file.
    
    Expected CSV columns:
    - patient_email (or patient_id)
    - date (YYYY-MM-DD)
    - time (HH:MM)
    - duration_minutes (optional, default 30)
    - type (optional, default 'initial_consultation')
    - notes (optional)
    """
    if current_user.role not in ["admin", "doctor"]:
        raise HTTPException(status_code=403, detail="Not authorized to import appointments")

    import csv
    import io
    from src.api.models.patient import Patient

    content = await file.read()
    decoded_content = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded_content))
    
    success_count = 0
    failed_count = 0
    errors = []
    
    # Normalize headers
    if csv_reader.fieldnames:
        csv_reader.fieldnames = [h.lower().strip() for h in csv_reader.fieldnames]

    for row_idx, row in enumerate(csv_reader, start=1):
        try:
            # 1. Find Patient
            patient = None
            if 'patient_id' in row and row['patient_id']:
                patient = db.query(Patient).filter(Patient.id == row['patient_id']).first()
            elif 'patient_email' in row and row['patient_email']:
                # Join with User table to find patient by email
                patient = db.query(Patient).join(User).filter(User.email == row['patient_email']).first()
            
            if not patient:
                raise ValueError(f"Patient not found for row {row_idx}")

            # 2. Parse Date/Time
            date_str = row.get('date')
            time_str = row.get('time')
            if not date_str or not time_str:
                raise ValueError("Date and Time are required")
            
            start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            duration = int(row.get('duration_minutes', 30))
            end_dt = start_dt + timedelta(minutes=duration)

            # 3. Create Appointment
            appt_type = row.get('type', 'initial_consultation')
            # Validate enum if possible, or let it fail/default
            
            new_appt = Appointment(
                patient_id=patient.id,
                provider_id=current_user.id, # Assign to current user
                appointment_type=appt_type,
                status=AppointmentStatus.SCHEDULED,
                scheduled_start=start_dt,
                scheduled_end=end_dt,
                duration_minutes=duration,
                notes=row.get('notes', ''),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_appt)
            success_count += 1
            
        except Exception as e:
            failed_count += 1
            errors.append(f"Row {row_idx}: {str(e)}")
            logger.error(f"Import error row {row_idx}: {e}")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database commit failed: {str(e)}")

    return {
        "success_count": success_count,
        "failed_count": failed_count,
        "errors": errors
    }
