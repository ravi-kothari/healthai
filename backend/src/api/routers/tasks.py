"""
Provider Task Management API.
Endpoints for managing clinical follow-ups, reminders, and to-do items.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging

from src.api.database import get_db
from src.api.auth.dependencies import get_current_user
from src.api.models.user import User
from src.api.models.task import ProviderTask, TaskCategory, TaskPriority, TaskStatus

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)


# ==================== Schemas ====================

class TaskCreate(BaseModel):
    """Create task schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: TaskCategory
    priority: TaskPriority = TaskPriority.MEDIUM
    patient_id: Optional[str] = None
    visit_id: Optional[str] = None
    appointment_id: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = []


class TaskUpdate(BaseModel):
    """Update task schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[TaskCategory] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None


class TaskResponse(BaseModel):
    """Task response schema."""
    id: str
    title: str
    description: Optional[str]
    category: str
    priority: str
    status: str
    provider_id: str
    patient_id: Optional[str]
    visit_id: Optional[str]
    appointment_id: Optional[str]
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    tags: Optional[List[str]]
    created_from_shortcut: bool
    shortcut_code: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Endpoints ====================

@router.get("/", response_model=List[TaskResponse])
async def get_my_tasks(
    status_filter: Optional[TaskStatus] = Query(None, description="Filter by status"),
    category_filter: Optional[TaskCategory] = Query(None, description="Filter by category"),
    priority_filter: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    patient_id: Optional[str] = Query(None, description="Filter by patient"),
    overdue_only: bool = Query(False, description="Show only overdue tasks"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all tasks for the current provider.

    Filters:
    - status: pending, in_progress, completed, cancelled
    - category: follow_up, lab_order, imaging_order, etc.
    - priority: low, medium, high, urgent
    - patient_id: tasks for specific patient
    - overdue_only: only show overdue tasks
    """
    query = db.query(ProviderTask).filter(ProviderTask.provider_id == current_user.id)

    if status_filter:
        query = query.filter(ProviderTask.status == status_filter)

    if category_filter:
        query = query.filter(ProviderTask.category == category_filter)

    if priority_filter:
        query = query.filter(ProviderTask.priority == priority_filter)

    if patient_id:
        query = query.filter(ProviderTask.patient_id == patient_id)

    if overdue_only:
        query = query.filter(
            ProviderTask.due_date < datetime.utcnow(),
            ProviderTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        )

    tasks = query.order_by(
        ProviderTask.priority.desc(),
        ProviderTask.due_date.asc()
    ).all()

    return tasks


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task."""
    task = ProviderTask(
        title=task_data.title,
        description=task_data.description,
        category=task_data.category,
        priority=task_data.priority,
        provider_id=current_user.id,
        patient_id=task_data.patient_id,
        visit_id=task_data.visit_id,
        appointment_id=task_data.appointment_id,
        due_date=task_data.due_date,
        tags=task_data.tags,
        status=TaskStatus.PENDING
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    logger.info(f"Task created: {task.id} by provider {current_user.id}")

    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific task."""
    task = db.query(ProviderTask).filter(
        ProviderTask.id == task_id,
        ProviderTask.provider_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task."""
    task = db.query(ProviderTask).filter(
        ProviderTask.id == task_id,
        ProviderTask.provider_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update fields
    update_data = task_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    # If marking as completed, set completed_at
    if task_update.status == TaskStatus.COMPLETED and not task.completed_at:
        task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    logger.info(f"Task updated: {task.id}")

    return task


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a task as completed."""
    task = db.query(ProviderTask).filter(
        ProviderTask.id == task_id,
        ProviderTask.provider_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    logger.info(f"Task completed: {task.id}")

    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a task."""
    task = db.query(ProviderTask).filter(
        ProviderTask.id == task_id,
        ProviderTask.provider_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    logger.info(f"Task deleted: {task_id}")

    return {"success": True, "message": "Task deleted successfully"}


@router.get("/stats/summary")
async def get_task_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get task statistics for the current provider."""
    total = db.query(ProviderTask).filter(
        ProviderTask.provider_id == current_user.id
    ).count()

    pending = db.query(ProviderTask).filter(
        ProviderTask.provider_id == current_user.id,
        ProviderTask.status == TaskStatus.PENDING
    ).count()

    in_progress = db.query(ProviderTask).filter(
        ProviderTask.provider_id == current_user.id,
        ProviderTask.status == TaskStatus.IN_PROGRESS
    ).count()

    completed_today = db.query(ProviderTask).filter(
        ProviderTask.provider_id == current_user.id,
        ProviderTask.status == TaskStatus.COMPLETED,
        ProviderTask.completed_at >= datetime.utcnow().date()
    ).count()

    overdue = db.query(ProviderTask).filter(
        ProviderTask.provider_id == current_user.id,
        ProviderTask.due_date < datetime.utcnow(),
        ProviderTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
    ).count()

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed_today": completed_today,
        "overdue": overdue
    }
