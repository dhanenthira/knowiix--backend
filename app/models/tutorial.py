from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class TutorialModel(Base):
    __tablename__ = "tutorials"

    id = Column(String(64), primary_key=True, index=True)
    category_id = Column(String(64), ForeignKey("categories.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, default="")
    difficulty = Column(String(32), default="Beginner")
    estimated_minutes = Column(Integer, default=20)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("CategoryModel", back_populates="tutorials")
    topics = relationship("TopicModel", back_populates="tutorial", cascade="all, delete-orphan")
    bookmarks = relationship("BookmarkModel", back_populates="tutorial", cascade="all, delete-orphan")
