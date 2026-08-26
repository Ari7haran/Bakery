import random
import string
import qrcode
import io
import base64
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.all_models import Order, OrderItem, CartItem, User, OrderStatusEnum, Coupon
from app.schemas.schemas import OrderCreate, OrderOut
from app.routers.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

def generate_order_number() -> str:
    digits = ''.join(random.choices(string.digits, k=6))
    return f"SC-{digits}"

def generate_pickup_number() -> str:
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    nums = ''.join(random.choices(string.digits, k=3))
    return f"PK-{letters}{nums}"

def generate_qr_code(data_str: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#2C1810", back_color="#FFFDF9")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

@router.post("/", response_model=OrderOut)
def create_order(order_in: OrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Your shopping cart is empty")

    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    discount_amount = 0.0

    if order_in.coupon_code:
        coupon = db.query(Coupon).filter(Coupon.code == order_in.coupon_code.upper(), Coupon.is_active == True).first()
        if coupon and total_amount >= coupon.min_order_amount:
            disc = (total_amount * coupon.discount_percent) / 100.0
            discount_amount = min(disc, coupon.max_discount_amount)

    final_amount = max(0.0, total_amount - discount_amount)
    order_num = generate_order_number()
    pickup_num = generate_pickup_number() if order_in.order_type == "Takeaway Pickup" else None

    # Generate QR Code content
    qr_payload = f"ORDER:{order_num}|USER:{current_user.email}|PICKUP:{pickup_num}|AMOUNT:₹{final_amount}"
    qr_code_image = generate_qr_code(qr_payload)

    new_order = Order(
        order_number=order_num,
        user_id=current_user.id,
        total_amount=round(total_amount, 2),
        discount_amount=round(discount_amount, 2),
        final_amount=round(final_amount, 2),
        order_type=order_in.order_type,
        pickup_date=order_in.pickup_date,
        pickup_time_slot=order_in.pickup_time_slot,
        pickup_number=pickup_num,
        qr_code_data=qr_code_image,
        status=OrderStatusEnum.RECEIVED.value,
        payment_method=order_in.payment_method,
        payment_status="Paid" if order_in.payment_method == "Online Payment" else "Pending",
        delivery_address=order_in.delivery_address,
        notes=order_in.notes
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Move cart items to order items
    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.add(order_item)
    
    # Clear cart
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    
    # Award loyalty points (10% of order value)
    earned_points = int(final_amount * 0.1)
    current_user.loyalty_points += earned_points

    db.commit()
    db.refresh(new_order)

    return new_order

@router.get("/my-orders", response_model=List[OrderOut])
def get_my_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()

@router.get("/{order_id}", response_model=OrderOut)
def get_order_by_id(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return order
