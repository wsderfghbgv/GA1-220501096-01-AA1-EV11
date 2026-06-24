"""
User service for device_systems.
Handles user-related business logic and database operations.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user_model import User


def get_users(db: Session) -> list[User]:
    """
    Retrieve all users from the database.

    Args:
        db: Database session.

    Returns:
        List of all User instances.
    """
    return db.query(User).all()


def get_user(db: Session, user_id: int) -> User:
    """
    Retrieve a single user by ID.

    Args:
        db: Database session.
        user_id: The ID of the user to retrieve.

    Returns:
        The User instance.

    Raises:
        HTTPException 404: If the user is not found.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user
