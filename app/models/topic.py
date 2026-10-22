from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class TopicModel(Base):
    __tablename__ = "topics"

    id = Column(String(64), primary_key=True, index=True)
    tutorial_id = Column(String(64), ForeignKey("tutorials.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, default="")
    code_example = Column(Text, default="")
    display_order = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    tutorial = relationship("TutorialModel", back_populates="topics")
    progress = relationship("UserProgressModel", back_populates="topic", cascade="all, delete-orphan")
