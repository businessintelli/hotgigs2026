"""Authentication request and response schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="viewer", pattern="^(admin|manager|recruiter|viewer)$")


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    last_login: Optional[datetime] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Login response with tokens."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None  # Seconds
    user: Optional[UserResponse] = None


class PasswordChange(BaseModel):
    """Password change request."""
    old_password: str
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset with token."""
    email: EmailStr
    token: str
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
