from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class CouponApply(BaseModel):
    code: str
    order_amount: float

class CouponOut(BaseModel):
    id: int
    code: str
    discount_percent: float
    max_discount_amount: float
    min_order_amount: float
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class CouponValidationResult(BaseModel):
    valid: bool
    code: str
    discount_percent: float
    discount_amount: float
