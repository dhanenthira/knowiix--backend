import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


def _gen_bm_id():
    return f"bm_{uuid.uuid4().hex[:16]}"


class BookmarkModel(Base):
    __tablename__ = "bookmarks"

    id = Column(String(64), primary_key=True, default=_gen_bm_id)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    tutorial_id = Column(String(64), ForeignKey("tutorials.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tutorial = relationship("TutorialModel", back_populates="bookmarks")
