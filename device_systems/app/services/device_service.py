"""
Device service for device_systems.
Handles device-related business logic and CRUD operations.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DeviceUpdate


def get_devices(db: Session) -> list[Device]:
    """
    Retrieve all devices from the database.

    Args:
        db: Database session.

    Returns:
        List of all Device instances.
    """
    return db.query(Device).all()


def get_device(db: Session, device_id: int) -> Device:
    """
    Retrieve a single device by ID.

    Args:
        db: Database session.
        device_id: The ID of the device to retrieve.

    Returns:
        The Device instance.

    Raises:
        HTTPException 404: If the device is not found.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found"
        )
    return device


def create_device(db: Session, device_data: DeviceCreate) -> Device:
    """
    Create a new device.

    Args:
        db: Database session.
        device_data: Validated device creation data.

    Returns:
        The newly created Device instance.

    Raises:
        HTTPException 400: If serial number already exists.
    """
    # Check for duplicate serial number
    if device_data.serial_number:
        existing = db.query(Device).filter(
            Device.serial_number == device_data.serial_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Device with serial number '{device_data.serial_number}' already exists"
            )

    new_device = Device(
        name=device_data.name,
        brand=device_data.brand,
        model=device_data.model,
        serial_number=device_data.serial_number,
        status=device_data.status
    )

    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device


def update_device(db: Session, device_id: int, device_data: DeviceUpdate) -> Device:
    """
    Update an existing device.

    Args:
        db: Database session.
        device_id: The ID of the device to update.
        device_data: Validated update data (partial).

    Returns:
        The updated Device instance.

    Raises:
        HTTPException 404: If the device is not found.
        HTTPException 400: If updated serial number already exists.
    """
    device = get_device(db, device_id)

    # Check for duplicate serial number if updating
    if device_data.serial_number and device_data.serial_number != device.serial_number:
        existing = db.query(Device).filter(
            Device.serial_number == device_data.serial_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Device with serial number '{device_data.serial_number}' already exists"
            )

    # Update only provided fields
    update_data = device_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)

    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device_id: int) -> dict:
    """
    Delete a device by ID.

    Args:
        db: Database session.
        device_id: The ID of the device to delete.

    Returns:
        Confirmation message dictionary.

    Raises:
        HTTPException 404: If the device is not found.
    """
    device = get_device(db, device_id)
    db.delete(device)
    db.commit()
    return {"message": f"Device with id {device_id} deleted successfully"}
