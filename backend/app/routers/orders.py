"""
Backward compatibility facade for orders router.
"""
from app.api.v1.orders import router, create_order, get_my_orders, get_order_by_id, cancel_order
from app.utils.qr_code import generate_order_number, generate_pickup_number, generate_qr_code

__all__ = [
    "router",
    "create_order",
    "get_my_orders",
    "get_order_by_id",
    "cancel_order",
    "generate_order_number",
    "generate_pickup_number",
    "generate_qr_code",
]
