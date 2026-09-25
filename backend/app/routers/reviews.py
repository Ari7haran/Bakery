"""
Backward compatibility facade for reviews router.
"""
from app.api.v1.reviews import (
    router,
    get_product_reviews,
    create_review,
    create_product_review,
    update_review,
    delete_review,
)

__all__ = [
    "router",
    "get_product_reviews",
    "create_review",
    "create_product_review",
    "update_review",
    "delete_review",
]
