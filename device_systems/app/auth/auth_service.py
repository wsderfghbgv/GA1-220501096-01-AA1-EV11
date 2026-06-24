"""
Authentication service for device_systems.
Handles user registration and authentication logic.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user_model import User
from app.schemas.auth_schema import UserRegister
from app.auth.security import get_password_hash, verify_password


def register_user(db: Session, user_data: UserRegister) -> User:
    """
    Register a new user with hashed password.

    Args:
        db: Database session.
        user_data: Validated registration data.

    Returns:
        The newly created User instance.

    Raises:
        HTTPException: If email already exists.
    """
    # Check if email is already registered
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )

    # Create user with hashed password
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user by email and password.

    Args:
        db: Database session.
        email: User's email address.
        password: Plain text password to verify.

    Returns:
        The User instance if authentication succeeds, None otherwise.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
