from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from app.schemas.user import UserOut

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

    model_config = ConfigDict(from_attributes=True)
