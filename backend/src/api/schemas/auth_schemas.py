"""
Pydantic schemas for authentication requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from src.api.models.user import UserRole


class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 characters)")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    role: UserRole = Field(default=UserRole.PATIENT, description="User role")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
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
        """Validate username format."""
        if not v.isalnum() and "_" not in v:
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "email": "patient@example.com",
                "username": "john_doe",
                "password": "SecurePass123",
                "full_name": "John Doe",
                "phone": "+1-555-0123",
                "role": "patient"
            }
        }


class UserLoginRequest(BaseModel):
    """Schema for user login request."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "SecurePass123"
            }
        }


class UserRoleUpdateRequest(BaseModel):
    """Schema for updating user role."""

    role: UserRole = Field(..., description="New user role")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "admin"
            }
        }


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class TenantInfo(BaseModel):
    """Schema for tenant information in responses."""

    id: str
    name: str
    slug: str
    subscription_plan: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Schema for user response."""

    id: str
    email: str
    username: str
    full_name: str
    phone: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    tenant_id: Optional[str] = None
    tenant: Optional[TenantInfo] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "patient@example.com",
                "username": "john_doe",
                "full_name": "John Doe",
                "phone": "+1-555-0123",
                "role": "patient",
                "is_active": True,
                "is_verified": False,
                "tenant_id": "defa0000-0000-0000-0000-000000000001",
                "tenant": {
                    "id": "defa0000-0000-0000-0000-000000000001",
                    "name": "Default Organization",
                    "slug": "default",
                    "subscription_plan": "professional"
                }
            }
        }


class AuthResponse(BaseModel):
    """Schema for authentication response with user and tokens."""

    user: UserResponse
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "patient@example.com",
                    "username": "john_doe",
                    "full_name": "John Doe",
                    "phone": "+1-555-0123",
                    "role": "patient",
                    "is_active": True,
                    "is_verified": False,
                    "tenant_id": "defa0000-0000-0000-0000-000000000001",
                    "tenant": {
                        "id": "defa0000-0000-0000-0000-000000000001",
                        "name": "Default Organization",
                        "slug": "default",
                        "subscription_plan": "professional"
                    }
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str = Field(..., description="Refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
