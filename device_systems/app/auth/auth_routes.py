"""
Authentication routes for device_systems.
Handles user registration, login, and profile retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.dependencies.database_dependency import get_db
from app.dependencies.auth_dependency import get_current_active_user
from app.auth.auth_service import register_user, authenticate_user
from app.auth.security import create_access_token
from app.schemas.auth_schema import UserRegister, UserLogin, Token
from app.schemas.user_schema import UserResponse
from app.models.user_model import User

router = APIRouter(prefix="/auth", tags=["Auth"])

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with a secure password. "
                "The password must meet strength requirements: min 8 chars, "
                "1 uppercase, 1 lowercase, 1 digit, no spaces.",
    responses={
        400: {"description": "Email already registered"},
        422: {"description": "Validation error (weak password, invalid email, etc.)"},
        429: {"description": "Too many requests"}
    }
)
@limiter.limit("3/minute")
def register(
    request: Request,
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user with validated and hashed password."""
    new_user = register_user(db, user_data)
    return new_user


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user and get JWT token",
    description="Authenticate with email and password to receive a JWT access token.",
    responses={
        401: {"description": "Invalid credentials"},
        429: {"description": "Too many requests"}
    }
)
@limiter.limit("5/minute")
def login(
    request: Request,
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create JWT token with user email as subject
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Retrieve the profile of the currently authenticated user. "
                "Requires a valid JWT token in the Authorization header.",
    responses={
        401: {"description": "Not authenticated or invalid token"}
    }
)
def get_me(current_user: User = Depends(get_current_active_user)):
    """Return the current authenticated user's data (without hashed_password)."""
    return current_user
