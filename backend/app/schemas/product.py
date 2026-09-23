from pydantic import BaseModel, ConfigDict
from typing import List, Optional
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
    price: float
    discount_price: Optional[float] = None
    is_veg: bool = True
    is_featured: bool = False
    is_todays_fresh: bool = False
    is_popular: bool = False
    ingredients: Optional[str] = None
    nutrition_info: Optional[str] = None
    prep_time: str = "15-20 mins"
    stock_quantity: int = 25
    image_url: str

class ProductOut(ProductBase):
    id: int
    rating: float
    review_count: int
    category: Optional[CategoryOut] = None
    images: List[ProductImageOut] = []

    model_config = ConfigDict(from_attributes=True)
