"""
Backward compatibility facade for cart router.
"""
from app.api.v1.cart import (
    router,
    get_cart,
    add_to_cart,
    update_cart_item,
    remove_cart_item,
    clear_cart,
    get_wishlist,
    toggle_wishlist,
    validate_coupon,
)

__all__ = [
    "router",
    "get_cart",
    "add_to_cart",
    "update_cart_item",
    "remove_cart_item",
    "clear_cart",
    "get_wishlist",
    "toggle_wishlist",
    "validate_coupon",
]
