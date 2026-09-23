from typing import List, Dict, Any
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.core.exceptions import ResourceNotFoundError, BusinessRuleError
from app.models.cart import CartItem
from app.models.product import Product

class CartService:
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository):
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def get_cart(self, user_id: int) -> List[CartItem]:
        return self.cart_repo.get_user_cart(user_id)

    def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1) -> CartItem:
        if quantity <= 0:
            raise BusinessRuleError("Quantity must be greater than zero")

        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ResourceNotFoundError(f"Product with id {product_id} not found")

        if product.stock_quantity < quantity:
            raise BusinessRuleError(f"Insufficient stock for '{product.name}'. Available: {product.stock_quantity}")

        existing = self.cart_repo.get_user_cart_item_by_product(user_id, product_id)
        if existing:
            new_qty = existing.quantity + quantity
            if product.stock_quantity < new_qty:
                raise BusinessRuleError(f"Cannot add {quantity} more. Stock limit: {product.stock_quantity}")
            existing.quantity = new_qty
            self.cart_repo.db.commit()
            self.cart_repo.db.refresh(existing)
            return existing
        else:
            return self.cart_repo.add_cart_item(user_id, product_id, quantity)

    def update_cart_item(self, user_id: int, cart_id: int, quantity: int) -> CartItem:
        cart_item = self.cart_repo.get_cart_item(cart_id, user_id)
        if not cart_item:
            raise ResourceNotFoundError("Cart item not found")

        if quantity <= 0:
            self.cart_repo.delete(cart_item)
            return cart_item

        if cart_item.product and cart_item.product.stock_quantity < quantity:
            raise BusinessRuleError(
                f"Insufficient stock for '{cart_item.product.name}'. Available: {cart_item.product.stock_quantity}"
            )

        cart_item.quantity = quantity
        self.cart_repo.db.commit()
        self.cart_repo.db.refresh(cart_item)
        return cart_item

    def remove_cart_item(self, user_id: int, cart_id: int) -> None:
        cart_item = self.cart_repo.get_cart_item(cart_id, user_id)
        if not cart_item:
            raise ResourceNotFoundError("Cart item not found")
        self.cart_repo.delete(cart_item)

    def clear_cart(self, user_id: int) -> None:
        self.cart_repo.clear_cart(user_id)

    def get_wishlist(self, user_id: int) -> List[Product]:
        items = self.cart_repo.get_user_wishlist(user_id)
        return [item.product for item in items if item.product]

    def toggle_wishlist(self, user_id: int, product_id: int) -> Dict[str, Any]:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ResourceNotFoundError("Product not found")

        existing = self.cart_repo.get_wishlist_item(user_id, product_id)
        if existing:
            self.cart_repo.delete_wishlist_item(existing)
            return {"in_wishlist": False, "message": "Removed from wishlist"}
        else:
            self.cart_repo.add_wishlist_item(user_id, product_id)
            return {"in_wishlist": True, "message": "Added to wishlist"}
