from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Import API routers
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.students import router as students_router
from app.api.questions import router as questions_router
from app.api.lessons import router as lessons_router
from app.api.practice import router as practice_router
from app.api.coding import router as coding_router
from app.api.tests import router as tests_router
from app.api.friends import router as friends_router
from app.api.battle_rooms import router as battle_router
from app.api.leaderboard import router as leaderboard_router
from app.api.reports import router as reports_router
from app.api.notifications import router as notifications_router
from app.routers.dashboard import router as dashboard_router
from app.routers.categories import router as categories_router
from app.routers.tutorials import router as tutorials_router
from app.routers.bookmarks import router as bookmarks_router
from app.routers.progress import router as progress_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for CodeArena – Learn, Practice & Compete platform"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.core.database import check_mysql_connection
from app.core.init_db import init_tables

@app.on_event("startup")
def on_startup():
    # Initialize MySQL tables on server start
    init_tables()

# Include Routers under /api/v1 and alias under /api
for pfx in [settings.API_V1_STR, "/api"]:
    app.include_router(auth_router, prefix=pfx)
    app.include_router(admin_router, prefix=pfx)
    app.include_router(students_router, prefix=pfx)
    app.include_router(questions_router, prefix=pfx)
    app.include_router(lessons_router, prefix=pfx)
    app.include_router(practice_router, prefix=pfx)
    app.include_router(coding_router, prefix=pfx)
    app.include_router(tests_router, prefix=pfx)
    app.include_router(friends_router, prefix=pfx)
    app.include_router(battle_router, prefix=pfx)
    app.include_router(leaderboard_router, prefix=pfx)
    app.include_router(reports_router, prefix=pfx)
    app.include_router(notifications_router, prefix=pfx)
    app.include_router(dashboard_router, prefix=pfx)
    app.include_router(categories_router, prefix=pfx)
    app.include_router(tutorials_router, prefix=pfx)
    app.include_router(bookmarks_router, prefix=pfx)
    app.include_router(progress_router, prefix=pfx)

# Aliases for singular /api/student/profile and /api/v1/student/profile
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.core.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.models.sql_models import UserModel

@app.get("/api/student/profile", response_model=UserResponse)
@app.get("/api/v1/student/profile", response_model=UserResponse)
def get_student_profile_singular(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user, from_attributes=True)

@app.get("/")
def root():
    return {
        "platform": "CodeArena – Learn, Practice & Compete",
        "status": "online",
        "api_docs": "/docs",
        "version": settings.VERSION
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/db-status")
def database_status():
    """Returns the current MySQL database connectivity status."""
    return check_mysql_connection()

# Gracefully absorb background polling from orphaned external browser tabs
@app.api_route("/api/v1/work/{path:path}", methods=["GET", "POST", "OPTIONS"])
def ignore_work_polling(path: str):
    return {"counts": 0, "unread_count": 0, "status": "ok"}

@app.api_route("/api/v1/people/{path:path}", methods=["GET", "POST", "OPTIONS"])
def ignore_people_polling(path: str):
    return []

@app.api_route("/api/v1/analytics/overview", methods=["GET", "OPTIONS"])
def get_analytics_overview():
    return {
        "status": "ok",
        "days": 30,
        "total_students": 150,
        "active_students": 120,
        "total_submissions": 450,
        "accuracy_rate": 88.5,
        "overview": {
            "daily_active_users": 85,
            "practice_sessions_completed": 310,
            "coding_challenges_solved": 195
        }
    }

@app.api_route("/api/v1/chat/{path:path}", methods=["GET", "POST", "OPTIONS"])
def handle_chat_channels(path: str):
    return []

