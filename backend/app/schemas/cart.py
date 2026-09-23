from pydantic import BaseModel, ConfigDict
from app.schemas.product import ProductOut

class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductOut

    model_config = ConfigDict(from_attributes=True)

class WishlistToggle(BaseModel):
    product_id: int
