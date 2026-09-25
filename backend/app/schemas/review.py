from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class ReviewSortOption(str, Enum):
    newest = "newest"
    oldest = "oldest"
    highest_rating = "highest_rating"
    lowest_rating = "lowest_rating"

class ReviewUserOut(BaseModel):
    id: int
    full_name: str

    model_config = ConfigDict(from_attributes=True)

class ReviewCreate(BaseModel):
    product_id: Optional[int] = Field(None, gt=0, description="Product ID must be greater than zero")
    rating: int = Field(..., ge=1, le=5, description="Rating must be between 1 and 5 stars")
    comment: Optional[str] = Field(default="", max_length=2000, description="Customer review comment")

    @field_validator("comment")
    @classmethod
    def clean_comment(cls, v: Optional[str]) -> str:
        if v is None:
            return ""
        return v.strip()

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating must be between 1 and 5 stars")
    comment: Optional[str] = Field(None, max_length=2000, description="Customer review comment")

    @field_validator("comment")
    @classmethod
    def clean_comment(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return v.strip()

class ReviewOut(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    comment: str
    created_at: datetime
    user: Optional[ReviewUserOut] = None
    is_verified_purchase: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)
