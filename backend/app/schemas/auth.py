from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from typing import Optional
from app.schemas.user import UserOut

class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name of the user")
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72, description="Password must be between 6 and 72 characters")
    phone: Optional[str] = Field(None, max_length=20)

    @field_validator("full_name")
    @classmethod
    def full_name_must_not_be_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Full name cannot be blank")
        return stripped

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=72)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

    model_config = ConfigDict(from_attributes=True)
