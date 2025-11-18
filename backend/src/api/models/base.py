"""
Base model with common fields for all database models.
"""

from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func
from datetime import datetime
import uuid


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class UUIDMixin:
    """Mixin for UUID primary key."""

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())
