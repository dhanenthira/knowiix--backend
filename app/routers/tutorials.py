from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.user import UserResponse
from app.schemas.tutorial import TutorialResponse, TopicResponse
from app.models.tutorial import TutorialModel
from app.models.topic import TopicModel
from app.models.bookmark import BookmarkModel
from app.models.progress import UserProgressModel
from app.models.category import CategoryModel
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/tutorials", tags=["Tutorials"])

@router.get("/recommended", response_model=List[TutorialResponse])
def get_recommended_tutorials(
    limit: int = Query(6, ge=1, le=20),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns recommended tutorials for the current user based on learning level and active categories.
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")
    return DashboardService.get_recommended_tutorials(user_id=current_user.id, db=db, limit=limit)

@router.get("", response_model=List[TutorialResponse])
@router.get("/", response_model=List[TutorialResponse])
def get_all_tutorials(
    category_slug: Optional[str] = None,
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    current_user: Optional[UserResponse] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns published tutorials, optionally filtered by category or search keyword.
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")

    query = db.query(TutorialModel).filter(TutorialModel.is_published == True)

    if category_slug:
        query = query.join(CategoryModel, TutorialModel.category_id == CategoryModel.id).filter(
            CategoryModel.slug == category_slug
        )
    elif category_id:
        query = query.filter(TutorialModel.category_id == category_id)

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (TutorialModel.title.ilike(s)) | (TutorialModel.description.ilike(s))
        )

    tutorials = query.order_by(TutorialModel.created_at.asc()).all()

    results = []
    user_id = current_user.id if current_user else None

    for tut in tutorials:
        total_topics = db.query(func.count(TopicModel.id)).filter(
            TopicModel.tutorial_id == tut.id
        ).scalar() or 0

        completed_topics = 0
        is_bm = False
        if user_id:
            completed_topics = db.query(func.count(TopicModel.id)).join(
                UserProgressModel, TopicModel.id == UserProgressModel.topic_id
            ).filter(
                TopicModel.tutorial_id == tut.id,
                UserProgressModel.user_id == user_id,
                UserProgressModel.is_completed == True
            ).scalar() or 0

            is_bm = db.query(BookmarkModel).filter(
                BookmarkModel.user_id == user_id,
                BookmarkModel.tutorial_id == tut.id
            ).first() is not None

        progress_pct = round((completed_topics / total_topics * 100.0), 1) if total_topics > 0 else 0.0
        category = tut.category

        results.append(TutorialResponse(
            id=tut.id,
            category_id=tut.category_id,
            title=tut.title,
            slug=tut.slug,
            description=tut.description or "",
            difficulty=tut.difficulty,
            estimated_minutes=tut.estimated_minutes,
            is_published=tut.is_published,
            created_at=tut.created_at,
            category_name=category.name if category else "General",
            category_slug=category.slug if category else "general",
            category_icon=category.icon if category else "code",
            total_topics=total_topics,
            completed_topics=completed_topics,
            progress_percentage=progress_pct,
            is_bookmarked=is_bm
        ))

    return results

@router.get("/{tutorial_id}", response_model=TutorialResponse)
def get_tutorial_detail(
    tutorial_id: str,
    current_user: Optional[UserResponse] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns full details for a single tutorial, including its topics.
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")

    tut = db.query(TutorialModel).filter(
        (TutorialModel.id == tutorial_id) | (TutorialModel.slug == tutorial_id)
    ).first()

    if not tut or not tut.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutorial not found")

    user_id = current_user.id if current_user else None

    # Retrieve topics
    topics_db = db.query(TopicModel).filter(
        TopicModel.tutorial_id == tut.id
    ).order_by(TopicModel.display_order.asc()).all()

    completed_topic_ids = set()
    is_bm = False
    if user_id:
        completed_records = db.query(UserProgressModel.topic_id).filter(
            UserProgressModel.user_id == user_id,
            UserProgressModel.is_completed == True
        ).all()
        completed_topic_ids = {r[0] for r in completed_records}

        is_bm = db.query(BookmarkModel).filter(
            BookmarkModel.user_id == user_id,
            BookmarkModel.tutorial_id == tut.id
        ).first() is not None

    topic_responses = []
    for top in topics_db:
        topic_responses.append(TopicResponse(
            id=top.id,
            tutorial_id=top.tutorial_id,
            title=top.title,
            content=top.content,
            code_example=top.code_example or "",
            display_order=top.display_order,
            is_completed=(top.id in completed_topic_ids)
        ))

    total_topics = len(topic_responses)
    completed_topics = sum(1 for t in topic_responses if t.is_completed)
    progress_pct = round((completed_topics / total_topics * 100.0), 1) if total_topics > 0 else 0.0
    category = tut.category

    return TutorialResponse(
        id=tut.id,
        category_id=tut.category_id,
        title=tut.title,
        slug=tut.slug,
        description=tut.description or "",
        difficulty=tut.difficulty,
        estimated_minutes=tut.estimated_minutes,
        is_published=tut.is_published,
        created_at=tut.created_at,
        category_name=category.name if category else "General",
        category_slug=category.slug if category else "general",
        category_icon=category.icon if category else "code",
        total_topics=total_topics,
        completed_topics=completed_topics,
        progress_percentage=progress_pct,
        is_bookmarked=is_bm,
        topics=topic_responses
    )

@router.get("/{tutorial_id}/topics", response_model=List[TopicResponse])
def get_tutorial_topics(
    tutorial_id: str,
    current_user: Optional[UserResponse] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns topics for a specific tutorial with completion flags for current user.
    """
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")

    tut = db.query(TutorialModel).filter(
        (TutorialModel.id == tutorial_id) | (TutorialModel.slug == tutorial_id)
    ).first()

    if not tut:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutorial not found")

    topics = db.query(TopicModel).filter(
        TopicModel.tutorial_id == tut.id
    ).order_by(TopicModel.display_order.asc()).all()

    completed_topic_ids = set()
    if current_user:
        completed_records = db.query(UserProgressModel.topic_id).filter(
            UserProgressModel.user_id == current_user.id,
            UserProgressModel.is_completed == True
        ).all()
        completed_topic_ids = {r[0] for r in completed_records}

    return [
        TopicResponse(
            id=top.id,
            tutorial_id=top.tutorial_id,
            title=top.title,
            content=top.content,
            code_example=top.code_example or "",
            display_order=top.display_order,
            is_completed=(top.id in completed_topic_ids)
        )
        for top in topics
    ]
