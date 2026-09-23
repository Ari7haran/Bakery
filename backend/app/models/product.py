from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True, nullable=False)
    slug = Column(String(150), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    is_veg = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_todays_fresh = Column(Boolean, default=False)
    is_popular = Column(Boolean, default=False)
    ingredients = Column(Text, nullable=True)
    nutrition_info = Column(Text, nullable=True)
    prep_time = Column(String(50), default="15-20 mins")
    rating = Column(Float, default=4.8)
    review_count = Column(Integer, default=12)
    stock_quantity = Column(Integer, default=25)
    image_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")

class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    image_url = Column(String(500), nullable=False)

    product = relationship("Product", back_populates="images")
