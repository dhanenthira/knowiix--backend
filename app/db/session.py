"""
Database session and engine helpers for Knowiix Learning Dashboard.
Reuses existing MySQL engine and session from app.core.database.
"""
from app.core.database import Base, engine, SessionLocal, get_db

__all__ = ["Base", "engine", "SessionLocal", "get_db"]
