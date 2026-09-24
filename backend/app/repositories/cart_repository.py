from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.cart import CartItem, WishlistItem

class CartRepository(BaseRepository[CartItem]):
    def __init__(self, db: Session):
        super().__init__(CartItem, db)

    def get_user_cart(self, user_id: int) -> List[CartItem]:
        return self.db.query(CartItem).filter(CartItem.user_id == user_id).all()

    def get_cart_item(self, cart_id: int, user_id: int) -> Optional[CartItem]:
        return self.db.query(CartItem).filter(CartItem.id == cart_id, CartItem.user_id == user_id).first()

    def get_user_cart_item_by_product(self, user_id: int, product_id: int) -> Optional[CartItem]:
        return self.db.query(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id
        ).first()

    def add_cart_item(self, user_id: int, product_id: int, quantity: int) -> CartItem:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        return self.add(item)

    def clear_cart(self, user_id: int, commit: bool = True) -> None:
        self.db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        if commit:
            self.db.commit()

    # Wishlist operations
    def get_user_wishlist(self, user_id: int) -> List[WishlistItem]:
        return self.db.query(WishlistItem).filter(WishlistItem.user_id == user_id).all()

    def get_wishlist_item(self, user_id: int, product_id: int) -> Optional[WishlistItem]:
        return self.db.query(WishlistItem).filter(
            WishlistItem.user_id == user_id,
            WishlistItem.product_id == product_id
        ).first()

    def add_wishlist_item(self, user_id: int, product_id: int) -> WishlistItem:
        item = WishlistItem(user_id=user_id, product_id=product_id)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_wishlist_item(self, item: WishlistItem) -> None:
        self.db.delete(item)
        self.db.commit()
