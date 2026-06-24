"""
Database dependency for FastAPI route injection.
Provides a database session per request with automatic cleanup.
"""

from app.database.connection import SessionLocal


def get_db():
    """
    Dependency that provides a SQLAlchemy database session.
    Yields a session and ensures it is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
