"""
AI Assistant API for real-time clinical support during visits.
Provides context-aware responses to help doctors during patient appointments.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
import logging

from src.api.database import get_db
from src.api.auth.dependencies import get_current_user
from src.api.models.user import User
from src.api.models.visit import Visit
from src.api.models.patient import Patient
from src.api.models.task import ProviderTask, TaskCategory, TaskPriority, TaskStatus
from datetime import datetime, timedelta
import re

router = APIRouter(prefix="/api/ai-assistant", tags=["ai-assistant"])
logger = logging.getLogger(__name__)


# ==================== Schemas ====================

class ChatMessage(BaseModel):
    """Chat message schema."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """AI chat request schema."""
    visit_id: str = Field(..., description="Current visit ID for context")
    message: str = Field(..., description="User's question or prompt")
    conversation_history: Optional[List[ChatMessage]] = Field(default=[], description="Previous conversation")


class ChatResponse(BaseModel):
    """AI chat response schema."""
    message: str = Field(..., description="AI assistant's response")
    suggestions: Optional[List[str]] = Field(default=[], description="Follow-up suggestions")
    context_used: Optional[dict] = Field(default={}, description="Context information used")


class QuickNote(BaseModel):
    """Quick note schema."""
    content: str = Field(..., description="Note content")


# ==================== AI Assistant Endpoints ====================

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chat with AI assistant during a visit.

    The AI has access to:
    - Patient demographics
    - Medical history
    - Current visit chief complaint
    - CarePrep data (if available)
    - Previous SOAP notes

    Example questions:
    - "What are the differential diagnoses for these symptoms?"
    - "What labs should I order for suspected diabetes?"
    - "Suggest medication for hypertension in elderly patients"
    - "What are red flags I should watch for?"
    """
    # Verify provider access
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only healthcare providers can use AI assistant"
        )

    # Get visit context
    visit = db.query(Visit).filter(Visit.id == request.visit_id).first()
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found"
        )

    # Get patient context
    patient = db.query(Patient).filter(Patient.id == visit.patient_id).first()

    # Build context for AI
    context = build_patient_context(visit, patient)

    # Get AI response (mock for now - will integrate Azure OpenAI)
    response = generate_ai_response(
        message=request.message,
        context=context,
        conversation_history=request.conversation_history
    )

    logger.info(f"AI assistant query from {current_user.id} for visit {request.visit_id}")

    return response


@router.post("/visits/{visit_id}/quick-notes")
async def add_quick_note(
    visit_id: str,
    note: QuickNote,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a quick note to the visit with smart shortcut parsing.

    Shortcuts create tasks automatically:
    - !followup <text> - Schedule follow-up appointment
    - !lab <test name> - Order lab test
    - !imaging <type> - Order imaging
    - !call <reason> - Call patient
    - !refer <specialty> - Refer to specialist
    - !rx <medication> - Medication task
    - !review <what> - Review results/records

    Examples:
    - "Patient doing well !followup in 2 weeks"
    - "Need to check lipid panel !lab lipid panel"
    - "Suspect pneumonia !imaging chest x-ray !call if fever worsens"
    """
    # Verify provider access
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only healthcare providers can add notes"
        )

    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found"
        )

    # Parse shortcuts and create tasks
    tasks_created = parse_and_create_tasks(
        note_content=note.content,
        visit=visit,
        provider_id=current_user.id,
        db=db
    )

    # Clean note content (remove shortcuts)
    clean_note = remove_shortcuts(note.content)

    # Append to subjective notes
    if visit.subjective:
        visit.subjective += f"\n\n--- Quick Note ({current_user.full_name}) ---\n{clean_note}"
    else:
        visit.subjective = f"--- Quick Note ({current_user.full_name}) ---\n{clean_note}"

    db.commit()
    db.refresh(visit)

    logger.info(f"Quick note added to visit {visit_id} by {current_user.id}, {len(tasks_created)} tasks created")

    return {
        "success": True,
        "message": "Quick note added successfully",
        "visit_id": visit_id,
        "tasks_created": len(tasks_created),
        "tasks": [task.to_dict() for task in tasks_created]
    }


@router.get("/visits/{visit_id}/suggestions")
async def get_clinical_suggestions(
    visit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered clinical suggestions based on current visit data.

    Returns:
    - Differential diagnoses
    - Recommended labs/imaging
    - Treatment suggestions
    - Red flags to watch for
    """
    # Verify provider access
    if current_user.role not in ["doctor", "nurse", "admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only healthcare providers can access suggestions"
        )

    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found"
        )

    patient = db.query(Patient).filter(Patient.id == visit.patient_id).first()

    # Generate suggestions based on visit data
    suggestions = generate_clinical_suggestions(visit, patient)

    return suggestions


# ==================== Helper Functions ====================

def build_patient_context(visit: Visit, patient: Optional[Patient]) -> dict:
    """Build comprehensive patient context for AI."""
    context = {
        "visit_type": visit.visit_type.value if visit.visit_type else "unknown",
        "chief_complaint": visit.chief_complaint or "Not specified",
        "reason_for_visit": visit.reason_for_visit or "Not specified"
    }

    if patient:
        context.update({
            "patient_age": patient.age if hasattr(patient, 'age') else "unknown",
            "patient_gender": patient.gender or "unknown",
            "allergies": patient.allergies or [],
            "chronic_conditions": patient.chronic_conditions or []
        })

    # Add SOAP notes if available
    if visit.subjective:
        context["subjective_notes"] = visit.subjective

    if visit.objective:
        context["objective_findings"] = visit.objective

    return context


def generate_ai_response(
    message: str,
    context: dict,
    conversation_history: List[ChatMessage]
) -> ChatResponse:
    """
    Generate AI response (mock implementation).
    TODO: Integrate with Azure OpenAI GPT-4o for production.
    """

    # Build system prompt with medical context
    system_prompt = f"""You are an AI medical assistant helping a doctor during a patient visit.

Current Visit Context:
- Chief Complaint: {context.get('chief_complaint')}
- Visit Type: {context.get('visit_type')}
- Patient Age: {context.get('patient_age')}
- Patient Gender: {context.get('patient_gender')}
- Allergies: {', '.join(context.get('allergies', []))}
- Chronic Conditions: {', '.join(context.get('chronic_conditions', []))}

You should provide:
1. Evidence-based medical information
2. Differential diagnoses when appropriate
3. Testing or treatment recommendations
4. Safety warnings and red flags
5. Patient education points

Always emphasize that final clinical decisions rest with the healthcare provider."""

    # Mock response based on common keywords
    message_lower = message.lower()

    if "differential" in message_lower or "diagnosis" in message_lower:
        response_text = f"""Based on the chief complaint '{context.get('chief_complaint')}', here are potential differential diagnoses to consider:

1. **Most Likely**: [Primary diagnosis based on symptoms]
2. **Consider**: [Alternative diagnoses]
3. **Rule Out**: [Serious conditions to exclude]

**Recommended Workup**:
- Vital signs and physical examination
- Relevant laboratory tests
- Consider imaging if indicated

**Red Flags to Watch**:
- Sudden worsening of symptoms
- New neurological signs
- Hemodynamic instability

Would you like me to elaborate on any specific diagnosis or suggest appropriate tests?"""

        suggestions = [
            "What labs should I order?",
            "What are the red flags?",
            "Suggest treatment options"
        ]

    elif "lab" in message_lower or "test" in message_lower:
        response_text = f"""For this presentation, I recommend the following diagnostic tests:

**Initial Labs**:
- Complete Blood Count (CBC)
- Comprehensive Metabolic Panel (CMP)
- Urinalysis if indicated

**Condition-Specific Tests**:
[Based on chief complaint and differential diagnoses]

**Imaging** (if indicated):
- Consider based on clinical findings

**Interpretation Tips**:
- Watch for critical values
- Consider trends over time
- Correlate with clinical picture

Would you like specific reference ranges or interpretation guidance?"""

        suggestions = [
            "Interpret these lab values",
            "What imaging is needed?",
            "Normal ranges for elderly patients"
        ]

    elif "medication" in message_lower or "treatment" in message_lower:
        allergies = context.get('allergies', [])
        allergy_note = f"\n⚠️ **Note**: Patient has documented allergies to: {', '.join(allergies)}" if allergies else ""

        response_text = f"""Treatment recommendations for this presentation:{allergy_note}

**First-Line Options**:
1. [Medication A]: Dosing, contraindications
2. [Medication B]: Alternative if A not suitable

**Patient Considerations**:
- Age: {context.get('patient_age')}
- Chronic conditions: {', '.join(context.get('chronic_conditions', []))}
- Drug interactions to check

**Non-Pharmacological**:
- Lifestyle modifications
- Patient education points
- Follow-up recommendations

**Monitoring**:
- Watch for side effects
- Efficacy assessment timeline
- When to escalate therapy

Would you like specific dosing information or alternative options?"""

        suggestions = [
            "Drug interactions to check",
            "What about generic alternatives?",
            "Patient education points"
        ]

    elif "red flag" in message_lower or "warning" in message_lower:
        response_text = f"""🚨 **Red Flags and Warning Signs to Monitor**:

**Immediate Concerns** (Seek emergency care):
- Chest pain with radiation
- Severe shortness of breath
- Altered mental status
- Signs of sepsis

**Urgent Evaluation Needed**:
- Progressive symptoms
- New neurological deficits
- Severe pain unresponsive to treatment

**Follow-up Indicators**:
- Symptoms not improving in 48-72 hours
- New symptom development
- Medication side effects

**Patient Education**:
Advise patient to return immediately if they experience any of the above warning signs.

Would you like specific red flags for this condition?"""

        suggestions = [
            "When to call 911?",
            "Follow-up timing recommendations",
            "Patient handout content"
        ]

    else:
        response_text = f"""I'm here to help with clinical decision support during this visit.

**I can assist with**:
- Differential diagnoses
- Lab and imaging recommendations
- Treatment options and dosing
- Red flags and warning signs
- Patient education materials

**Current Patient Context**:
- Chief Complaint: {context.get('chief_complaint')}
- Visit Type: {context.get('visit_type')}

How can I help you with this patient's care?"""

        suggestions = [
            "What are the differential diagnoses?",
            "What labs should I order?",
            "Suggest treatment options",
            "What are the red flags?"
        ]

    return ChatResponse(
        message=response_text,
        suggestions=suggestions,
        context_used={
            "chief_complaint": context.get('chief_complaint'),
            "patient_age": context.get('patient_age'),
            "allergies_count": len(context.get('allergies', []))
        }
    )


def generate_clinical_suggestions(visit: Visit, patient: Optional[Patient]) -> dict:
    """Generate clinical suggestions for the visit."""

    suggestions = {
        "differential_diagnoses": [
            "Diagnosis 1 (Most likely based on symptoms)",
            "Diagnosis 2 (Consider alternative)",
            "Diagnosis 3 (Rule out serious condition)"
        ],
        "recommended_tests": [
            "Complete Blood Count (CBC)",
            "Comprehensive Metabolic Panel",
            "Condition-specific tests based on chief complaint"
        ],
        "treatment_considerations": [
            "First-line medication options",
            "Lifestyle modifications",
            "Patient education priorities"
        ],
        "red_flags": [
            "Worsening symptoms despite treatment",
            "New concerning signs",
            "Specific red flags for this condition"
        ],
        "follow_up": {
            "timing": "2-4 weeks or sooner if symptoms worsen",
            "what_to_monitor": "Symptom progression, medication tolerance, lab results"
        }
    }

    return suggestions


def parse_and_create_tasks(
    note_content: str,
    visit: Visit,
    provider_id: str,
    db: Session
) -> List[ProviderTask]:
    """
    Parse shortcuts from note content and create tasks.

    Supported shortcuts:
    - !followup <text> - Schedule follow-up
    - !lab <test> - Order lab
    - !imaging <type> - Order imaging
    - !call <reason> - Call patient
    - !refer <specialty> - Referral
    - !rx <medication> - Medication task
    - !review <what> - Review task
    """
    tasks_created = []

    # Shortcut patterns
    shortcuts = {
        r'!followup\s+(.+?)(?=!|$)': (TaskCategory.FOLLOW_UP, TaskPriority.MEDIUM, 7),  # 7 days default
        r'!lab\s+(.+?)(?=!|$)': (TaskCategory.LAB_ORDER, TaskPriority.HIGH, 3),
        r'!imaging\s+(.+?)(?=!|$)': (TaskCategory.IMAGING_ORDER, TaskPriority.HIGH, 3),
        r'!call\s+(.+?)(?=!|$)': (TaskCategory.PHONE_CALL, TaskPriority.MEDIUM, 1),
        r'!refer\s+(.+?)(?=!|$)': (TaskCategory.REFERRAL, TaskPriority.MEDIUM, 7),
        r'!rx\s+(.+?)(?=!|$)': (TaskCategory.MEDICATION, TaskPriority.HIGH, 1),
        r'!review\s+(.+?)(?=!|$)': (TaskCategory.REVIEW, TaskPriority.MEDIUM, 3),
    }

    for pattern, (category, priority, default_days) in shortcuts.items():
        matches = re.finditer(pattern, note_content, re.IGNORECASE)

        for match in matches:
            task_description = match.group(1).strip()

            # Get string values from enums
            category_str = category.value if hasattr(category, 'value') else str(category)
            priority_str = priority.value if hasattr(priority, 'value') else str(priority)
            status_str = "pending"

            # Debug logging
            logger.info(f"Creating task - category={category}, category_str={category_str}, priority_str={priority_str}, status_str={status_str}")

            # Create title from category and description
            category_name = category_str.replace('_', ' ').title()
            title = f"{category_name}: {task_description[:50]}"

            # Set due date
            due_date = datetime.utcnow() + timedelta(days=default_days)

            # Create task - use string values directly, not enums
            task = ProviderTask(
                title=title,
                description=task_description,
                category=category_str,
                priority=priority_str,
                status=status_str,
                provider_id=provider_id,
                patient_id=visit.patient_id,
                visit_id=visit.id,
                appointment_id=visit.appointment_id,
                due_date=due_date,
                created_from_shortcut=True,
                shortcut_code=match.group(0).split()[0],  # e.g., "!followup"
                task_metadata={
                    "created_during_visit": True,
                    "original_note_snippet": match.group(0)
                }
            )

            db.add(task)
            tasks_created.append(task)

    if tasks_created:
        db.commit()
        for task in tasks_created:
            db.refresh(task)

    return tasks_created


def remove_shortcuts(note_content: str) -> str:
    """Remove shortcut commands from note content but keep the descriptive text."""
    # Replace shortcuts with just the description
    shortcuts_pattern = r'!(followup|lab|imaging|call|refer|rx|review)\s+'
    cleaned = re.sub(shortcuts_pattern, '[Task: \\1] ', note_content, flags=re.IGNORECASE)
    return cleaned
