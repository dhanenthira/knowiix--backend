from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    slug = Column(String(128), unique=True, index=True, nullable=False)
    description = Column(Text, default="")
    icon = Column(String(64), default="code")
    display_order = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tutorials = relationship("TutorialModel", back_populates="category", cascade="all, delete-orphan")
