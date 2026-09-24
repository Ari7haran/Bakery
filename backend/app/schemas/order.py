from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.product import ProductOut

class OrderItemInput(BaseModel):
    product_id: int
    quantity: int = Field(1, gt=0, description="Quantity must be greater than zero")

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: Optional[ProductOut] = None

    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    order_type: str = "Takeaway Pickup"  # Delivery or Takeaway Pickup
    pickup_date: Optional[str] = None
    pickup_time_slot: Optional[str] = None
    delivery_address: Optional[str] = None
    payment_method: str = "Cash on Pickup"
    coupon_code: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[OrderItemInput]] = None

class OrderOut(BaseModel):
    id: int
    order_number: str
    total_amount: float
    discount_amount: float
    final_amount: float
    order_type: str
    pickup_date: Optional[str] = None
    pickup_time_slot: Optional[str] = None
    pickup_number: Optional[str] = None
    qr_code_data: Optional[str] = None
    status: str
    payment_method: str
    payment_status: str
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    items: List[OrderItemOut] = []

    model_config = ConfigDict(from_attributes=True)

class OrderStatusUpdate(BaseModel):
    status: str

class PaymentStatusUpdate(BaseModel):
    payment_status: str = Field(..., description="Payment status: Pending, Paid, or Failed")
