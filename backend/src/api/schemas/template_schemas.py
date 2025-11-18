"""
Pydantic schemas for SOAP template requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from src.api.models.template import TemplateType, TemplateCategory


class SOAPContent(BaseModel):
    """Schema for SOAP note content structure."""

    subjective: str = Field("", description="Subjective section content")
    objective: str = Field("", description="Objective section content")
    assessment: str = Field("", description="Assessment section content")
    plan: str = Field("", description="Plan section content")

    class Config:
        json_schema_extra = {
            "example": {
                "subjective": "Patient reports [chief_complaint]. Symptoms started [duration] ago.",
                "objective": "Vital Signs: BP [bp], HR [hr], Temp [temp]\nExamination findings...",
                "assessment": "Primary diagnosis: [diagnosis]",
                "plan": "Treatment plan: [treatment]\nFollow-up: [follow_up]"
            }
        }


class TemplateCreateRequest(BaseModel):
    """Schema for creating a new template."""

    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: Optional[str] = Field(None, max_length=1000, description="Template description")
    type: TemplateType = Field(TemplateType.PERSONAL, description="Template type (personal/practice/community)")
    category: TemplateCategory = Field(TemplateCategory.GENERAL, description="Medical specialty category")
    specialty: Optional[str] = Field(None, max_length=100, description="Detailed specialty")
    content: SOAPContent = Field(..., description="SOAP note content")
    tags: Optional[List[str]] = Field(default_factory=list, description="Search tags")
    appointment_types: Optional[List[str]] = Field(default_factory=list, description="Applicable appointment types")
    is_favorite: bool = Field(False, description="Mark as favorite")
    practice_id: Optional[str] = Field(None, max_length=36, description="Practice ID (for practice templates)")

    @validator("tags")
    def validate_tags(cls, v):
        """Validate tags list."""
        if v and len(v) > 20:
            raise ValueError("Maximum 20 tags allowed")
        if v:
            for tag in v:
                if len(tag) > 50:
                    raise ValueError("Tag length cannot exceed 50 characters")
        return v

    @validator("appointment_types")
    def validate_appointment_types(cls, v):
        """Validate appointment types list."""
        if v and len(v) > 10:
            raise ValueError("Maximum 10 appointment types allowed")
        return v

    @validator("name")
    def validate_name(cls, v):
        """Validate template name."""
        if not v.strip():
            raise ValueError("Template name cannot be empty or whitespace")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Diabetes Follow-up Visit",
                "description": "Standard template for routine diabetes management visits",
                "type": "personal",
                "category": "General",
                "specialty": "Endocrinology",
                "content": {
                    "subjective": "Patient with Type 2 Diabetes here for follow-up. Reports blood sugars ranging from [fasting_glucose] to [post_meal_glucose]. Compliance with medications: [compliance]. Diet and exercise: [lifestyle].",
                    "objective": "Vital Signs: BP [bp], Weight [weight], BMI [bmi]\nA1C: [a1c]%\nFoot exam: [foot_exam]\nEye exam: [eye_exam]",
                    "assessment": "Type 2 Diabetes Mellitus - [control_status]\nHypertension - [bp_status]\nDyslipidemia - [lipid_status]",
                    "plan": "1. Continue current medications\n2. A1C goal: <7%\n3. Refer to ophthalmology for annual exam\n4. Follow-up in 3 months\n5. Lab: A1C, lipid panel, microalbumin"
                },
                "tags": ["diabetes", "chronic-care", "follow-up", "endocrinology"],
                "appointment_types": ["Follow-up", "Chronic Care Management"],
                "is_favorite": True
            }
        }


class TemplateUpdateRequest(BaseModel):
    """Schema for updating a template (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[TemplateCategory] = None
    specialty: Optional[str] = Field(None, max_length=100)
    content: Optional[SOAPContent] = None
    tags: Optional[List[str]] = None
    appointment_types: Optional[List[str]] = None
    is_favorite: Optional[bool] = None
    is_active: Optional[bool] = None

    @validator("tags")
    def validate_tags(cls, v):
        """Validate tags list."""
        if v and len(v) > 20:
            raise ValueError("Maximum 20 tags allowed")
        if v:
            for tag in v:
                if len(tag) > 50:
                    raise ValueError("Tag length cannot exceed 50 characters")
        return v

    @validator("appointment_types")
    def validate_appointment_types(cls, v):
        """Validate appointment types list."""
        if v and len(v) > 10:
            raise ValueError("Maximum 10 appointment types allowed")
        return v

    @validator("name")
    def validate_name(cls, v):
        """Validate template name."""
        if v is not None and not v.strip():
            raise ValueError("Template name cannot be empty or whitespace")
        return v.strip() if v else v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Template Name",
                "is_favorite": True,
                "tags": ["updated-tag"]
            }
        }


class TemplatePublishRequest(BaseModel):
    """Schema for publishing a template to community."""

    author_name: str = Field(..., min_length=1, max_length=255, description="Author display name")
    description: Optional[str] = Field(None, max_length=1000, description="Community description")

    class Config:
        json_schema_extra = {
            "example": {
                "author_name": "Dr. Jane Smith",
                "description": "A comprehensive template for diabetes management visits based on ADA guidelines"
            }
        }


class TemplateResponse(BaseModel):
    """Schema for template response."""

    id: str
    user_id: str
    name: str
    description: Optional[str]
    type: str
    category: str
    specialty: Optional[str]
    content: Dict[str, Any]
    tags: List[str]
    appointment_types: List[str]
    usage_count: int
    is_favorite: bool
    last_used: Optional[str]
    version: str
    author_name: Optional[str]
    author_id: Optional[str]
    practice_id: Optional[str]
    is_published: bool
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """Schema for paginated template list response."""

    items: List[TemplateResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 50,
                "page": 1,
                "page_size": 20,
                "total_pages": 3
            }
        }


class TemplateFilterRequest(BaseModel):
    """Schema for filtering templates."""

    type: Optional[TemplateType] = Field(None, description="Filter by template type")
    category: Optional[TemplateCategory] = Field(None, description="Filter by category")
    specialty: Optional[str] = Field(None, description="Filter by specialty")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (OR logic)")
    appointment_type: Optional[str] = Field(None, description="Filter by appointment type")
    search: Optional[str] = Field(None, description="Search in name and description")
    is_favorite: Optional[bool] = Field(None, description="Filter favorites only")
    is_published: Optional[bool] = Field(None, description="Filter published templates")
    practice_id: Optional[str] = Field(None, description="Filter by practice ID")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")

    class Config:
        json_schema_extra = {
            "example": {
                "category": "Cardiology",
                "tags": ["follow-up", "chronic-care"],
                "search": "diabetes",
                "is_favorite": True,
                "page": 1,
                "page_size": 20
            }
        }


class TemplateUsageRequest(BaseModel):
    """Schema for recording template usage."""

    visit_id: Optional[str] = Field(None, description="Visit ID where template was used")

    class Config:
        json_schema_extra = {
            "example": {
                "visit_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class TemplateDuplicateRequest(BaseModel):
    """Schema for duplicating a template."""

    new_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name for the duplicate (defaults to 'Copy of [original]')")

    class Config:
        json_schema_extra = {
            "example": {
                "new_name": "My Custom Diabetes Template"
            }
        }
