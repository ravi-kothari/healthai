"""
Clinical Data API Router.
Provides CRUD endpoints for medications, labs, allergies, conditions, imaging, documents, and care plans.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from src.api.database import get_db
from src.api.auth.dependencies import get_current_user
from src.api.models.user import User
from src.api.models.clinical import (
    Medication, LabResult, LabOrder, Allergy, Condition,
    ImagingStudy, ClinicalDocument, CarePlan, CareGoal, FollowUpInstruction
)
from src.api.schemas.clinical_schemas import (
    MedicationCreate, MedicationUpdate, MedicationResponse,
    LabResultCreate, LabResultResponse, LabOrderCreate, LabOrderResponse,
    AllergyCreate, AllergyUpdate, AllergyResponse,
    ConditionCreate, ConditionUpdate, ConditionResponse,
    ImagingStudyCreate, ImagingStudyUpdate, ImagingStudyResponse,
    ClinicalDocumentCreate, ClinicalDocumentResponse,
    CarePlanCreate, CarePlanResponse,
    CareGoalCreate, CareGoalUpdate, CareGoalResponse,
    FollowUpInstructionCreate, FollowUpInstructionResponse
)

router = APIRouter(prefix="/api/clinical", tags=["clinical"])


# ============================================================================
# MEDICATIONS
# ============================================================================

@router.get("/patients/{patient_id}/medications", response_model=List[MedicationResponse])
async def get_patient_medications(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all medications for a patient."""
    medications = db.query(Medication).filter(Medication.patient_id == patient_id).all()
    return medications


@router.post("/medications", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
async def create_medication(
    medication: MedicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new medication."""
    db_medication = Medication(**medication.model_dump())
    db.add(db_medication)
    db.commit()
    db.refresh(db_medication)
    return db_medication


@router.put("/medications/{medication_id}", response_model=MedicationResponse)
async def update_medication(
    medication_id: str,
    medication: MedicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a medication."""
    db_medication = db.query(Medication).filter(Medication.id == medication_id).first()
    if not db_medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    for key, value in medication.model_dump(exclude_unset=True).items():
        setattr(db_medication, key, value)

    db.commit()
    db.refresh(db_medication)
    return db_medication


@router.delete("/medications/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication(
    medication_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a medication."""
    db_medication = db.query(Medication).filter(Medication.id == medication_id).first()
    if not db_medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    db.delete(db_medication)
    db.commit()
    return None


# ============================================================================
# LAB RESULTS
# ============================================================================

@router.get("/patients/{patient_id}/lab-results", response_model=List[LabResultResponse])
async def get_patient_lab_results(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all lab results for a patient."""
    results = db.query(LabResult).filter(LabResult.patient_id == patient_id).all()
    return results


@router.post("/lab-results", response_model=LabResultResponse, status_code=status.HTTP_201_CREATED)
async def create_lab_result(
    lab_result: LabResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new lab result."""
    db_result = LabResult(**lab_result.model_dump())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


@router.get("/patients/{patient_id}/lab-orders", response_model=List[LabOrderResponse])
async def get_patient_lab_orders(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all lab orders for a patient."""
    orders = db.query(LabOrder).filter(LabOrder.patient_id == patient_id).all()
    return orders


@router.post("/lab-orders", response_model=LabOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_lab_order(
    lab_order: LabOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new lab order."""
    db_order = LabOrder(**lab_order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


# ============================================================================
# ALLERGIES
# ============================================================================

@router.get("/patients/{patient_id}/allergies", response_model=List[AllergyResponse])
async def get_patient_allergies(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all allergies for a patient."""
    allergies = db.query(Allergy).filter(Allergy.patient_id == patient_id).all()
    return allergies


@router.post("/allergies", response_model=AllergyResponse, status_code=status.HTTP_201_CREATED)
async def create_allergy(
    allergy: AllergyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new allergy."""
    db_allergy = Allergy(**allergy.model_dump())
    db.add(db_allergy)
    db.commit()
    db.refresh(db_allergy)
    return db_allergy


@router.put("/allergies/{allergy_id}", response_model=AllergyResponse)
async def update_allergy(
    allergy_id: str,
    allergy: AllergyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an allergy."""
    db_allergy = db.query(Allergy).filter(Allergy.id == allergy_id).first()
    if not db_allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")

    for key, value in allergy.model_dump(exclude_unset=True).items():
        setattr(db_allergy, key, value)

    db.commit()
    db.refresh(db_allergy)
    return db_allergy


@router.delete("/allergies/{allergy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_allergy(
    allergy_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an allergy."""
    db_allergy = db.query(Allergy).filter(Allergy.id == allergy_id).first()
    if not db_allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")

    db.delete(db_allergy)
    db.commit()
    return None


# ============================================================================
# CONDITIONS
# ============================================================================

@router.get("/patients/{patient_id}/conditions", response_model=List[ConditionResponse])
async def get_patient_conditions(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all conditions for a patient."""
    conditions = db.query(Condition).filter(Condition.patient_id == patient_id).all()
    return conditions


@router.post("/conditions", response_model=ConditionResponse, status_code=status.HTTP_201_CREATED)
async def create_condition(
    condition: ConditionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new condition."""
    db_condition = Condition(**condition.model_dump())
    db.add(db_condition)
    db.commit()
    db.refresh(db_condition)
    return db_condition


@router.put("/conditions/{condition_id}", response_model=ConditionResponse)
async def update_condition(
    condition_id: str,
    condition: ConditionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a condition."""
    db_condition = db.query(Condition).filter(Condition.id == condition_id).first()
    if not db_condition:
        raise HTTPException(status_code=404, detail="Condition not found")

    for key, value in condition.model_dump(exclude_unset=True).items():
        setattr(db_condition, key, value)

    db.commit()
    db.refresh(db_condition)
    return db_condition


@router.delete("/conditions/{condition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_condition(
    condition_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a condition."""
    db_condition = db.query(Condition).filter(Condition.id == condition_id).first()
    if not db_condition:
        raise HTTPException(status_code=404, detail="Condition not found")

    db.delete(db_condition)
    db.commit()
    return None


# ============================================================================
# IMAGING STUDIES
# ============================================================================

@router.get("/patients/{patient_id}/imaging-studies", response_model=List[ImagingStudyResponse])
async def get_patient_imaging_studies(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all imaging studies for a patient."""
    studies = db.query(ImagingStudy).filter(ImagingStudy.patient_id == patient_id).all()
    return studies


@router.post("/imaging-studies", response_model=ImagingStudyResponse, status_code=status.HTTP_201_CREATED)
async def create_imaging_study(
    study: ImagingStudyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new imaging study."""
    db_study = ImagingStudy(**study.model_dump())
    db.add(db_study)
    db.commit()
    db.refresh(db_study)
    return db_study


@router.put("/imaging-studies/{study_id}", response_model=ImagingStudyResponse)
async def update_imaging_study(
    study_id: str,
    study: ImagingStudyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an imaging study."""
    db_study = db.query(ImagingStudy).filter(ImagingStudy.id == study_id).first()
    if not db_study:
        raise HTTPException(status_code=404, detail="Imaging study not found")

    for key, value in study.model_dump(exclude_unset=True).items():
        setattr(db_study, key, value)

    db.commit()
    db.refresh(db_study)
    return db_study


@router.delete("/imaging-studies/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_imaging_study(
    study_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an imaging study."""
    db_study = db.query(ImagingStudy).filter(ImagingStudy.id == study_id).first()
    if not db_study:
        raise HTTPException(status_code=404, detail="Imaging study not found")

    db.delete(db_study)
    db.commit()
    return None


# ============================================================================
# CLINICAL DOCUMENTS
# ============================================================================

@router.get("/patients/{patient_id}/documents", response_model=List[ClinicalDocumentResponse])
async def get_patient_documents(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all clinical documents for a patient."""
    documents = db.query(ClinicalDocument).filter(ClinicalDocument.patient_id == patient_id).all()
    return documents


@router.post("/documents", response_model=ClinicalDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: ClinicalDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new clinical document."""
    db_document = ClinicalDocument(**document.model_dump())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a clinical document."""
    db_document = db.query(ClinicalDocument).filter(ClinicalDocument.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(db_document)
    db.commit()
    return None


# ============================================================================
# CARE PLANS
# ============================================================================

@router.get("/patients/{patient_id}/care-plans", response_model=List[CarePlanResponse])
async def get_patient_care_plans(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all care plans for a patient."""
    care_plans = db.query(CarePlan).filter(CarePlan.patient_id == patient_id).all()
    return care_plans


@router.post("/care-plans", response_model=CarePlanResponse, status_code=status.HTTP_201_CREATED)
async def create_care_plan(
    care_plan: CarePlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new care plan."""
    # Create care plan
    db_care_plan = CarePlan(
        patient_id=care_plan.patient_id,
        title=care_plan.title,
        diagnosis=care_plan.diagnosis,
        created_by=care_plan.created_by
    )
    db.add(db_care_plan)
    db.flush()

    # Add goals
    for goal_data in care_plan.goals or []:
        goal = CareGoal(
            care_plan_id=db_care_plan.id,
            **goal_data.model_dump()
        )
        db.add(goal)

    # Add instructions
    for instruction_data in care_plan.instructions or []:
        instruction = FollowUpInstruction(
            care_plan_id=db_care_plan.id,
            **instruction_data.model_dump()
        )
        db.add(instruction)

    db.commit()
    db.refresh(db_care_plan)
    return db_care_plan


@router.post("/care-plans/{plan_id}/goals", response_model=CareGoalResponse, status_code=status.HTTP_201_CREATED)
async def add_care_goal(
    plan_id: str,
    goal: CareGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a goal to a care plan."""
    db_goal = CareGoal(care_plan_id=plan_id, **goal.model_dump())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.put("/care-plans/goals/{goal_id}", response_model=CareGoalResponse)
async def update_care_goal(
    goal_id: str,
    goal: CareGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a care goal."""
    db_goal = db.query(CareGoal).filter(CareGoal.id == goal_id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Care goal not found")

    for key, value in goal.model_dump(exclude_unset=True).items():
        setattr(db_goal, key, value)

    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.post("/care-plans/{plan_id}/instructions", response_model=FollowUpInstructionResponse, status_code=status.HTTP_201_CREATED)
async def add_followup_instruction(
    plan_id: str,
    instruction: FollowUpInstructionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a follow-up instruction to a care plan."""
    db_instruction = FollowUpInstruction(care_plan_id=plan_id, **instruction.model_dump())
    db.add(db_instruction)
    db.commit()
    db.refresh(db_instruction)
    return db_instruction
