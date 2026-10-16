from pydantic import BaseModel, ConfigDict
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = ""
    icon: Optional[str] = "code"
    display_order: int = 0
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: str
    tutorial_count: int = 0

    model_config = ConfigDict(from_attributes=True)
