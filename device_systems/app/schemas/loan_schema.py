"""
Loan schemas for device_systems.
Pydantic v2 models for loan validation and serialization.
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional
from datetime import datetime


class LoanBase(BaseModel):
    """Base schema with common loan fields."""
    user_id: int = Field(
        ...,
        gt=0,
        description="ID of the user requesting the loan",
        examples=[1]
    )
    device_id: int = Field(
        ...,
        gt=0,
        description="ID of the device to loan",
        examples=[1]
    )


class LoanCreate(LoanBase):
    """Schema for creating a new loan."""

    @model_validator(mode="after")
    def validate_ids_different(self):
        """Ensure user_id and device_id are valid positive integers."""
        if self.user_id <= 0 or self.device_id <= 0:
            raise ValueError("user_id and device_id must be positive integers")
        return self


class LoanResponse(BaseModel):
    """Schema for loan responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Loan ID")
    user_id: int = Field(..., description="User ID")
    device_id: int = Field(..., description="Device ID")
    loan_date: Optional[datetime] = Field(None, description="Loan start date")
    return_date: Optional[datetime] = Field(None, description="Return date")
    status: str = Field(..., description="Loan status (active, returned)")


class LoanDetailResponse(BaseModel):
    """
    Detailed loan response including user and device information.
    Used for GET /loans/details endpoint with join queries.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Loan ID")
    loan_date: Optional[datetime] = Field(None, description="Loan start date")
    return_date: Optional[datetime] = Field(None, description="Return date")
    status: str = Field(..., description="Loan status")
    user_name: str = Field(..., description="Name of the user")
    user_email: str = Field(..., description="Email of the user")
    device_name: str = Field(..., description="Name of the device")
    device_brand: str = Field(..., description="Brand of the device")
    device_serial: Optional[str] = Field(None, description="Serial number of the device")
