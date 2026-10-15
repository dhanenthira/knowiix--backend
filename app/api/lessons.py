from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.schemas.lesson import ModuleSummary, LessonDetail, LessonProgressUpdate
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.sql_models import LearningModuleModel, LessonModel, UserModel

router = APIRouter(prefix="/lessons", tags=["Learning Module"])

@router.get("/modules", response_model=List[ModuleSummary])
def get_all_modules(db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    modules = db.query(LearningModuleModel).all()
    return [ModuleSummary.model_validate(m, from_attributes=True) for m in modules]

@router.get("/module/{module_id}/lessons", response_model=List[LessonDetail])
def get_module_lessons(module_id: str, db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    lessons = db.query(LessonModel).filter(
        (LessonModel.module_id == module_id) | (LessonModel.category == module_id)
    ).order_by(LessonModel.order).all()
    return [LessonDetail.model_validate(l, from_attributes=True) for l in lessons]

@router.get("/{lesson_id}", response_model=LessonDetail)
def get_lesson_detail(lesson_id: str, db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    lesson = db.query(LessonModel).filter(LessonModel.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return LessonDetail.model_validate(lesson, from_attributes=True)

@router.post("/{lesson_id}/add-note")
def add_lesson_note(lesson_id: str, note_data: dict, db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    lesson = db.query(LessonModel).filter(LessonModel.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    note_text = note_data.get("note", "").strip()
    if not note_text:
        raise HTTPException(status_code=400, detail="Note content cannot be empty")
    
    current_notes = list(lesson.notes or [])
    current_notes.append(note_text)
    lesson.notes = current_notes
    db.commit()
    db.refresh(lesson)
    return {"status": "success", "lesson_id": lesson_id, "notes": lesson.notes}

@router.post("/progress")
def update_lesson_progress(
    progress: LessonProgressUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    lesson = db.query(LessonModel).filter(LessonModel.id == progress.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
        
    lesson.is_completed = progress.completed
    
    # Update user points in MySQL if newly completed
    if progress.completed:
        user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
        if user:
            user.total_points = (user.total_points or 0) + 15
            
    db.commit()
    return {"status": "success", "lesson_id": progress.lesson_id, "is_completed": progress.completed}

