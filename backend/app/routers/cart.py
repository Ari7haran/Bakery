from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.all_models import CartItem, WishlistItem, Product, User, Coupon
from app.schemas.schemas import CartItemAdd, CartItemUpdate, CartItemOut, ProductOut, CouponApply
from app.routers.auth import get_current_user

router = APIRouter(prefix="/user", tags=["Cart & Wishlist"])

@router.get("/cart", response_model=List[CartItemOut])
def get_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(CartItem).filter(CartItem.user_id == current_user.id).all()

@router.post("/cart", response_model=CartItemOut)
def add_to_cart(item_in: CartItemAdd, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == item_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == item_in.product_id
    ).first()

    if existing:
        existing.quantity += item_in.quantity
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_item = CartItem(user_id=current_user.id, product_id=item_in.product_id, quantity=item_in.quantity)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

@router.put("/cart/{cart_id}", response_model=CartItemOut)
def update_cart_item(cart_id: int, item_in: CartItemUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == cart_id, CartItem.user_id == current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if item_in.quantity <= 0:
        db.delete(cart_item)
        db.commit()
        return cart_item

    cart_item.quantity = item_in.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/cart/{cart_id}")
def remove_cart_item(cart_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == cart_id, CartItem.user_id == current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(cart_item)
    db.commit()
    return {"message": "Cart item removed"}

@router.delete("/cart-clear")
def clear_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Cart cleared"}

@router.get("/wishlist", response_model=List[ProductOut])
def get_wishlist(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(WishlistItem).filter(WishlistItem.user_id == current_user.id).all()
    return [item.product for item in items]

@router.post("/wishlist/toggle/{product_id}")
def toggle_wishlist(product_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.product_id == product_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"in_wishlist": False, "message": "Removed from wishlist"}
    else:
        new_wish = WishlistItem(user_id=current_user.id, product_id=product_id)
        db.add(new_wish)
        db.commit()
        return {"in_wishlist": True, "message": "Added to wishlist"}

@router.post("/coupon/validate")
def validate_coupon(data: CouponApply, db: Session = Depends(get_db)):
    coupon = db.query(Coupon).filter(Coupon.code == data.code.upper(), Coupon.is_active == True).first()
    if not coupon:
        raise HTTPException(status_code=400, detail="Invalid or expired coupon code")
    
    if data.order_amount < coupon.min_order_amount:
        raise HTTPException(status_code=400, detail=f"Minimum order amount for this coupon is ₹{coupon.min_order_amount}")

    discount = (data.order_amount * coupon.discount_percent) / 100.0
    discount = min(discount, coupon.max_discount_amount)

    return {
        "valid": True,
        "code": coupon.code,
        "discount_percent": coupon.discount_percent,
        "discount_amount": round(discount, 2)
    }
