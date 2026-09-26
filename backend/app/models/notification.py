import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class NotificationTypeEnum(str, enum.Enum):
    ORDER_CREATED = "order_created"
    ORDER_STATUS = "order_status"
    ORDER_CANCELLED = "order_cancelled"
    PAYMENT = "payment"
    INVENTORY = "inventory"
    LOYALTY = "loyalty"
    SYSTEM = "system"

class NotificationPriorityEnum(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            "priority IN ('low', 'normal', 'high', 'urgent')",
            name="check_notification_priority"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default=NotificationTypeEnum.SYSTEM.value, index=True, nullable=False)
    priority = Column(String(20), default=NotificationPriorityEnum.NORMAL.value, nullable=False)
    is_read = Column(Boolean, default=False, index=True, nullable=False)
    read_at = Column(DateTime, nullable=True)
    link_url = Column(String(255), nullable=True)
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    user = relationship("User", back_populates="notifications")
