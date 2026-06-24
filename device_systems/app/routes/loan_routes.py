"""
Loan routes for device_systems.
Endpoints for loan management with role-based protection.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.dependencies.database_dependency import get_db
from app.dependencies.auth_dependency import (
    get_current_active_user,
    require_admin_or_support
)
from app.services.loan_service import create_loan, return_loan, get_loan_details, get_loans
from app.schemas.loan_schema import LoanCreate, LoanResponse, LoanDetailResponse
from app.models.user_model import User

router = APIRouter(prefix="/loans", tags=["Loans"])

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/",
    response_model=list[LoanResponse],
    summary="Get all loans",
    description="Retrieve a list of all loans. Requires authentication.",
    responses={
        401: {"description": "Not authenticated"}
    }
)
def read_loans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all loans. Requires authenticated user."""
    return get_loans(db)


@router.get(
    "/details",
    response_model=list[LoanDetailResponse],
    summary="Get all loans with details",
    description="Retrieve all loans with user and device details using join queries. "
                "Requires admin or support role.",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions (admin or support required)"}
    }
)
def read_loan_details(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_support)
):
    """Get all loans with user and device details. Requires admin or support role."""
    return get_loan_details(db)


@router.post(
    "/",
    response_model=LoanResponse,
    status_code=201,
    summary="Create a new loan",
    description="Create a new device loan for a user. The device must be available. "
                "Requires authentication.",
    responses={
        400: {"description": "Device not available"},
        401: {"description": "Not authenticated"},
        404: {"description": "User or device not found"},
        429: {"description": "Too many requests"}
    }
)
@limiter.limit("10/minute")
def create_new_loan(
    request: Request,
    loan_data: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new loan. Requires authenticated user."""
    return create_loan(db, loan_data)


@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse,
    summary="Return a loaned device",
    description="Mark a loan as returned and make the device available again. "
                "Requires admin or support role.",
    responses={
        400: {"description": "Loan already returned"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions (admin or support required)"},
        404: {"description": "Loan not found"}
    }
)
def return_loaned_device(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_support)
):
    """Return a loaned device. Requires admin or support role."""
    return return_loan(db, loan_id)
