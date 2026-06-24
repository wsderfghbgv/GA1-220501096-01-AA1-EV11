"""
User schemas for device_systems.
Pydantic v2 models for user validation and serialization.
"""

from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base schema with common user fields."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the user",
        examples=["Juan Pérez"]
    )
    email: EmailStr = Field(
        ...,
        description="Unique email address",
        examples=["juan@example.com"]
    )


class UserCreate(UserBase):
    """Schema for creating a user (admin use, without password)."""
    role: str = Field(
        default="user",
        description="User role (admin, support, user)",
        examples=["user"]
    )


class UserUpdate(BaseModel):
    """Schema for updating user fields."""
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Full name of the user"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Email address"
    )
    role: Optional[str] = Field(
        None,
        description="User role (admin, support, user)"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the user account is active"
    )


class UserResponse(BaseModel):
    """
    Schema for user responses.
    Never includes hashed_password.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="User ID")
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Account active status")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")
