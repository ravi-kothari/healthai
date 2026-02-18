"""
Pydantic schemas for user management API.

Covers:
- User CRUD operations (admin)
- User invitations
- Role assignments (scoped)
- Support access grants
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class ScopeType(str, Enum):
    """Scope types for role assignments."""
    PLATFORM = "platform"
    REGIONAL = "regional"
    TENANT = "tenant"


class AccessLevel(str, Enum):
    """Support access levels."""
    METADATA = "metadata"
    FULL = "full"


# =============================================================================
# Role Schemas
# =============================================================================

class RoleResponse(BaseModel):
    """Response schema for a role."""
    id: str
    name: str
    display_name: str
    description: Optional[str]
    scope: str
    permissions: List[str]
    is_system: bool

    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    """Response schema for listing roles."""
    roles: List[RoleResponse]
    total: int


# =============================================================================
# User Role Assignment Schemas
# =============================================================================

class UserRoleAssignment(BaseModel):
    """Schema for a user's role assignment."""
    id: str
    role_id: str
    role_name: str
    role_display_name: str
    scope_type: str
    scope_id: Optional[str]
    is_primary: bool
    granted_by: Optional[str]
    granted_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class AssignRoleRequest(BaseModel):
    """Request schema for assigning a role to a user."""
    role_name: str = Field(..., description="Name of the role to assign")
    scope_type: ScopeType = Field(..., description="Scope type (platform, regional, tenant)")
    scope_id: Optional[str] = Field(None, description="Scope ID (region_id or tenant_id). Required for regional/tenant scope.")
    is_primary: bool = Field(False, description="Whether this is the user's primary role")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration datetime")

    @field_validator("scope_id")
    @classmethod
    def validate_scope_id(cls, v, info):
        # This will be further validated in the endpoint
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "role_name": "provider",
                "scope_type": "tenant",
                "scope_id": "tenant-uuid-here",
                "is_primary": True
            }
        }


class RevokeRoleRequest(BaseModel):
    """Request schema for revoking a role from a user."""
    role_name: str = Field(..., description="Name of the role to revoke")
    scope_type: ScopeType = Field(..., description="Scope type")
    scope_id: Optional[str] = Field(None, description="Scope ID")

    class Config:
        json_schema_extra = {
            "example": {
                "role_name": "provider",
                "scope_type": "tenant",
                "scope_id": "tenant-uuid-here"
            }
        }


# =============================================================================
# User Management Schemas
# =============================================================================

class UserCreateRequest(BaseModel):
    """Request schema for creating a user (admin operation)."""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=8, max_length=100, description="Initial password")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    tenant_id: Optional[str] = Field(None, description="Tenant ID (required for tenant-scoped users)")
    role_name: str = Field("patient", description="Initial role to assign")
    is_verified: bool = Field(False, description="Whether email is pre-verified")
    send_welcome_email: bool = Field(True, description="Whether to send welcome email")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "email": "newuser@example.com",
                "username": "new_user",
                "password": "SecurePass123",
                "full_name": "New User",
                "phone": "+1-555-0123",
                "tenant_id": "tenant-uuid-here",
                "role_name": "provider",
                "is_verified": True,
                "send_welcome_email": True
            }
        }


class UserUpdateRequest(BaseModel):
    """Request schema for updating a user."""
    email: Optional[EmailStr] = Field(None, description="New email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="New full name")
    phone: Optional[str] = Field(None, max_length=20, description="New phone number")
    is_active: Optional[bool] = Field(None, description="Activate/deactivate user")
    is_verified: Optional[bool] = Field(None, description="Mark email as verified")

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Updated Name",
                "phone": "+1-555-9999",
                "is_active": True
            }
        }


class UserDetailResponse(BaseModel):
    """Detailed user response with roles."""
    id: str
    email: str
    username: str
    full_name: str
    phone: Optional[str]
    is_active: bool
    is_verified: bool
    tenant_id: Optional[str]
    tenant_name: Optional[str] = None
    roles: List[UserRoleAssignment] = []
    created_at: datetime
    updated_at: Optional[datetime]
    last_login_at: Optional[datetime] = None
    login_count: int = 0

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "user-uuid-here",
                "email": "user@example.com",
                "username": "john_doe",
                "full_name": "John Doe",
                "phone": "+1-555-0123",
                "is_active": True,
                "is_verified": True,
                "tenant_id": "tenant-uuid-here",
                "tenant_name": "Acme Healthcare",
                "roles": [
                    {
                        "id": "role-assignment-uuid",
                        "role_id": "role-uuid",
                        "role_name": "provider",
                        "role_display_name": "Healthcare Provider",
                        "scope_type": "tenant",
                        "scope_id": "tenant-uuid-here",
                        "is_primary": True,
                        "granted_by": "admin-uuid",
                        "granted_at": "2024-01-01T00:00:00Z",
                        "expires_at": None
                    }
                ],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T00:00:00Z",
                "last_login_at": "2024-01-20T00:00:00Z",
                "login_count": 42
            }
        }


class UserListItemResponse(BaseModel):
    """User item in a list response (minimal info)."""
    id: str
    email: str
    username: str
    full_name: str
    is_active: bool
    is_verified: bool
    primary_role: Optional[str] = None
    tenant_id: Optional[str]
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Paginated list of users."""
    users: List[UserListItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserListFilters(BaseModel):
    """Filters for listing users."""
    search: Optional[str] = Field(None, description="Search by email, username, or name")
    role_name: Optional[str] = Field(None, description="Filter by role name")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_verified: Optional[bool] = Field(None, description="Filter by verified status")
    tenant_id: Optional[str] = Field(None, description="Filter by tenant")


# =============================================================================
# User Invitation Schemas
# =============================================================================

class UserInviteRequest(BaseModel):
    """Request schema for inviting a user."""
    email: EmailStr = Field(..., description="Email to send invitation to")
    role_name: str = Field(..., description="Role to assign upon acceptance")
    full_name: Optional[str] = Field(None, description="Optional pre-filled name")
    message: Optional[str] = Field(None, max_length=500, description="Custom invitation message")
    expires_in_days: int = Field(7, ge=1, le=30, description="Days until invitation expires")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "newdoctor@example.com",
                "role_name": "provider",
                "full_name": "Dr. Jane Smith",
                "message": "Welcome to our practice!",
                "expires_in_days": 7
            }
        }


class UserInvitationResponse(BaseModel):
    """Response schema for a user invitation."""
    id: str
    email: str
    role_name: str
    tenant_id: str
    tenant_name: str
    invited_by: str
    invited_by_name: str
    status: str  # pending, accepted, expired, cancelled
    created_at: datetime
    expires_at: datetime
    accepted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvitationListResponse(BaseModel):
    """Paginated list of invitations."""
    invitations: List[UserInvitationResponse]
    total: int
    page: int
    page_size: int


# =============================================================================
# Support Access Grant Schemas
# =============================================================================

class SupportAccessRequestCreate(BaseModel):
    """Request schema for requesting support access."""
    tenant_id: str = Field(..., description="Tenant to request access to")
    reason: str = Field(..., min_length=10, max_length=500, description="Reason for access request")
    access_level: AccessLevel = Field(AccessLevel.METADATA, description="Requested access level")
    duration_hours: int = Field(24, ge=1, le=48, description="Requested duration in hours (max 48)")

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant-uuid-here",
                "reason": "Investigating reported issue with appointment scheduling",
                "access_level": "metadata",
                "duration_hours": 24
            }
        }


class SupportAccessGrantCreate(BaseModel):
    """Request schema for granting support access (tenant admin)."""
    support_user_id: str = Field(..., description="Support agent user ID")
    reason: str = Field(..., min_length=10, max_length=500, description="Reason for granting access")
    access_level: AccessLevel = Field(AccessLevel.METADATA, description="Access level to grant")
    duration_hours: int = Field(24, ge=1, le=48, description="Duration in hours (max 48)")

    class Config:
        json_schema_extra = {
            "example": {
                "support_user_id": "support-user-uuid",
                "reason": "Approved access for ticket #12345",
                "access_level": "metadata",
                "duration_hours": 24
            }
        }


class SupportAccessGrantResponse(BaseModel):
    """Response schema for a support access grant."""
    id: str
    tenant_id: str
    tenant_name: str
    granted_to_user_id: str
    granted_to_name: str
    granted_by_user_id: str
    granted_by_name: str
    reason: str
    access_level: str
    is_active: bool
    created_at: datetime
    expires_at: datetime
    revoked_at: Optional[datetime] = None
    revoked_by: Optional[str] = None

    class Config:
        from_attributes = True


class SupportAccessGrantListResponse(BaseModel):
    """List of support access grants."""
    grants: List[SupportAccessGrantResponse]
    total: int


class RevokeAccessRequest(BaseModel):
    """Request schema for revoking support access."""
    reason: Optional[str] = Field(None, max_length=500, description="Optional reason for revocation")

    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Issue resolved, access no longer needed"
            }
        }


# =============================================================================
# Password Management Schemas
# =============================================================================

class PasswordResetRequest(BaseModel):
    """Request schema for initiating password reset."""
    email: EmailStr = Field(..., description="Email address")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """Request schema for confirming password reset."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class PasswordChangeRequest(BaseModel):
    """Request schema for changing password (authenticated user)."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


# =============================================================================
# Bulk Operations Schemas
# =============================================================================

class BulkUserActionRequest(BaseModel):
    """Request schema for bulk user operations."""
    user_ids: List[str] = Field(..., min_length=1, max_length=100, description="List of user IDs")
    action: str = Field(..., description="Action to perform: activate, deactivate, delete")

    @field_validator("action")
    @classmethod
    def validate_action(cls, v):
        allowed = ["activate", "deactivate", "delete"]
        if v not in allowed:
            raise ValueError(f"Action must be one of: {', '.join(allowed)}")
        return v


class BulkActionResult(BaseModel):
    """Result of a bulk operation."""
    success_count: int
    failure_count: int
    failures: List[dict] = []  # List of {user_id, error}
