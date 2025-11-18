"""
User model for authentication and authorization.
Supports both patients and healthcare providers.
"""

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

from src.api.database import Base
from src.api.models.base import UUIDMixin, TimestampMixin


class UserRole(str, Enum):
    """User roles in the system."""

    PATIENT = "patient"
    DOCTOR = "doctor"
    NURSE = "nurse"
    ADMIN = "admin"
    STAFF = "staff"


class User(Base, UUIDMixin, TimestampMixin):
    """
    User model for authentication and authorization.

    Attributes:
        id: Unique identifier (UUID)
        email: User's email address (unique)
        username: Username (unique)
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        role: User role (patient, doctor, nurse, admin, staff)
        is_active: Whether the user account is active
        is_verified: Whether the user's email is verified
        phone: Phone number (optional)
    """

    __tablename__ = "users"

    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Profile fields
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)

    # Role and permissions
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.PATIENT)

    # Status flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    # patient relationship will be added when creating Patient model
    provider_visits = relationship("Visit", back_populates="provider", foreign_keys="Visit.provider_id")
    templates = relationship("Template", back_populates="user", foreign_keys="Template.user_id")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "phone": self.phone,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
