"""
Backward compatibility facade for admin router.
"""
from app.api.v1.admin import (
    router,
    get_analytics,
    get_all_orders,
    update_order_status,
    create_product,
    update_product,
    delete_product,
    get_all_users,
)

__all__ = [
    "router",
    "get_analytics",
    "get_all_orders",
    "update_order_status",
    "create_product",
    "update_product",
    "delete_product",
    "get_all_users",
]
