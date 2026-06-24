"""
Loan service for device_systems.
Handles loan-related business logic including creation, return, and detail queries with joins.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.loan_model import Loan
from app.models.user_model import User
from app.models.device_model import Device
from app.schemas.loan_schema import LoanCreate


def create_loan(db: Session, loan_data: LoanCreate) -> Loan:
    """
    Create a new device loan.

    Args:
        db: Database session.
        loan_data: Validated loan creation data.

    Returns:
        The newly created Loan instance.

    Raises:
        HTTPException 404: If user or device not found.
        HTTPException 400: If device is not available for loan.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == loan_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {loan_data.user_id} not found"
        )

    # Verify device exists
    device = db.query(Device).filter(Device.id == loan_data.device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {loan_data.device_id} not found"
        )

    # Check device availability
    if device.status != "available":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device '{device.name}' is not available (current status: {device.status})"
        )

    # Create the loan
    new_loan = Loan(
        user_id=loan_data.user_id,
        device_id=loan_data.device_id,
        status="active"
    )

    # Update device status to loaned
    device.status = "loaned"

    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return new_loan


def return_loan(db: Session, loan_id: int) -> Loan:
    """
    Mark a loan as returned.

    Args:
        db: Database session.
        loan_id: The ID of the loan to return.

    Returns:
        The updated Loan instance.

    Raises:
        HTTPException 404: If the loan is not found.
        HTTPException 400: If the loan is already returned.
    """
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Loan with id {loan_id} not found"
        )

    if loan.status == "returned":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This loan has already been returned"
        )

    # Update loan
    loan.status = "returned"
    loan.return_date = datetime.now(timezone.utc)

    # Update device status back to available
    device = db.query(Device).filter(Device.id == loan.device_id).first()
    if device:
        device.status = "available"

    db.commit()
    db.refresh(loan)
    return loan


def get_loan_details(db: Session) -> list[dict]:
    """
    Retrieve all loans with user and device details using joins.

    Args:
        db: Database session.

    Returns:
        List of dictionaries with loan, user, and device information.
    """
    results = (
        db.query(Loan, User, Device)
        .join(User, Loan.user_id == User.id)
        .join(Device, Loan.device_id == Device.id)
        .all()
    )

    loan_details = []
    for loan, user, device in results:
        loan_details.append({
            "id": loan.id,
            "loan_date": loan.loan_date,
            "return_date": loan.return_date,
            "status": loan.status,
            "user_name": user.name,
            "user_email": user.email,
            "device_name": device.name,
            "device_brand": device.brand,
            "device_serial": device.serial_number
        })

    return loan_details


def get_loans(db: Session) -> list[Loan]:
    """
    Retrieve all loans.

    Args:
        db: Database session.

    Returns:
        List of all Loan instances.
    """
    return db.query(Loan).all()
