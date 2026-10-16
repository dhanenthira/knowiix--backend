from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.question import QuestionResponse
from app.core.database import get_db
from app.models.sql_models import QuestionModel

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.get("", response_model=List[QuestionResponse])
def get_questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    topic: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    query = db.query(QuestionModel)
    if category:
        query = query.filter(QuestionModel.category == category)
    if difficulty:
        query = query.filter(QuestionModel.difficulty == difficulty)
    if topic:
        query = query.filter(QuestionModel.topic == topic)

    questions = query.limit(limit).all()
    return [QuestionResponse.model_validate(q, from_attributes=True) for q in questions]

import uuid
from datetime import datetime
from app.schemas.question import QuestionCreate

@router.post("", response_model=QuestionResponse)
def create_question_direct(
    q_in: QuestionCreate,
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    q_id = f"q_{uuid.uuid4().hex[:8]}"
    new_q = QuestionModel(
        id=q_id,
        title=q_in.title,
        content=q_in.content,
        category=q_in.category.value if hasattr(q_in.category, "value") else str(q_in.category).lower(),
        topic=q_in.topic,
        difficulty=q_in.difficulty.value if hasattr(q_in.difficulty, "value") else str(q_in.difficulty).lower(),
        question_type=q_in.question_type.value if hasattr(q_in.question_type, "value") else str(q_in.question_type),
        options=q_in.options,
        correct_answer=q_in.correct_answer,
        explanation=q_in.explanation or "",
        marks=q_in.marks,
        tags=q_in.tags or [],
        created_at=datetime.utcnow()
    )
    db.add(new_q)
    db.commit()
    db.refresh(new_q)
    return QuestionResponse.model_validate(new_q, from_attributes=True)

@router.delete("/{question_id}")
def delete_question_direct(
    question_id: str,
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    q = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()
    return {"status": "success", "message": f"Question {question_id} deleted successfully"}

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    apt_count = 0
    tech_count = 0
    code_count = 0
    mixed_count = 0

    if db:
        apt_count = db.query(QuestionModel).filter(QuestionModel.category == "aptitude").count()
        tech_count = db.query(QuestionModel).filter(QuestionModel.category == "technical").count()
        code_count = db.query(QuestionModel).filter(QuestionModel.category == "coding").count()
        mixed_count = db.query(QuestionModel).filter(QuestionModel.category == "mixed").count()

    return [
        {"id": "aptitude", "name": "Quantitative & Logical Aptitude", "count": apt_count, "icon": "brain"},
        {"id": "technical", "name": "Computer Science & Engineering", "count": tech_count, "icon": "cpu"},
        {"id": "coding", "name": "Data Structures & Algorithms", "count": code_count, "icon": "code-2"},
        {"id": "mixed", "name": "Grand Challenge Mix", "count": mixed_count, "icon": "sparkles"}
    ]

from pydantic import BaseModel
from app.models.sql_models import QuestionSolvedModel, UserModel
from app.api.auth import get_current_user
from app.core.security import oauth2_scheme
from app.schemas.user import UserResponse

def get_optional_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[UserModel]:
    if not token or not db:
        return db.query(UserModel).filter(UserModel.role == "student").first() if db else None
    try:
        cur = get_current_user(token=token, db=db)
        if cur:
            u = db.query(UserModel).filter(UserModel.id == cur.id).first()
            if u:
                return u
    except Exception:
        pass
    return db.query(UserModel).filter(UserModel.role == "student").first() if db else None

class QuestionSolveRequest(BaseModel):
    question_id: str
    selected_answer: Optional[str] = None
    category: Optional[str] = "aptitude"

class BatchSolveRequest(BaseModel):
    question_ids: List[str]
    category: Optional[str] = "aptitude"

@router.get("/aptitude/progress")
def get_aptitude_progress(
    user: Optional[UserModel] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Returns the real-time aptitude progress for the authenticated user:
    - total_problems: total aptitude questions in database
    - problems_solved: number of unique aptitude questions solved by user
    - problems_remaining: remaining problems
    - progress_percentage: percentage completed
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    total_problems = db.query(QuestionModel).filter(QuestionModel.category.ilike("%aptitude%")).count()
    if total_problems == 0:
        total_problems = 100

    user_id = user.id if user else "user_student_01"
    solved_records = db.query(QuestionSolvedModel.question_id).filter(
        QuestionSolvedModel.user_id == user_id,
        QuestionSolvedModel.category.ilike("%aptitude%")
    ).all()

    solved_ids = [r[0] for r in solved_records]
    problems_solved = len(solved_ids)
    problems_remaining = max(0, total_problems - problems_solved)
    progress_percentage = round((problems_solved / total_problems) * 100, 1) if total_problems > 0 else 0.0

    return {
        "user_id": user_id,
        "total_problems": total_problems,
        "problems_solved": problems_solved,
        "problems_remaining": problems_remaining,
        "progress_percentage": progress_percentage,
        "solved_question_ids": solved_ids
    }

@router.post("/aptitude/solve")
def solve_aptitude_problem(
    req: QuestionSolveRequest,
    user: Optional[UserModel] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Tracks that a user has solved an aptitude question.
    Saves in the database (QuestionSolvedModel) so it persists across logins.
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    if not user:
        user = db.query(UserModel).filter(UserModel.role == "student").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already solved
    existing = db.query(QuestionSolvedModel).filter(
        QuestionSolvedModel.user_id == user.id,
        QuestionSolvedModel.question_id == req.question_id
    ).first()

    already_solved = False
    if not existing:
        new_solve = QuestionSolvedModel(
            user_id=user.id,
            question_id=req.question_id,
            category=req.category or "aptitude",
            first_solved_at=datetime.utcnow()
        )
        db.add(new_solve)
        if user.questions_solved is not None:
            user.questions_solved += 1
        else:
            user.questions_solved = 1
        if user.total_points is not None:
            user.total_points += 10
        db.commit()
    else:
        already_solved = True

    total_problems = db.query(QuestionModel).filter(QuestionModel.category.ilike("%aptitude%")).count() or 100
    problems_solved = db.query(QuestionSolvedModel).filter(
        QuestionSolvedModel.user_id == user.id,
        QuestionSolvedModel.category.ilike("%aptitude%")
    ).count()
    problems_remaining = max(0, total_problems - problems_solved)
    progress_percentage = round((problems_solved / total_problems) * 100, 1) if total_problems > 0 else 0.0

    return {
        "success": True,
        "already_solved": already_solved,
        "message": "Problem already solved previously" if already_solved else "Problem solved and recorded successfully",
        "total_problems": total_problems,
        "problems_solved": problems_solved,
        "problems_remaining": problems_remaining,
        "progress_percentage": progress_percentage
    }

@router.post("/{question_id}/solve")
def solve_question_by_id(
    question_id: str,
    user: Optional[UserModel] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    req = QuestionSolveRequest(question_id=question_id, category="aptitude")
    return solve_aptitude_problem(req, user=user, db=db)

@router.post("/aptitude/batch-solve")
def batch_solve_aptitude(
    req: BatchSolveRequest,
    user: Optional[UserModel] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Batch records solved aptitude questions (e.g. at the completion of a quiz/test).
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    if not user:
        user = db.query(UserModel).filter(UserModel.role == "student").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    newly_solved_count = 0
    for q_id in req.question_ids:
        existing = db.query(QuestionSolvedModel).filter(
            QuestionSolvedModel.user_id == user.id,
            QuestionSolvedModel.question_id == q_id
        ).first()
        if not existing:
            db.add(QuestionSolvedModel(
                user_id=user.id,
                question_id=q_id,
                category=req.category or "aptitude",
                first_solved_at=datetime.utcnow()
            ))
            newly_solved_count += 1

    if newly_solved_count > 0:
        if user.questions_solved is not None:
            user.questions_solved += newly_solved_count
        else:
            user.questions_solved = newly_solved_count
        if user.total_points is not None:
            user.total_points += newly_solved_count * 10
        db.commit()

    total_problems = db.query(QuestionModel).filter(QuestionModel.category.ilike("%aptitude%")).count() or 100
    problems_solved = db.query(QuestionSolvedModel).filter(
        QuestionSolvedModel.user_id == user.id,
        QuestionSolvedModel.category.ilike("%aptitude%")
    ).count()
    problems_remaining = max(0, total_problems - problems_solved)
    progress_percentage = round((problems_solved / total_problems) * 100, 1) if total_problems > 0 else 0.0

    return {
        "success": True,
        "newly_solved_count": newly_solved_count,
        "total_problems": total_problems,
        "problems_solved": problems_solved,
        "problems_remaining": problems_remaining,
        "progress_percentage": progress_percentage
    }
