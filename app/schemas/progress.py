from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, Union

class TopicProgressResponse(BaseModel):
    id: str
    user_id: str
    topic_id: str
    is_completed: bool
    last_read_at: datetime
    completed_at: Optional[datetime] = None
    reading_position: int = 0
    topic_title: Optional[str] = None
    tutorial_id: Optional[str] = None
    tutorial_title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserProgressSummary(BaseModel):
    total_available_topics: int
    completed_topics_count: int
    overall_progress_percentage: float
    completed_topics: List[TopicProgressResponse] = []
    in_progress_topics: List[TopicProgressResponse] = []

    model_config = ConfigDict(from_attributes=True)

class LearningActivityResponse(BaseModel):
    id: Union[int, str]
    user_id: str
    tutorial_id: Optional[str] = None
    topic_id: Optional[str] = None
    activity_type: str
    created_at: datetime
    tutorial_title: Optional[str] = None
    topic_title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
