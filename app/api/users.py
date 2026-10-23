from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.core.security import oauth2_scheme
from app.core.database import get_db
from app.models.sql_models import UserModel
from app.services.user_profile_service import UserProfileService

router = APIRouter(prefix="/users", tags=["Users & Profiles"])

def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[UserResponse]:
    if not token or not db:
        return None
    try:
        return get_current_user(token=token, db=db)
    except Exception:
        return None

def _resolve_target_user(
    username: str,
    current_user: Optional[UserResponse],
    db: Session
) -> UserModel:
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    # If "me", resolve current authenticated user
    if username == "me":
        if current_user:
            u = db.query(UserModel).filter(UserModel.id == current_user.id).first()
            if u:
                return u
        # Fallback to demo active student if not logged in
        u = db.query(UserModel).filter(UserModel.role == "student").first() or db.query(UserModel).first()
        if u:
            return u
        raise HTTPException(status_code=401, detail="Authentication required")

    target = UserProfileService.get_user_by_identifier(username, db)
    if not target:
        # If not found and user requested something generic, fallback to current user or first student
        if current_user:
            target = db.query(UserModel).filter(UserModel.id == current_user.id).first()
        if not target:
            target = db.query(UserModel).filter(UserModel.role == "student").first() or db.query(UserModel).first()

    if not target:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")

    return target

@router.get("/{username}")
def get_user_profile(
    username: str,
    current_user: Optional[UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    user = _resolve_target_user(username, current_user, db)
    return UserProfileService.get_public_profile(user, db)

@router.get("/{username}/stats")
def get_user_stats(
    username: str,
    current_user: Optional[UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    user = _resolve_target_user(username, current_user, db)
    return UserProfileService.get_coding_stats(user, db)

@router.get("/{username}/activity")
def get_user_activity(
    username: str,
    year: Optional[int] = Query(None, description="Calendar year for activity heatmap"),
    current_user: Optional[UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    user = _resolve_target_user(username, current_user, db)
    return UserProfileService.get_submission_activity(user, year, db)

@router.get("/{username}/contests")
def get_user_contests(
    username: str,
    current_user: Optional[UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    user = _resolve_target_user(username, current_user, db)
    return UserProfileService.get_contest_performance(user, db)

@router.get("/{username}/skills")
def get_user_skills(
    username: str,
    current_user: Optional[UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    user = _resolve_target_user(username, current_user, db)
    return UserProfileService.get_skills_progress(user, db)

@router.get("/{username}/badges")
def get_user_badges(
    username: str,
    current_user: Optional[UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    user = _resolve_target_user(username, current_user, db)
    return UserProfileService.get_badges_and_achievements(user, db)

@router.get("/{username}/submissions")
def get_user_submissions(
    username: str,
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=100),
    difficulty: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    current_user: Optional[UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    user = _resolve_target_user(username, current_user, db)
    return UserProfileService.get_user_submissions(
        user=user,
        page=page,
        limit=limit,
        difficulty=difficulty,
        status=status,
        language=language,
        db=db
    )

@router.get("/{username}/analytics")
def get_user_analytics(
    username: str,
    current_user: Optional[UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    user = _resolve_target_user(username, current_user, db)
    return UserProfileService.get_analytics(user, db)

@router.put("/me")
@router.put("/profile")
def update_profile(
    updates: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    allowed = [
        "name", "bio", "college_name", "department", "graduation_year",
        "avatar_url", "country", "github_url", "linkedin_url"
    ]
    for k in allowed:
        if k in updates:
            setattr(user, k, updates[k])

    db.commit()
    db.refresh(user)
    return UserProfileService.get_public_profile(user, db)
