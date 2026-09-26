from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.user_repository import UserRepository
from app.repositories.coupon_repository import CouponRepository
from app.repositories.notification_repository import NotificationRepository
from app.services.order_service import OrderService
from app.services.coupon_service import CouponService
from app.services.payment_service import PaymentService
from app.services.notification_service import NotificationService
from app.schemas.order import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["Orders"])

def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(
        notification_repo=NotificationRepository(db),
        user_repo=UserRepository(db),
        db=db
    )

def get_order_service(
    db: Session = Depends(get_db),
    notif_service: NotificationService = Depends(get_notification_service)
) -> OrderService:
    order_repo = OrderRepository(db)
    product_repo = ProductRepository(db)
    cart_repo = CartRepository(db)
    user_repo = UserRepository(db)
    coupon_service = CouponService(CouponRepository(db))
    payment_service = PaymentService(order_repo, notification_service=notif_service)
    return OrderService(
        order_repo=order_repo,
        product_repo=product_repo,
        cart_repo=cart_repo,
        user_repo=user_repo,
        coupon_service=coupon_service,
        payment_service=payment_service,
        db=db,
        notification_service=notif_service
    )

@router.post("/", response_model=OrderOut)
def create_order(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    return service.create_order(current_user, order_in)

@router.get("/my-orders", response_model=List[OrderOut])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    return service.get_my_orders(current_user.id)

@router.get("/{order_id}", response_model=OrderOut)
def get_order_by_id(
    order_id: int,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    return service.get_order_by_id(current_user, order_id)

@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    return service.cancel_order(current_user, order_id)
