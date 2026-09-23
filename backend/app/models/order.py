import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class OrderStatusEnum(str, enum.Enum):
    RECEIVED = "Received"
    PREPARING = "Preparing"
    BAKING = "Baking"
    PACKING = "Packing"
    READY_FOR_PICKUP = "Ready for Pickup"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class OrderTypeEnum(str, enum.Enum):
    DELIVERY = "Delivery"
    TAKEAWAY = "Takeaway Pickup"

class PaymentStatusEnum(str, enum.Enum):
    PENDING = "Pending"
    PAID = "Paid"
    FAILED = "Failed"

class PaymentMethodEnum(str, enum.Enum):
    CASH = "CASH"
    CASH_ON_PICKUP = "Cash on Pickup"
    CASH_ON_DELIVERY = "Cash on Delivery"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    order_type = Column(String(50), default=OrderTypeEnum.TAKEAWAY.value)
    pickup_date = Column(String(50), nullable=True)
    pickup_time_slot = Column(String(50), nullable=True)
    pickup_number = Column(String(20), nullable=True)
    qr_code_data = Column(Text, nullable=True)
    status = Column(String(50), default=OrderStatusEnum.RECEIVED.value)
    payment_method = Column(String(50), default="Cash on Pickup")
    payment_status = Column(String(50), default=PaymentStatusEnum.PENDING.value)
    delivery_address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
