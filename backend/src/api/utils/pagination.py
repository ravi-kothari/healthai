"""
Pagination utilities for list endpoints.
"""

from typing import TypeVar, Generic, List
from pydantic import BaseModel
from sqlalchemy.orm import Query
from math import ceil

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = 1
    page_size: int = 20

    def get_offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size

    def get_limit(self) -> int:
        """Get limit for database query."""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


def paginate(query: Query, page: int = 1, page_size: int = 20, max_page_size: int = 100) -> tuple:
    """
    Paginate a SQLAlchemy query.

    Args:
        query: SQLAlchemy query to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page
        max_page_size: Maximum allowed page size

    Returns:
        tuple: (items, total_count, total_pages)

    Example:
        >>> query = db.query(Patient)
        >>> items, total, pages = paginate(query, page=1, page_size=20)
    """
    # Validate and limit page size
    page_size = min(page_size, max_page_size)
    page = max(1, page)  # Ensure page is at least 1

    # Get total count
    total_count = query.count()

    # Calculate total pages
    total_pages = ceil(total_count / page_size) if total_count > 0 else 1

    # Calculate offset
    offset = (page - 1) * page_size

    # Get items
    items = query.offset(offset).limit(page_size).all()

    return items, total_count, total_pages
