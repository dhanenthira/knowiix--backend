from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.user import UserResponse
from app.schemas.dashboard import DashboardSummaryResponse
from app.schemas.tutorial import ContinueLearningItem
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Learning Dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns high-level learning dashboard metrics for the authenticated user:
    - Available Courses
    - Courses Started
    - Completed Lessons
    - Saved Tutorials
    - Overall Progress Percentage
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")
    return DashboardService.get_dashboard_summary(user_id=current_user.id, db=db)

@router.get("/continue-learning", response_model=List[ContinueLearningItem])
def get_continue_learning(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns recently accessed tutorials for resuming study.
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")
    return DashboardService.get_continue_learning(user_id=current_user.id, db=db)
