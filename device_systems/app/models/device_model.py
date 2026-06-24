"""
Device model for device_systems.
Represents technological devices available for loan.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class Device(Base):
    """
    Device model representing technological devices in the system.

    Attributes:
        id: Primary key auto-incremented.
        name: Name or description of the device.
        brand: Brand/manufacturer of the device.
        model: Specific model identifier.
        serial_number: Unique serial number.
        status: Current status (available, loaned, maintenance).
        created_at: Timestamp of device registration.
        loans: Relationship to Loan model.
    """
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=True)
    serial_number = Column(String(100), unique=True, nullable=True)
    status = Column(String(20), nullable=False, default="available")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with loans
    loans = relationship("Loan", back_populates="device")

    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.name}', brand='{self.brand}', status='{self.status}')>"
