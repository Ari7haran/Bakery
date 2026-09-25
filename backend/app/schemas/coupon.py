from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

class CouponApply(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, description="Coupon code")
    order_amount: float = Field(..., ge=0, description="Order subtotal amount (must be non-negative)")

    @field_validator("code")
    @classmethod
    def clean_code(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Coupon code cannot be empty or whitespace only")
        return cleaned

class CouponCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, description="Unique coupon code")
    discount_percent: float = Field(..., ge=0, le=100, description="Discount percentage between 0 and 100")
    max_discount_amount: float = Field(default=100.0, ge=0, description="Maximum discount cap amount")
    min_order_amount: float = Field(default=200.0, ge=0, description="Minimum order subtotal required")
    is_active: bool = Field(default=True, description="Whether coupon is currently active")
    expiry_date: Optional[datetime] = Field(None, description="Expiration date/time (UTC)")

    @field_validator("code")
    @classmethod
    def clean_code(cls, v: str) -> str:
        cleaned = v.strip().upper()
        if not cleaned:
            raise ValueError("Coupon code cannot be empty")
        return cleaned

class CouponUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=50, description="Updated coupon code")
    discount_percent: Optional[float] = Field(None, ge=0, le=100, description="Discount percentage between 0 and 100")
    max_discount_amount: Optional[float] = Field(None, ge=0, description="Maximum discount cap amount")
    min_order_amount: Optional[float] = Field(None, ge=0, description="Minimum order subtotal required")
    is_active: Optional[bool] = Field(None, description="Whether coupon is active")
    expiry_date: Optional[datetime] = Field(None, description="Expiration date/time (UTC)")

    @field_validator("code")
    @classmethod
    def clean_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip().upper()
        if not cleaned:
            raise ValueError("Coupon code cannot be empty")
        return cleaned

class CouponOut(BaseModel):
    id: int
    code: str
    discount_percent: float
    max_discount_amount: float
    min_order_amount: float
    is_active: bool
    expiry_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CouponValidationResult(BaseModel):
    valid: bool = True
    code: str
    discount_percent: float
    discount_amount: float
    min_order_amount: float = 0.0
    max_discount_amount: float = 0.0
    final_amount: Optional[float] = None
    message: Optional[str] = "Coupon applied successfully"
