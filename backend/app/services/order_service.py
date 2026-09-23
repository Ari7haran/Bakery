from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.user_repository import UserRepository
from app.services.coupon_service import CouponService
from app.services.payment_service import PaymentService
from app.core.exceptions import ResourceNotFoundError, BusinessRuleError, ForbiddenError
from app.models.order import Order, OrderItem, OrderStatusEnum, PaymentStatusEnum
from app.models.user import User
from app.schemas.order import OrderCreate
from app.utils.qr_code import generate_order_number, generate_pickup_number, generate_qr_code

# Strict Order Lifecycle State Machine
ALLOWED_STATUS_TRANSITIONS = {
    OrderStatusEnum.RECEIVED.value: {OrderStatusEnum.PREPARING.value, OrderStatusEnum.CANCELLED.value},
    OrderStatusEnum.PREPARING.value: {OrderStatusEnum.BAKING.value, OrderStatusEnum.CANCELLED.value},
    OrderStatusEnum.BAKING.value: {OrderStatusEnum.PACKING.value, OrderStatusEnum.CANCELLED.value},
    OrderStatusEnum.PACKING.value: {OrderStatusEnum.READY_FOR_PICKUP.value, OrderStatusEnum.CANCELLED.value},
    OrderStatusEnum.READY_FOR_PICKUP.value: {OrderStatusEnum.COMPLETED.value, OrderStatusEnum.CANCELLED.value},
    OrderStatusEnum.COMPLETED.value: set(),
    OrderStatusEnum.CANCELLED.value: set(),
}

class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        cart_repo: CartRepository,
        user_repo: UserRepository,
        coupon_service: CouponService,
        payment_service: PaymentService,
        db: Session
    ):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.cart_repo = cart_repo
        self.user_repo = user_repo
        self.coupon_service = coupon_service
        self.payment_service = payment_service
        self.db = db

    def create_order(self, current_user: User, order_in: OrderCreate) -> Order:
        # 1. Validate payment method: CASH only
        normalized_payment_method = self.payment_service.validate_payment_method(order_in.payment_method)

        # 2. Gather items to order
        raw_items = []
        used_db_cart = False

        if order_in.items and len(order_in.items) > 0:
            for item_in in order_in.items:
                if item_in.quantity <= 0:
                    raise BusinessRuleError("Item quantity must be greater than zero")
                raw_items.append((item_in.product_id, item_in.quantity))
        else:
            db_cart = self.cart_repo.get_user_cart(current_user.id)
            if not db_cart:
                raise BusinessRuleError("Your shopping cart is empty")
            used_db_cart = True
            for c_item in db_cart:
                raw_items.append((c_item.product_id, c_item.quantity))

        if not raw_items:
            raise BusinessRuleError("Your shopping cart is empty")

        # 3. Validate products, stock, and calculate authoritative server-side prices
        order_items_data = []
        total_amount = 0.0

        for product_id, quantity in raw_items:
            product = self.product_repo.get_by_id(product_id)
            if not product:
                raise ResourceNotFoundError(f"Product with id {product_id} not found")

            if product.stock_quantity < quantity:
                raise BusinessRuleError(
                    f"Insufficient stock for '{product.name}'. Requested: {quantity}, Available: {product.stock_quantity}"
                )

            # Server-authoritative unit price
            unit_price = product.discount_price if product.discount_price is not None else product.price
            total_amount += unit_price * quantity

            order_items_data.append({
                "product": product,
                "product_id": product.id,
                "quantity": quantity,
                "price": unit_price
            })

        # 4. Coupon discount calculation
        discount_amount = 0.0
        if order_in.coupon_code:
            discount_amount = self.coupon_service.calculate_discount(order_in.coupon_code, total_amount)

        final_amount = max(0.0, total_amount - discount_amount)
        order_num = generate_order_number()
        is_takeaway = "Takeaway" in order_in.order_type
        pickup_num = generate_pickup_number() if is_takeaway else None

        # 5. Generate QR Code
        qr_payload = f"ORDER:{order_num}|USER:{current_user.email}|PICKUP:{pickup_num}|AMOUNT:₹{round(final_amount, 2)}"
        qr_code_image = generate_qr_code(qr_payload)

        # 6. Atomic Transaction: deduct stock, save order, save items, award points, clear cart
        try:
            for item in order_items_data:
                item["product"].stock_quantity -= item["quantity"]

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
                payment_method=normalized_payment_method,
                payment_status=PaymentStatusEnum.PENDING.value,
                delivery_address=order_in.delivery_address,
                notes=order_in.notes
            )
            self.db.add(new_order)
            self.db.flush()

            for item in order_items_data:
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    price=item["price"]
                )
                self.db.add(order_item)

            if used_db_cart:
                self.cart_repo.clear_cart(current_user.id)

            # Award loyalty points (10% of final order value)
            earned_points = int(final_amount * 0.1)
            current_user.loyalty_points += earned_points

            self.db.commit()
            self.db.refresh(new_order)
            return new_order
        except Exception:
            self.db.rollback()
            raise

    def get_my_orders(self, user_id: int) -> List[Order]:
        return self.order_repo.list_by_user(user_id)

    def get_order_by_id(self, current_user: User, order_id: int) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ResourceNotFoundError("Order not found")

        # User data isolation: only owner or admin can view
        if order.user_id != current_user.id and current_user.role != "admin":
            raise ForbiddenError("Not authorized to view this order")

        return order

    def update_order_status(self, order_id: int, new_status: str) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ResourceNotFoundError("Order not found")

        allowed_next = ALLOWED_STATUS_TRANSITIONS.get(order.status, set())
        if new_status not in allowed_next and new_status != order.status:
            raise BusinessRuleError(
                f"Invalid status transition from '{order.status}' to '{new_status}'. Allowed: {list(allowed_next)}"
            )

        order.status = new_status
        if new_status == OrderStatusEnum.COMPLETED.value:
            order.payment_status = PaymentStatusEnum.PAID.value

        self.db.commit()
        self.db.refresh(order)
        return order
