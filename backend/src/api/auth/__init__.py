"""
Authentication package for JWT token handling and user authentication.

Provides:
- Password hashing and verification
- JWT token creation and verification
- User authentication dependencies
- Role-based access control (legacy + new scoped system)
- Permission-based access control
- Support access grant verification
"""

from src.api.auth.password import hash_password, verify_password
from src.api.auth.jwt_handler import create_access_token, verify_token, create_refresh_token
from src.api.auth.dependencies import (
    # Core authentication
    get_current_user,
    get_current_active_user,
    get_optional_user,
    get_current_user_with_tenant,
    # Legacy role checking (uses UserRole enum)
    require_role,
    require_super_admin,
    require_tenant_admin,
    require_permission,
    require_tenant_access,
    # New scoped permission system
    require_permissions,
    require_all_permissions,
    require_platform_admin,
    require_regional_access,
    require_scoped_tenant_access,
    require_support_access,
    require_clinical_access,
)

__all__ = [
    # Password utilities
    "hash_password",
    "verify_password",
    # JWT handling
    "create_access_token",
    "verify_token",
    "create_refresh_token",
    # Core authentication
    "get_current_user",
    "get_current_active_user",
    "get_optional_user",
    "get_current_user_with_tenant",
    # Legacy role checking
    "require_role",
    "require_super_admin",
    "require_tenant_admin",
    "require_permission",
    "require_tenant_access",
    # New scoped permission system
    "require_permissions",
    "require_all_permissions",
    "require_platform_admin",
    "require_regional_access",
    "require_scoped_tenant_access",
    "require_support_access",
    "require_clinical_access",
]
