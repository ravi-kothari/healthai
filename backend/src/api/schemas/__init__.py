"""
Pydantic schemas package.
"""

from src.api.schemas.auth_schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    AuthResponse,
    RefreshTokenRequest,
)
from src.api.schemas.patient_schemas import (
    PatientCreateRequest,
    PatientUpdateRequest,
    PatientResponse,
    PatientListResponse,
)
from src.api.schemas.template_schemas import (
    SOAPContent,
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplatePublishRequest,
    TemplateResponse,
    TemplateListResponse,
    TemplateFilterRequest,
    TemplateUsageRequest,
    TemplateDuplicateRequest,
)
from src.api.schemas.user_management_schemas import (
    # Enums
    ScopeType,
    AccessLevel,
    # Role schemas
    RoleResponse,
    RoleListResponse,
    # User role assignment
    UserRoleAssignment,
    AssignRoleRequest,
    RevokeRoleRequest,
    # User management
    UserCreateRequest,
    UserUpdateRequest,
    UserDetailResponse,
    UserListItemResponse,
    UserListResponse,
    UserListFilters,
    # Invitations
    UserInviteRequest,
    UserInvitationResponse,
    InvitationListResponse,
    # Support access
    SupportAccessRequestCreate,
    SupportAccessGrantCreate,
    SupportAccessGrantResponse,
    SupportAccessGrantListResponse,
    RevokeAccessRequest,
    # Password
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    # Bulk operations
    BulkUserActionRequest,
    BulkActionResult,
)

__all__ = [
    # Auth
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenResponse",
    "UserResponse",
    "AuthResponse",
    "RefreshTokenRequest",
    # Patients
    "PatientCreateRequest",
    "PatientUpdateRequest",
    "PatientResponse",
    "PatientListResponse",
    # Templates
    "SOAPContent",
    "TemplateCreateRequest",
    "TemplateUpdateRequest",
    "TemplatePublishRequest",
    "TemplateResponse",
    "TemplateListResponse",
    "TemplateFilterRequest",
    "TemplateUsageRequest",
    "TemplateDuplicateRequest",
    # User Management
    "ScopeType",
    "AccessLevel",
    "RoleResponse",
    "RoleListResponse",
    "UserRoleAssignment",
    "AssignRoleRequest",
    "RevokeRoleRequest",
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserDetailResponse",
    "UserListItemResponse",
    "UserListResponse",
    "UserListFilters",
    "UserInviteRequest",
    "UserInvitationResponse",
    "InvitationListResponse",
    "SupportAccessRequestCreate",
    "SupportAccessGrantCreate",
    "SupportAccessGrantResponse",
    "SupportAccessGrantListResponse",
    "RevokeAccessRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "PasswordChangeRequest",
    "BulkUserActionRequest",
    "BulkActionResult",
]
