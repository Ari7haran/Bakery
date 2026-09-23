"""
Backward compatibility facade for products router.
"""
from app.api.v1.products import router, get_categories, get_products, get_ai_recommendations, get_product, get_banners

__all__ = ["router", "get_categories", "get_products", "get_ai_recommendations", "get_product", "get_banners"]
