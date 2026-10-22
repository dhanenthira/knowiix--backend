from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.core.database import Base


class LearningActivityModel(Base):
    __tablename__ = "learning_activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    tutorial_id = Column(String(64), nullable=True)
    topic_id = Column(String(64), nullable=True)
    activity_type = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
