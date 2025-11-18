"""
Template CRUD router with create, read, update, delete, and publishing operations.
Supports personal, practice, and community templates.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime
import logging

from src.api.database import get_db
from src.api.models.user import User, UserRole
from src.api.models.template import Template, TemplateType, TemplateCategory
from src.api.schemas.template_schemas import (
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplatePublishRequest,
    TemplateResponse,
    TemplateListResponse,
    TemplateFilterRequest,
    TemplateUsageRequest,
    TemplateDuplicateRequest,
)
from src.api.auth.dependencies import get_current_user, require_role
from src.api.utils.pagination import paginate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/templates", tags=["Templates"])


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN))
):
    """
    Create a new SOAP template.

    Args:
        template_data: Template information
        db: Database session
        current_user: Current authenticated user (must be healthcare provider)

    Returns:
        TemplateResponse: Created template data

    Raises:
        HTTPException: If validation fails or other errors
    """
    logger.info(f"Creating template '{template_data.name}' for user: {current_user.id}")

    # Validate practice template has practice_id
    if template_data.type == TemplateType.PRACTICE and not template_data.practice_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Practice templates must have a practice_id"
        )

    try:
        new_template = Template(
            user_id=current_user.id,
            name=template_data.name,
            description=template_data.description,
            type=template_data.type,
            category=template_data.category,
            specialty=template_data.specialty,
            content=template_data.content.model_dump(),
            tags=template_data.tags,
            appointment_types=template_data.appointment_types,
            is_favorite=template_data.is_favorite,
            practice_id=template_data.practice_id,
            version="1.0",
        )

        db.add(new_template)
        db.commit()
        db.refresh(new_template)

        logger.info(f"Template created successfully: {new_template.id}")

        return TemplateResponse.model_validate(new_template.to_dict())

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database error creating template: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create template due to database constraint"
        )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get template by ID.

    Args:
        template_id: Template UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        TemplateResponse: Template data

    Raises:
        HTTPException: If template not found or access denied
    """
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Access control
    # Users can access: their own templates, published community templates, or practice templates from their practice
    can_access = (
        template.user_id == current_user.id or
        (template.type == TemplateType.COMMUNITY and template.is_published) or
        (template.type == TemplateType.PRACTICE and template.practice_id)  # TODO: Add practice membership check
    )

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return TemplateResponse.model_validate(template.to_dict())


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    type: Optional[TemplateType] = Query(None, description="Filter by template type"),
    category: Optional[TemplateCategory] = Query(None, description="Filter by category"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    appointment_type: Optional[str] = Query(None, description="Filter by appointment type"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    is_favorite: Optional[bool] = Query(None, description="Filter favorites only"),
    practice_id: Optional[str] = Query(None, description="Filter by practice ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List templates with filtering and pagination.

    Returns templates visible to the current user:
    - Personal templates created by the user
    - Published community templates
    - Practice templates from user's practice

    Args:
        type: Filter by template type
        category: Filter by medical specialty
        specialty: Filter by detailed specialty
        tags: Comma-separated tags to filter
        appointment_type: Filter by appointment type
        search: Search term for name/description
        is_favorite: Show only favorites
        practice_id: Filter by practice
        page: Page number
        page_size: Items per page
        db: Database session
        current_user: Current authenticated user

    Returns:
        TemplateListResponse: Paginated list of templates
    """
    # Base query - user can see their own templates, community templates, or practice templates
    query = db.query(Template).filter(
        or_(
            Template.user_id == current_user.id,
            and_(Template.type == TemplateType.COMMUNITY, Template.is_published == True),
            # TODO: Add practice membership check for practice templates
        )
    )

    # Apply filters
    if type:
        query = query.filter(Template.type == type)

    if category:
        query = query.filter(Template.category == category)

    if specialty:
        query = query.filter(Template.specialty.ilike(f"%{specialty}%"))

    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        # Filter templates that have any of the specified tags
        for tag in tag_list:
            query = query.filter(Template.tags.contains([tag]))

    if appointment_type:
        query = query.filter(Template.appointment_types.contains([appointment_type]))

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Template.name.ilike(search_filter),
                Template.description.ilike(search_filter)
            )
        )

    if is_favorite is not None:
        query = query.filter(Template.is_favorite == is_favorite)

    if practice_id:
        query = query.filter(Template.practice_id == practice_id)

    # Filter only active templates
    query = query.filter(Template.is_active == True)

    # Order by: favorites first, then usage count, then created date
    query = query.order_by(
        Template.is_favorite.desc(),
        Template.usage_count.desc(),
        Template.created_at.desc()
    )

    # Paginate
    items, total, total_pages = paginate(query, page=page, page_size=page_size)

    # Convert to response models
    template_responses = [TemplateResponse.model_validate(t.to_dict()) for t in items]

    return TemplateListResponse(
        items=template_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template_data: TemplateUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update template information.

    Args:
        template_id: Template UUID
        template_data: Updated template information
        db: Database session
        current_user: Current authenticated user

    Returns:
        TemplateResponse: Updated template data

    Raises:
        HTTPException: If template not found or access denied
    """
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Only owner can update template
    if template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only template owner can update it"
        )

    # Update fields if provided
    update_data = template_data.model_dump(exclude_unset=True)

    # Handle SOAP content separately
    if "content" in update_data and update_data["content"]:
        update_data["content"] = update_data["content"].model_dump()

    for field, value in update_data.items():
        setattr(template, field, value)

    try:
        db.commit()
        db.refresh(template)

        logger.info(f"Template updated successfully: {template.id}")

        return TemplateResponse.model_validate(template.to_dict())

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database error updating template: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update template"
        )


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a template (soft delete by setting is_active=False).

    Args:
        template_id: Template UUID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If template not found or access denied
    """
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Only owner can delete template
    if template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only template owner can delete it"
        )

    # Soft delete
    template.is_active = False
    db.commit()

    logger.info(f"Template deleted: {template_id} by user {current_user.id}")

    return None


@router.post("/{template_id}/publish", response_model=TemplateResponse)
async def publish_template(
    template_id: str,
    publish_data: TemplatePublishRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN))
):
    """
    Publish a personal template to the community.

    Args:
        template_id: Template UUID
        publish_data: Publishing information (author name, description)
        db: Database session
        current_user: Current authenticated user (must be healthcare provider)

    Returns:
        TemplateResponse: Published template data

    Raises:
        HTTPException: If template not found, access denied, or already published
    """
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Only owner can publish
    if template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only template owner can publish it"
        )

    # Can only publish personal templates
    if template.type != TemplateType.PERSONAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only personal templates can be published to community"
        )

    # Check if already published
    if template.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template is already published"
        )

    # Update to community template
    template.type = TemplateType.COMMUNITY
    template.is_published = True
    template.author_name = publish_data.author_name
    template.author_id = current_user.id

    if publish_data.description:
        template.description = publish_data.description

    try:
        db.commit()
        db.refresh(template)

        logger.info(f"Template published to community: {template.id}")

        return TemplateResponse.model_validate(template.to_dict())

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database error publishing template: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to publish template"
        )


@router.post("/{template_id}/unpublish", response_model=TemplateResponse)
async def unpublish_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unpublish a community template (revert to personal).

    Args:
        template_id: Template UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        TemplateResponse: Unpublished template data

    Raises:
        HTTPException: If template not found, access denied, or not published
    """
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Only author can unpublish
    if template.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only template author can unpublish it"
        )

    if not template.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template is not published"
        )

    # Revert to personal template
    template.type = TemplateType.PERSONAL
    template.is_published = False

    db.commit()
    db.refresh(template)

    logger.info(f"Template unpublished: {template.id}")

    return TemplateResponse.model_validate(template.to_dict())


@router.post("/{template_id}/duplicate", response_model=TemplateResponse)
async def duplicate_template(
    template_id: str,
    duplicate_data: TemplateDuplicateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Duplicate a template to create a personal copy.

    Args:
        template_id: Template UUID to duplicate
        duplicate_data: Duplicate request data (optional new name)
        db: Database session
        current_user: Current authenticated user

    Returns:
        TemplateResponse: Newly created template copy

    Raises:
        HTTPException: If template not found or access denied
    """
    original_template = db.query(Template).filter(Template.id == template_id).first()

    if not original_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Check access (same as get_template)
    can_access = (
        original_template.user_id == current_user.id or
        (original_template.type == TemplateType.COMMUNITY and original_template.is_published) or
        (original_template.type == TemplateType.PRACTICE and original_template.practice_id)
    )

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Create new template as personal copy
    new_name = duplicate_data.new_name or f"Copy of {original_template.name}"

    try:
        new_template = Template(
            user_id=current_user.id,
            name=new_name,
            description=original_template.description,
            type=TemplateType.PERSONAL,  # Always create as personal
            category=original_template.category,
            specialty=original_template.specialty,
            content=original_template.content,
            tags=original_template.tags,
            appointment_types=original_template.appointment_types,
            is_favorite=False,  # Don't copy favorite status
            version="1.0",  # Reset version
        )

        db.add(new_template)
        db.commit()
        db.refresh(new_template)

        logger.info(f"Template duplicated: {template_id} -> {new_template.id}")

        return TemplateResponse.model_validate(new_template.to_dict())

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database error duplicating template: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to duplicate template"
        )


@router.post("/{template_id}/use", response_model=TemplateResponse)
async def record_template_usage(
    template_id: str,
    usage_data: TemplateUsageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record template usage (increment usage count and update last_used timestamp).

    Args:
        template_id: Template UUID
        usage_data: Usage tracking data (optional visit_id)
        db: Database session
        current_user: Current authenticated user

    Returns:
        TemplateResponse: Updated template data

    Raises:
        HTTPException: If template not found or access denied
    """
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Check access (same as get_template)
    can_access = (
        template.user_id == current_user.id or
        (template.type == TemplateType.COMMUNITY and template.is_published) or
        (template.type == TemplateType.PRACTICE and template.practice_id)
    )

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Update usage tracking
    template.usage_count += 1
    template.last_used = datetime.utcnow().isoformat()

    db.commit()
    db.refresh(template)

    logger.info(f"Template usage recorded: {template_id} by user {current_user.id}")

    return TemplateResponse.model_validate(template.to_dict())


@router.post("/{template_id}/favorite", response_model=TemplateResponse)
async def toggle_favorite(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle template favorite status.

    Args:
        template_id: Template UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        TemplateResponse: Updated template data

    Raises:
        HTTPException: If template not found or access denied
    """
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Only owner can toggle favorite
    if template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only template owner can toggle favorite"
        )

    # Toggle favorite
    template.is_favorite = not template.is_favorite

    db.commit()
    db.refresh(template)

    logger.info(f"Template favorite toggled: {template_id} -> {template.is_favorite}")

    return TemplateResponse.model_validate(template.to_dict())
