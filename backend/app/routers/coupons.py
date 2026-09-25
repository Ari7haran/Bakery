"""
Backward compatibility facade for coupons router.
"""
from app.api.v1.coupons import (
    router,
    list_active_coupons,
    validate_coupon_endpoint,
    admin_list_all_coupons,
    admin_create_coupon,
    admin_get_coupon,
    admin_update_coupon,
    admin_delete_coupon,
)

__all__ = [
    "router",
    "list_active_coupons",
    "validate_coupon_endpoint",
    "admin_list_all_coupons",
    "admin_create_coupon",
    "admin_get_coupon",
    "admin_update_coupon",
    "admin_delete_coupon",
]
