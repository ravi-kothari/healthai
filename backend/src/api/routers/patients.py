"""
Patient CRUD router with create, read, update, delete operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import logging

from src.api.database import get_db
from src.api.models.user import User, UserRole
from src.api.models.patient import Patient
from src.api.schemas.patient_schemas import (
    PatientCreateRequest,
    PatientUpdateRequest,
    PatientResponse,
    PatientListResponse,
)
from src.api.auth.dependencies import get_current_user, require_role
from src.api.utils.mrn_generator import generate_mrn
from src.api.utils.pagination import paginate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new patient record.

    Args:
        patient_data: Patient information
        db: Database session
        current_user: Current authenticated user

    Returns:
        PatientResponse: Created patient data

    Raises:
        HTTPException: If user_id already has a patient record or other errors
    """
    logger.info(f"Creating patient for user_id: {patient_data.user_id}")

    # Check if user exists
    user = db.query(User).filter(User.id == patient_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if patient already exists for this user
    existing_patient = db.query(Patient).filter(Patient.user_id == patient_data.user_id).first()
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient record already exists for this user"
        )

    # Generate unique MRN
    mrn = generate_mrn()
    while db.query(Patient).filter(Patient.mrn == mrn).first():
        mrn = generate_mrn()  # Regenerate if collision

    try:
        new_patient = Patient(
            user_id=patient_data.user_id,
            mrn=mrn,
            first_name=patient_data.first_name,
            last_name=patient_data.last_name,
            date_of_birth=patient_data.date_of_birth,
            gender=patient_data.gender,
            blood_type=patient_data.blood_type,
            address=patient_data.address,
            city=patient_data.city,
            state=patient_data.state,
            zip_code=patient_data.zip_code,
            emergency_contact_name=patient_data.emergency_contact_name,
            emergency_contact_phone=patient_data.emergency_contact_phone,
            emergency_contact_relationship=patient_data.emergency_contact_relationship,
            insurance_provider=patient_data.insurance_provider,
            insurance_policy_number=patient_data.insurance_policy_number,
            insurance_group_number=patient_data.insurance_group_number,
            allergies=patient_data.allergies,
            chronic_conditions=patient_data.chronic_conditions,
            current_medications=patient_data.current_medications,
            notes=patient_data.notes,
        )

        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)

        logger.info(f"Patient created successfully: {new_patient.id}, MRN: {new_patient.mrn}")

        return PatientResponse.model_validate(new_patient.to_dict())

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database error creating patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create patient due to database constraint"
        )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get patient by ID.

    Args:
        patient_id: Patient UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        PatientResponse: Patient data

    Raises:
        HTTPException: If patient not found
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    # Access control: Patients can only view their own record
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return PatientResponse.model_validate(patient.to_dict())


@router.get("", response_model=PatientListResponse)
async def list_patients(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or MRN"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN, UserRole.STAFF))
):
    """
    List all patients with pagination and search.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        search: Optional search term
        db: Database session
        current_user: Current authenticated user (must be healthcare provider)

    Returns:
        PatientListResponse: Paginated list of patients
    """
    query = db.query(Patient)

    # Apply search filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Patient.first_name.ilike(search_filter)) |
            (Patient.last_name.ilike(search_filter)) |
            (Patient.mrn.ilike(search_filter))
        )

    # Order by created_at descending
    query = query.order_by(Patient.created_at.desc())

    # Paginate
    items, total, total_pages = paginate(query, page=page, page_size=page_size)

    # Convert to response models
    patient_responses = [PatientResponse.model_validate(p.to_dict()) for p in items]

    return PatientListResponse(
        items=patient_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update patient information.

    Args:
        patient_id: Patient UUID
        patient_data: Updated patient information
        db: Database session
        current_user: Current authenticated user

    Returns:
        PatientResponse: Updated patient data

    Raises:
        HTTPException: If patient not found or access denied
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    # Access control: Patients can only update their own record
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Update fields if provided
    update_data = patient_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(patient, field, value)

    try:
        db.commit()
        db.refresh(patient)

        logger.info(f"Patient updated successfully: {patient.id}")

        return PatientResponse.model_validate(patient.to_dict())

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database error updating patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update patient"
        )


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Delete a patient record (admin only).

    Args:
        patient_id: Patient UUID
        db: Database session
        current_user: Current authenticated user (must be admin)

    Raises:
        HTTPException: If patient not found
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    db.delete(patient)
    db.commit()

    logger.info(f"Patient deleted: {patient_id} by admin {current_user.id}")

    return None


@router.get("/by-user/{user_id}", response_model=PatientResponse)
async def get_patient_by_user_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get patient record by user ID.

    Args:
        user_id: User UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        PatientResponse: Patient data

    Raises:
        HTTPException: If patient not found
    """
    patient = db.query(Patient).filter(Patient.user_id == user_id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient record not found for this user"
        )

    # Access control
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return PatientResponse.model_validate(patient.to_dict())
