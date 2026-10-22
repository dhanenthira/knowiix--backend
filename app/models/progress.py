from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserProgressModel(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    topic_id = Column(String(64), ForeignKey("topics.id", ondelete="CASCADE"), index=True, nullable=False)
    is_completed = Column(Boolean, default=False)
    last_read_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    reading_position = Column(Integer, default=0)

    topic = relationship("TopicModel", back_populates="progress")
