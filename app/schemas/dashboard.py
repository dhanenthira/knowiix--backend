from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.schemas.tutorial import ContinueLearningItem, TutorialResponse
from app.schemas.progress import LearningActivityResponse

class DashboardSummaryResponse(BaseModel):
    available_courses: int # Count of published tutorials
    courses_started: int # Distinct tutorials with at least one progress record
    completed_lessons: int # Distinct topics marked completed
    saved_tutorials: int # Distinct bookmarks
    overall_progress_percentage: float # (completed_lessons / total_available_topics) * 100
    total_available_topics: int

    model_config = ConfigDict(from_attributes=True)
