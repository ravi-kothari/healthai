"""
SOAP Template model for storing reusable clinical note templates.
Supports personal, practice, and community templates with PHI scrubbing.
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, JSON, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from enum import Enum

from src.api.database import Base
from src.api.models.base import UUIDMixin, TimestampMixin


class TemplateType(str, Enum):
    """Template type options."""

    PERSONAL = "personal"
    PRACTICE = "practice"
    COMMUNITY = "community"


class TemplateCategory(str, Enum):
    """Template category options."""

    GENERAL = "General"
    CARDIOLOGY = "Cardiology"
    PEDIATRICS = "Pediatrics"
    DERMATOLOGY = "Dermatology"
    MENTAL_HEALTH = "Mental Health"
    ORTHOPEDICS = "Orthopedics"
    OTHER = "Other"


class Template(Base, UUIDMixin, TimestampMixin):
    """
    SOAP Template model for reusable clinical documentation.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to User model (creator)
        name: Template name
        description: Template description
        type: Template type (personal/practice/community)
        category: Medical specialty category
        specialty: Detailed specialty (optional)
        content: SOAP note content (JSON with subjective, objective, assessment, plan)
        tags: List of tags for searching (JSON array)
        appointment_types: Applicable appointment types (JSON array)
        usage_count: Number of times template has been used
        is_favorite: Whether user has favorited this template
        version: Template version number
        author_name: Name of template author (for community templates)
        author_id: User ID of author (for community templates)
        practice_id: Practice ID (for practice templates)
        is_published: Whether template is published to community
        is_active: Whether template is active/available
    """

    __tablename__ = "templates"

    # Basic Information
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Template Type and Category
    type = Column(SQLEnum(TemplateType), nullable=False, default=TemplateType.PERSONAL, index=True)
    category = Column(SQLEnum(TemplateCategory), nullable=False, default=TemplateCategory.GENERAL, index=True)
    specialty = Column(String(100), nullable=True)

    # SOAP Content (stored as JSON)
    # Example: {
    #   "subjective": "text with [placeholders]",
    #   "objective": "text with [placeholders]",
    #   "assessment": "text",
    #   "plan": "text"
    # }
    content = Column(JSON, nullable=False)

    # Metadata (stored as JSON arrays)
    tags = Column(JSON, nullable=True)  # ["diabetes", "chronic-care", "follow-up"]
    appointment_types = Column(JSON, nullable=True)  # ["Follow-up", "Chronic Care"]

    # Usage Tracking
    usage_count = Column(Integer, default=0, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    last_used = Column(String(50), nullable=True)  # ISO datetime string

    # Versioning
    version = Column(String(20), default="1.0", nullable=False)

    # Author Information (for community templates)
    author_name = Column(String(255), nullable=True)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Practice Information (for practice templates)
    practice_id = Column(String(36), nullable=True, index=True)

    # Publication Status
    is_published = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="templates")
    author = relationship("User", foreign_keys=[author_id])

    # Indexes for common queries
    __table_args__ = (
        Index("idx_template_user_type", "user_id", "type"),
        Index("idx_template_category_type", "category", "type"),
        Index("idx_template_practice", "practice_id", "type"),
        Index("idx_template_published", "is_published", "is_active"),
    )

    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}', type={self.type}, category={self.category})>"

    def to_dict(self):
        """Convert template to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value if isinstance(self.type, Enum) else self.type,
            "category": self.category.value if isinstance(self.category, Enum) else self.category,
            "specialty": self.specialty,
            "content": self.content,
            "tags": self.tags or [],
            "appointment_types": self.appointment_types or [],
            "usage_count": self.usage_count,
            "is_favorite": self.is_favorite,
            "last_used": self.last_used,
            "version": self.version,
            "author_name": self.author_name,
            "author_id": self.author_id,
            "practice_id": self.practice_id,
            "is_published": self.is_published,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
