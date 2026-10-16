from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.user import UserResponse
from app.schemas.progress import UserProgressSummary, LearningActivityResponse
from app.schemas.tutorial import TopicResponse
from app.models.topic import TopicModel
from app.models.progress import UserProgressModel
from app.services.dashboard_service import DashboardService

router = APIRouter(tags=["Learning Progress"])

@router.get("/progress/me", response_model=UserProgressSummary)
def get_my_learning_progress(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the authenticated user's overall progress, completed topics, and in-progress topics.
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")
    return DashboardService.get_user_progress(user_id=current_user.id, db=db)

@router.post("/topics/{topic_id}/complete")
def complete_topic(
    topic_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marks a topic as completed for the authenticated user, updates completion timestamp,
    awards learning points, and records activity.
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")
    return DashboardService.complete_topic(user_id=current_user.id, topic_id=topic_id, db=db)

@router.get("/progress/recent", response_model=List[LearningActivityResponse])
def get_recent_learning_activity(
    limit: int = Query(15, ge=1, le=50),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns recent learning activities belonging strictly to the authenticated user.
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")
    return DashboardService.get_recent_activity(user_id=current_user.id, db=db, limit=limit)

@router.get("/topics/{topic_id}", response_model=TopicResponse)
def get_topic_detail(
    topic_id: str,
    current_user: Optional[UserResponse] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves full details for a single topic and records topic viewing activity.
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")

    topic = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    is_done = False
    if current_user:
        DashboardService.record_topic_access(user_id=current_user.id, topic_id=topic_id, db=db)
        prog = db.query(UserProgressModel).filter(
            UserProgressModel.user_id == current_user.id,
            UserProgressModel.topic_id == topic_id
        ).first()
        if prog:
            is_done = prog.is_completed

    return TopicResponse(
        id=topic.id,
        tutorial_id=topic.tutorial_id,
        title=topic.title,
        content=topic.content,
        code_example=topic.code_example or "",
        display_order=topic.display_order,
        is_completed=is_done
    )
