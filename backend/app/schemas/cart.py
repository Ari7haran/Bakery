from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.product import ProductOut

class CartItemAdd(BaseModel):
    product_id: int = Field(..., gt=0, description="Product ID must be greater than zero")
    quantity: int = Field(1, gt=0, description="Quantity must be greater than zero")

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0, description="Quantity must be greater than zero")

class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductOut
    subtotal: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class WishlistToggle(BaseModel):
    product_id: int = Field(..., gt=0, description="Product ID must be greater than zero")
