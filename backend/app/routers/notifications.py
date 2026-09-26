"""
Backward compatibility facade for notifications router.
"""
from app.api.v1.notifications import (
    router,
    list_notifications,
    get_unread_count,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    delete_notification,
)

__all__ = [
    "router",
    "list_notifications",
    "get_unread_count",
    "mark_notification_as_read",
    "mark_all_notifications_as_read",
    "delete_notification",
]
