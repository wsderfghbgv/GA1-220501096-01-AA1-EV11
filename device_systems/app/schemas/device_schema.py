"""
Device schemas for device_systems.
Pydantic v2 models for device validation and serialization.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import datetime


VALID_STATUSES = ["available", "loaned", "maintenance"]


class DeviceBase(BaseModel):
    """Base schema with common device fields."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name or description of the device",
        examples=["Laptop Dell Latitude"]
    )
    brand: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Brand or manufacturer",
        examples=["Dell"]
    )
    model: Optional[str] = Field(
        None,
        max_length=50,
        description="Device model identifier",
        examples=["Latitude 5520"]
    )
    serial_number: Optional[str] = Field(
        None,
        max_length=100,
        description="Unique serial number",
        examples=["SN-2024-001"]
    )


class DeviceCreate(DeviceBase):
    """Schema for creating a new device."""
    status: str = Field(
        default="available",
        description="Initial device status",
        examples=["available"]
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that the status is one of the allowed values."""
        if v.lower() not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return v.lower()


class DeviceUpdate(BaseModel):
    """Schema for updating device fields."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    brand: Optional[str] = Field(None, min_length=1, max_length=50)
    model: Optional[str] = Field(None, max_length=50)
    serial_number: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate that the status is one of the allowed values."""
        if v is not None and v.lower() not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return v.lower() if v else v


class DeviceResponse(BaseModel):
    """Schema for device responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Device ID")
    name: str = Field(..., description="Device name")
    brand: str = Field(..., description="Brand")
    model: Optional[str] = Field(None, description="Model")
    serial_number: Optional[str] = Field(None, description="Serial number")
    status: str = Field(..., description="Current status")
    created_at: Optional[datetime] = Field(None, description="Registration timestamp")
