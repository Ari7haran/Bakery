from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

class NotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150, description="Headline of the notification")
    message: str = Field(..., min_length=1, description="Notification body content")
    notification_type: str = Field("system", max_length=50, description="Type: order_created, order_status, order_cancelled, payment, inventory, loyalty, system")
    priority: str = Field("normal", description="Priority level: low, normal, high, urgent")
    link_url: Optional[str] = Field(None, max_length=255, description="Relative URL to navigate to upon click")
    related_entity_type: Optional[str] = Field(None, max_length=50, description="Entity type, e.g. order, product")
    related_entity_id: Optional[int] = Field(None, description="Primary key of related entity")

class NotificationCreate(NotificationBase):
    user_id: int = Field(..., description="Target user recipient ID")

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = Field(None, description="Read state toggle")

class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    priority: str
    is_read: bool
    read_at: Optional[datetime] = None
    link_url: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UnreadCountOut(BaseModel):
    unread_count: int = Field(..., ge=0, description="Total count of unread notifications for current user")

class NotificationListOut(BaseModel):
    items: List[NotificationOut] = Field(default_factory=list)
    total: int = Field(0, ge=0)
    unread_count: int = Field(0, ge=0)
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1)

    model_config = ConfigDict(from_attributes=True)
