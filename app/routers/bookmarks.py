from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.user import UserResponse
from app.schemas.bookmark import BookmarkResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])

@router.get("", response_model=List[BookmarkResponse])
@router.get("/", response_model=List[BookmarkResponse])
def get_user_bookmarks(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns bookmarks belonging strictly to the authenticated user.
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")
    return DashboardService.get_bookmarks(user_id=current_user.id, db=db)

@router.post("/{tutorial_id}")
def add_tutorial_bookmark(
    tutorial_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Saves a tutorial to user's bookmarks.
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")
    return DashboardService.add_bookmark(user_id=current_user.id, tutorial_id=tutorial_id, db=db)

@router.delete("/{tutorial_id}")
def delete_tutorial_bookmark(
    tutorial_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Removes a tutorial from user's bookmarks.
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")
    return DashboardService.remove_bookmark(user_id=current_user.id, tutorial_id=tutorial_id, db=db)
