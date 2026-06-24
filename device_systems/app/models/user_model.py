"""
User model for device_systems.
Supports authentication with hashed passwords and role-based authorization.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class User(Base):
    """
    User model representing system users.

    Attributes:
        id: Primary key auto-incremented.
        name: Full name of the user.
        email: Unique email address used for authentication.
        hashed_password: Bcrypt hash of the user's password (never exposed in responses).
        role: User role for authorization (admin, support, user).
        is_active: Whether the user account is active.
        created_at: Timestamp of account creation.
        loans: Relationship to Loan model.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with loans
    loans = relationship("Loan", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}', role='{self.role}')>"
