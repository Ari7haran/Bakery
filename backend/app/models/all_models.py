"""
Backward-compatibility facade for models.
Re-exports all models from app.models to ensure existing references continue to function.
"""
from app.models import (
    User,
    Address,
    RoleEnum,
    Category,
    Product,
    ProductImage,
    CartItem,
    WishlistItem,
    Order,
    OrderItem,
    OrderStatusEnum,
    OrderTypeEnum,
    PaymentStatusEnum,
    PaymentMethodEnum,
    Coupon,
    Review,
    Banner,
)

__all__ = [
    "User",
    "Address",
    "RoleEnum",
    "Category",
    "Product",
    "ProductImage",
    "CartItem",
    "WishlistItem",
    "Order",
    "OrderItem",
    "OrderStatusEnum",
    "OrderTypeEnum",
    "PaymentStatusEnum",
    "PaymentMethodEnum",
    "Coupon",
    "Review",
    "Banner",
]
