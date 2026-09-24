from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.category import CategoryOut

class ProductImageOut(BaseModel):
    id: int
    image_url: str

    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    name: str
    slug: str
    category_id: int
    description: str
    price: float = Field(..., ge=0, description="Price must be non-negative")
    discount_price: Optional[float] = Field(None, ge=0, description="Discount price must be non-negative")
    is_veg: bool = True
    is_featured: bool = False
    is_todays_fresh: bool = False
    is_popular: bool = False
    ingredients: Optional[str] = None
    nutrition_info: Optional[str] = None
    prep_time: str = "15-20 mins"
    stock_quantity: int = Field(25, ge=0, description="Stock quantity must be a non-negative integer")
    image_url: str

class ProductStockUpdate(BaseModel):
    stock_quantity: int = Field(..., ge=0, description="Stock quantity must be a non-negative integer")

class ProductOut(ProductBase):
    id: int
    rating: float
    review_count: int
    category: Optional[CategoryOut] = None
    images: List[ProductImageOut] = []

    model_config = ConfigDict(from_attributes=True)
