from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.schemas.tutorial import TutorialResponse

class BookmarkResponse(BaseModel):
    id: str
    user_id: str
    tutorial_id: str
    created_at: datetime
    tutorial: Optional[TutorialResponse] = None

    model_config = ConfigDict(from_attributes=True)
