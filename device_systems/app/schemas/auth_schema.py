"""
Authentication schemas for device_systems.
Pydantic v2 models with advanced validation for registration and login.
"""

import re
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator, model_validator


VALID_ROLES = ["admin", "support", "user"]


class UserRegister(BaseModel):
    """
    Schema for user registration.
    Applies strict password validation rules.
    """
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the user",
        examples=["Juan Pérez"]
    )
    email: EmailStr = Field(
        ...,
        description="Valid and unique email address",
        examples=["juan@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Secure password (min 8 chars, 1 uppercase, 1 lowercase, 1 digit, no spaces)",
        examples=["SecurePass1"]
    )
    role: str = Field(
        default="user",
        description="User role (admin, support, user)",
        examples=["user"]
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets security requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - No whitespace characters
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if " " in v or "\t" in v or "\n" in v:
            raise ValueError("Password must not contain whitespace characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate that the role is one of the allowed values."""
        if v.lower() not in VALID_ROLES:
            raise ValueError(f"Role must be one of: {', '.join(VALID_ROLES)}")
        return v.lower()

    @model_validator(mode="after")
    def validate_name_not_email(self):
        """Ensure the name is not the same as the email."""
        if self.name.lower() == self.email.lower():
            raise ValueError("Name cannot be the same as the email address")
        return self


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(
        ...,
        description="Registered email address",
        examples=["juan@example.com"]
    )
    password: str = Field(
        ...,
        min_length=1,
        description="User password",
        examples=["SecurePass1"]
    )


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Schema for decoded token data."""
    email: str | None = Field(None, description="User email from token")
