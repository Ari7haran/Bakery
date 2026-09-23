"""
Backward compatibility facade for database session.
Re-exports from app.core.database to ensure existing references continue to work seamlessly.
"""
from app.core.database import engine, SessionLocal, Base, get_db

__all__ = ["engine", "SessionLocal", "Base", "get_db"]
