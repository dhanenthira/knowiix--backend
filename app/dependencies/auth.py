"""
Authentication dependencies for the Learning Dashboard.
Reuses existing security and user verification logic.
"""
from fastapi import Depends
from app.api.auth import get_current_user, get_current_admin_user
from app.schemas.user import UserResponse

__all__ = ["get_current_user", "get_current_admin_user", "UserResponse"]
