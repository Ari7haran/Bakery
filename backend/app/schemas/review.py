from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.schemas.user import UserOut

class ReviewCreate(BaseModel):
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str

class ReviewOut(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    comment: str
    created_at: datetime
    user: UserOut

    model_config = ConfigDict(from_attributes=True)
