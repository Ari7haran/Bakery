from pydantic import BaseModel, ConfigDict
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    slug: str
    icon: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class CategoryOut(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
