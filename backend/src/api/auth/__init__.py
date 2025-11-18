"""
Authentication package for JWT token handling and user authentication.
"""

from src.api.auth.password import hash_password, verify_password
from src.api.auth.jwt_handler import create_access_token, verify_token, create_refresh_token
from src.api.auth.dependencies import get_current_user, get_current_active_user, require_role

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "verify_token",
    "create_refresh_token",
    "get_current_user",
    "get_current_active_user",
    "require_role",
]
