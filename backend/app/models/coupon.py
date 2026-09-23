from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, CheckConstraint
from app.core.database import Base

class Coupon(Base):
    __tablename__ = "coupons"
    __table_args__ = (
        CheckConstraint("discount_percent >= 0 AND discount_percent <= 100", name="check_coupon_discount_percent_range"),
        CheckConstraint("min_order_amount >= 0", name="check_coupon_min_order_amount_non_neg"),
        CheckConstraint("max_discount_amount >= 0", name="check_coupon_max_discount_amount_non_neg"),
    )

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    discount_percent = Column(Float, nullable=False)
    max_discount_amount = Column(Float, default=100.0, nullable=False)
    min_order_amount = Column(Float, default=200.0, nullable=False)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
