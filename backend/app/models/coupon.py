from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.core.database import Base

class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    discount_percent = Column(Float, nullable=False)
    max_discount_amount = Column(Float, default=100.0)
    min_order_amount = Column(Float, default=200.0)
    is_active = Column(Boolean, default=True)
    expiry_date = Column(DateTime, nullable=True)
