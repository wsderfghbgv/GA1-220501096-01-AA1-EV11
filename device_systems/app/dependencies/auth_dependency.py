"""
Authentication dependency for device_systems.
Provides route protection through OAuth2 bearer token validation.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.auth.security import decode_access_token
from app.models.user_model import User

# OAuth2 scheme pointing to the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from the JWT token.

    Args:
        token: JWT bearer token from the Authorization header.
        db: Database session.

    Returns:
        The authenticated User instance.

    Raises:
        HTTPException 401: If the token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is active.

    Args:
        current_user: The authenticated user.

    Returns:
        The active User instance.

    Raises:
        HTTPException 403: If the user account is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user


def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to restrict access to admin users only.

    Args:
        current_user: The authenticated and active user.

    Returns:
        The admin User instance.

    Raises:
        HTTPException 403: If the user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: admin role required"
        )
    return current_user


def require_admin_or_support(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to restrict access to admin or support users.

    Args:
        current_user: The authenticated and active user.

    Returns:
        The User instance with admin or support role.

    Raises:
        HTTPException 403: If the user is not admin or support.
    """
    if current_user.role not in ("admin", "support"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: admin or support role required"
        )
    return current_user
