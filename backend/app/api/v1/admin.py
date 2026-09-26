from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.banner_repository import BannerRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.coupon_repository import CouponRepository
from app.repositories.notification_repository import NotificationRepository
from app.services.admin_service import AdminService
from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.services.coupon_service import CouponService
from app.services.payment_service import PaymentService
from app.services.notification_service import NotificationService
from app.schemas.analytics import AnalyticsOut
from app.schemas.order import OrderOut, OrderStatusUpdate
from app.schemas.product import ProductOut, ProductBase, ProductStockUpdate
from app.schemas.user import UserOut

router = APIRouter(prefix="/admin", tags=["Admin Dashboard & Management"])

def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(
        order_repo=OrderRepository(db),
        user_repo=UserRepository(db)
    )

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

def get_product_service(
    db: Session = Depends(get_db),
    notif_service: NotificationService = Depends(get_notification_service)
) -> ProductService:
    return ProductService(
        product_repo=ProductRepository(db),
        category_repo=CategoryRepository(db),
        banner_repo=BannerRepository(db),
        review_repo=ReviewRepository(db),
        notification_service=notif_service
    )

def get_payment_service(
    db: Session = Depends(get_db),
    notif_service: NotificationService = Depends(get_notification_service)
) -> PaymentService:
    return PaymentService(OrderRepository(db), notification_service=notif_service)

@router.get("/analytics", response_model=AnalyticsOut)
def get_analytics(
    admin: User = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    return service.get_analytics()

@router.get("/orders", response_model=List[OrderOut])
def get_all_orders(
    admin: User = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    return service.list_orders()

@router.put("/orders/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    admin: User = Depends(get_current_admin),
    service: OrderService = Depends(get_order_service)
):
    return service.update_order_status(order_id, payload.status)

@router.put("/orders/{order_id}/payment", response_model=OrderOut)
def mark_order_payment_paid(
    order_id: int,
    admin: User = Depends(get_current_admin),
    service: PaymentService = Depends(get_payment_service)
):
    return service.mark_payment_paid(order_id)

@router.post("/products", response_model=ProductOut)
def create_product(
    product_in: ProductBase,
    admin: User = Depends(get_current_admin),
    service: ProductService = Depends(get_product_service)
):
    return service.create_product(product_in)

@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    product_in: ProductBase,
    admin: User = Depends(get_current_admin),
    service: ProductService = Depends(get_product_service)
):
    return service.update_product(product_id, product_in)

@router.put("/products/{product_id}/stock", response_model=ProductOut)
@router.patch("/products/{product_id}/stock", response_model=ProductOut)
def update_product_stock(
    product_id: int,
    stock_in: ProductStockUpdate,
    admin: User = Depends(get_current_admin),
    service: ProductService = Depends(get_product_service)
):
    return service.update_product_stock(product_id, stock_in.stock_quantity)

@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    admin: User = Depends(get_current_admin),
    service: ProductService = Depends(get_product_service)
):
    service.delete_product(product_id)
    return {"message": "Product deleted successfully"}

@router.get("/users", response_model=List[UserOut])
def get_all_users(
    admin: User = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    return service.list_users()
