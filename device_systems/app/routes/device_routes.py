"""
Device routes for device_systems.
CRUD endpoints for device management with role-based protection.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.dependencies.auth_dependency import (
    get_current_active_user,
    require_admin,
    require_admin_or_support
)
from app.services.device_service import (
    get_devices,
    get_device,
    create_device,
    update_device,
    delete_device
)
from app.schemas.device_schema import DeviceCreate, DeviceUpdate, DeviceResponse
from app.models.user_model import User

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get(
    "/",
    response_model=list[DeviceResponse],
    summary="Get all devices",
    description="Retrieve a list of all registered devices. Requires authentication.",
    responses={
        401: {"description": "Not authenticated"}
    }
)
def read_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all devices. Requires authenticated user."""
    return get_devices(db)


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Get device by ID",
    description="Retrieve a specific device by its ID. Requires authentication.",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Device not found"}
    }
)
def read_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific device by ID. Requires authenticated user."""
    return get_device(db, device_id)


@router.post(
    "/",
    response_model=DeviceResponse,
    status_code=201,
    summary="Create a new device",
    description="Register a new device in the system. Requires admin or support role.",
    responses={
        400: {"description": "Duplicate serial number"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions (admin or support required)"}
    }
)
def create_new_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_support)
):
    """Create a new device. Requires admin or support role."""
    return create_device(db, device_data)


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Update a device",
    description="Update an existing device's information. Requires admin or support role.",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions (admin or support required)"},
        404: {"description": "Device not found"}
    }
)
def update_existing_device(
    device_id: int,
    device_data: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_support)
):
    """Update an existing device. Requires admin or support role."""
    return update_device(db, device_id, device_data)


@router.delete(
    "/{device_id}",
    summary="Delete a device",
    description="Delete a device from the system. Requires admin role only.",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions (admin required)"},
        404: {"description": "Device not found"}
    }
)
def delete_existing_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a device by ID. Requires admin role only."""
    return delete_device(db, device_id)
