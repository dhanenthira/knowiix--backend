from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class BookmarkModel(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    tutorial_id = Column(String(64), ForeignKey("tutorials.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tutorial = relationship("TutorialModel", back_populates="bookmarks")
