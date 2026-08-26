from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# Auth Schemas
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
    user: "UserOut"

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    role: str
    loyalty_points: int
    is_active: bool

    class Config:
        from_attributes = True

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    icon: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# Product Image
class ProductImageOut(BaseModel):
    id: int
    image_url: str

    class Config:
        from_attributes = True

# Product Schemas
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

    class Config:
        from_attributes = True

# Cart Schemas
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

    class Config:
        from_attributes = True

# Wishlist
class WishlistToggle(BaseModel):
    product_id: int

# Order Schemas
class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: ProductOut

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    order_type: str = "Takeaway Pickup" # Delivery or Takeaway Pickup
    pickup_date: Optional[str] = None
    pickup_time_slot: Optional[str] = None
    delivery_address: Optional[str] = None
    payment_method: str = "Cash on Pickup"
    coupon_code: Optional[str] = None
    notes: Optional[str] = None

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

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str

# Review Schemas
class ReviewCreate(BaseModel):
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str

class ReviewOut(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    comment: str
    created_at: datetime
    user: UserOut

    class Config:
        from_attributes = True

# Coupon Schemas
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

    class Config:
        from_attributes = True

# Analytics Dashboard Schema
class AnalyticsOut(BaseModel):
    total_revenue: float
    today_orders: int
    monthly_sales: float
    customer_count: int
    popular_products: List[dict]
    sales_chart: List[dict]
