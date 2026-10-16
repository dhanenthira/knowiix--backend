from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class TopicBase(BaseModel):
    title: str
    content: str
    code_example: Optional[str] = ""
    display_order: int = 1

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: str
    tutorial_id: str
    is_completed: bool = False

    model_config = ConfigDict(from_attributes=True)

class TutorialBase(BaseModel):
    category_id: str
    title: str
    slug: str
    description: Optional[str] = ""
    difficulty: str = "Beginner"
    estimated_minutes: int = 15
    is_published: bool = True

class TutorialCreate(TutorialBase):
    pass

class TutorialResponse(TutorialBase):
    id: str
    created_at: datetime
    category_name: Optional[str] = None
    category_slug: Optional[str] = None
    category_icon: Optional[str] = None
    total_topics: int = 0
    completed_topics: int = 0
    progress_percentage: float = 0.0
    is_bookmarked: bool = False
    topics: Optional[List[TopicResponse]] = None

    model_config = ConfigDict(from_attributes=True)

class ContinueLearningItem(BaseModel):
    tutorial_id: str
    tutorial_title: str
    tutorial_slug: str
    category_name: str
    category_slug: str
    category_icon: str
    total_topics: int
    completed_topics: int
    progress_percentage: float
    last_accessed_at: datetime
    last_topic_id: Optional[str] = None
    last_topic_title: Optional[str] = None
    resume_route: str

    model_config = ConfigDict(from_attributes=True)
