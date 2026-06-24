"""
Loan model for device_systems.
Represents the relationship between users and devices through loans.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class Loan(Base):
    """
    Loan model representing device loans to users.

    Attributes:
        id: Primary key auto-incremented.
        user_id: Foreign key referencing the user who borrowed the device.
        device_id: Foreign key referencing the borrowed device.
        loan_date: Timestamp when the loan was created.
        return_date: Timestamp when the device was returned (nullable).
        status: Current status of the loan (active, returned).
        user: Relationship to User model.
        device: Relationship to Device model.
    """
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    loan_date = Column(DateTime(timezone=True), server_default=func.now())
    return_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="active")

    # Relationships
    user = relationship("User", back_populates="loans")
    device = relationship("Device", back_populates="loans")

    def __repr__(self):
        return f"<Loan(id={self.id}, user_id={self.user_id}, device_id={self.device_id}, status='{self.status}')>"
