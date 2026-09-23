from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.coupon_repository import CouponRepository
from app.services.cart_service import CartService
from app.services.coupon_service import CouponService
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartItemOut
from app.schemas.product import ProductOut
from app.schemas.coupon import CouponApply, CouponValidationResult

router = APIRouter(prefix="/user", tags=["Cart & Wishlist"])

def get_cart_service(db: Session = Depends(get_db)) -> CartService:
    return CartService(
        cart_repo=CartRepository(db),
        product_repo=ProductRepository(db)
    )

def get_coupon_service(db: Session = Depends(get_db)) -> CouponService:
    return CouponService(CouponRepository(db))

@router.get("/cart", response_model=List[CartItemOut])
def get_cart(current_user: User = Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    return service.get_cart(current_user.id)

@router.post("/cart", response_model=CartItemOut)
def add_to_cart(item_in: CartItemAdd, current_user: User = Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    return service.add_to_cart(current_user.id, item_in.product_id, item_in.quantity)

@router.put("/cart/{cart_id}", response_model=CartItemOut)
def update_cart_item(cart_id: int, item_in: CartItemUpdate, current_user: User = Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    return service.update_cart_item(current_user.id, cart_id, item_in.quantity)

@router.delete("/cart/{cart_id}")
def remove_cart_item(cart_id: int, current_user: User = Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    service.remove_cart_item(current_user.id, cart_id)
    return {"message": "Cart item removed"}

@router.delete("/cart-clear")
def clear_cart(current_user: User = Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    service.clear_cart(current_user.id)
    return {"message": "Cart cleared"}

@router.get("/wishlist", response_model=List[ProductOut])
def get_wishlist(current_user: User = Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    return service.get_wishlist(current_user.id)

@router.post("/wishlist/toggle/{product_id}")
def toggle_wishlist(product_id: int, current_user: User = Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    return service.toggle_wishlist(current_user.id, product_id)

@router.post("/coupon/validate", response_model=CouponValidationResult)
def validate_coupon(data: CouponApply, service: CouponService = Depends(get_coupon_service)):
    return service.validate_coupon(data.code, data.order_amount)
