"""
User routes for device_systems.
Protected endpoints for user management.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.dependencies.database_dependency import get_db
from app.dependencies.auth_dependency import get_current_active_user
from app.services.user_service import get_users, get_user
from app.schemas.user_schema import UserResponse
from app.models.user_model import User

router = APIRouter(prefix="/users", tags=["Users"])

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Get all users",
    description="Retrieve a list of all registered users. Requires authentication.",
    responses={
        401: {"description": "Not authenticated"},
        429: {"description": "Too many requests"}
    }
)
@limiter.limit("30/minute")
def read_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all users. Requires authenticated user."""
    return get_users(db)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve a specific user by their ID. Requires authentication.",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "User not found"}
    }
)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific user by ID. Requires authenticated user."""
    return get_user(db, user_id)
