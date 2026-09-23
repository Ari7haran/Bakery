from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    role: str
    loyalty_points: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
