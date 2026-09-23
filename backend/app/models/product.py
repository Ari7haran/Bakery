from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_product_price_non_neg"),
        CheckConstraint("stock_quantity >= 0", name="check_product_stock_non_neg"),
        CheckConstraint("discount_price IS NULL OR discount_price >= 0", name="check_product_discount_non_neg"),
        CheckConstraint("rating >= 0 AND rating <= 5", name="check_product_rating_range"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True, nullable=False)
    slug = Column(String(150), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), index=True, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    is_veg = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    is_todays_fresh = Column(Boolean, default=False, nullable=False)
    is_popular = Column(Boolean, default=False, nullable=False)
    ingredients = Column(Text, nullable=True)
    nutrition_info = Column(Text, nullable=True)
    prep_time = Column(String(50), default="15-20 mins")
    rating = Column(Float, default=4.8, nullable=False)
    review_count = Column(Integer, default=12, nullable=False)
    stock_quantity = Column(Integer, default=25, nullable=False)
    image_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")

class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    image_url = Column(String(500), nullable=False)

    product = relationship("Product", back_populates="images")
