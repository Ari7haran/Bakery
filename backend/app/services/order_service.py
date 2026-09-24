from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.user_repository import UserRepository
from app.services.coupon_service import CouponService
from app.services.payment_service import PaymentService
from app.core.exceptions import ResourceNotFoundError, BusinessRuleError, ForbiddenError
from app.models.order import Order, OrderItem, OrderStatusEnum, PaymentStatusEnum, OrderTypeEnum
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

        # 2. Validate order type and delivery address
        raw_order_type = (order_in.order_type or "").strip()
        valid_order_types = {
            OrderTypeEnum.TAKEAWAY.value.lower(): OrderTypeEnum.TAKEAWAY.value,
            OrderTypeEnum.DELIVERY.value.lower(): OrderTypeEnum.DELIVERY.value,
            "takeaway": OrderTypeEnum.TAKEAWAY.value,
            "delivery": OrderTypeEnum.DELIVERY.value,
        }
        matched_order_type = valid_order_types.get(raw_order_type.lower())
        if not matched_order_type:
            raise BusinessRuleError(
                f"Invalid order type: '{order_in.order_type}'. Allowed types: 'Takeaway Pickup', 'Delivery'"
            )

        if matched_order_type == OrderTypeEnum.DELIVERY.value:
            if not order_in.delivery_address or not order_in.delivery_address.strip():
                raise BusinessRuleError("Delivery address is required for Delivery orders")

        # 3. Gather and consolidate items to order
        consolidated_items: Dict[int, int] = {}
        used_db_cart = False

        if order_in.items is not None:
            if len(order_in.items) == 0:
                raise BusinessRuleError("Cannot place an order with no items")
            for item_in in order_in.items:
                if item_in.quantity <= 0:
                    raise BusinessRuleError("Item quantity must be greater than zero")
                consolidated_items[item_in.product_id] = consolidated_items.get(item_in.product_id, 0) + item_in.quantity
        else:
            db_cart = self.cart_repo.get_user_cart(current_user.id)
            if not db_cart:
                raise BusinessRuleError("Your shopping cart is empty")
            used_db_cart = True
            for c_item in db_cart:
                if c_item.quantity > 0:
                    consolidated_items[c_item.product_id] = consolidated_items.get(c_item.product_id, 0) + c_item.quantity

        if not consolidated_items:
            raise BusinessRuleError("Your shopping cart is empty")

        # 4. Validate products, stock, and calculate authoritative server-side prices
        order_items_data = []
        total_amount = 0.0

        for product_id, quantity in consolidated_items.items():
            product = self.product_repo.get_by_id(product_id)
            if not product:
                raise ResourceNotFoundError(f"Product with id {product_id} not found")

            if product.stock_quantity < quantity:
                raise BusinessRuleError(
                    f"Insufficient stock for '{product.name}'. Requested: {quantity}, Available: {product.stock_quantity}"
                )

            # Server-authoritative unit price snapshot
            raw_unit_price = product.discount_price if product.discount_price is not None else product.price
            if raw_unit_price < 0:
                raise BusinessRuleError(f"Invalid unit price for product '{product.name}'")

            unit_price = round(raw_unit_price, 2)
            total_amount += round(unit_price * quantity, 2)

            order_items_data.append({
                "product": product,
                "product_id": product.id,
                "quantity": quantity,
                "price": unit_price
            })

        total_amount = round(total_amount, 2)

        # 5. Coupon discount calculation (with validation)
        discount_amount = 0.0
        if order_in.coupon_code and order_in.coupon_code.strip():
            discount_amount = self.coupon_service.calculate_discount(order_in.coupon_code.strip(), total_amount)

        final_amount = max(0.0, round(total_amount - discount_amount, 2))

        # 6. Generate collision-free unique order number
        while True:
            order_num = generate_order_number()
            if not self.order_repo.get_by_order_number(order_num):
                break

        is_takeaway = (matched_order_type == OrderTypeEnum.TAKEAWAY.value)
        pickup_num = generate_pickup_number() if is_takeaway else None

        # 7. Prepare QR Code Payload
        qr_payload = f"ORDER:{order_num}|USER:{current_user.email}|PICKUP:{pickup_num}|AMOUNT:₹{final_amount}"

        # 8. Atomic Transaction: deduct stock, generate QR, save order, save items, award points, clear cart
        try:
            for item in order_items_data:
                item["product"].stock_quantity -= item["quantity"]

            qr_code_image = generate_qr_code(qr_payload)

            new_order = Order(
                order_number=order_num,
                user_id=current_user.id,
                total_amount=total_amount,
                discount_amount=discount_amount,
                final_amount=final_amount,
                order_type=matched_order_type,
                pickup_date=order_in.pickup_date,
                pickup_time_slot=order_in.pickup_time_slot,
                pickup_number=pickup_num,
                qr_code_data=qr_code_image,
                status=OrderStatusEnum.RECEIVED.value,
                payment_method=normalized_payment_method,
                payment_status=PaymentStatusEnum.PENDING.value,
                delivery_address=order_in.delivery_address.strip() if order_in.delivery_address else None,
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

            # Clear cart without premature commit to guarantee transaction atomicity
            if used_db_cart:
                self.cart_repo.clear_cart(current_user.id, commit=False)

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

    def cancel_order(self, current_user: User, order_id: int) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ResourceNotFoundError("Order not found")

        # Ownership authorization: only owner or admin can cancel
        if order.user_id != current_user.id and current_user.role != "admin":
            raise ForbiddenError("Not authorized to cancel this order")

        if order.status == OrderStatusEnum.CANCELLED.value:
            raise BusinessRuleError("Order is already cancelled")

        if order.status == OrderStatusEnum.COMPLETED.value:
            raise BusinessRuleError("Cannot cancel an order that has already been completed")

        # Customer cancellation is permitted only while order is in Received or Preparing state
        if current_user.role != "admin" and order.status not in {OrderStatusEnum.RECEIVED.value, OrderStatusEnum.PREPARING.value}:
            raise BusinessRuleError(f"Cannot cancel order in '{order.status}' status. Baking has already started.")

        return self._execute_cancellation(order)

    def _execute_cancellation(self, order: Order) -> Order:
        try:
            # 1. Restore product inventory
            for item in order.items:
                product = self.product_repo.get_by_id(item.product_id)
                if product:
                    product.stock_quantity += item.quantity

            # 2. Reclaim awarded loyalty points (do not drop below 0)
            if order.user:
                earned_points = int(order.final_amount * 0.1)
                order.user.loyalty_points = max(0, order.user.loyalty_points - earned_points)

            # 3. Update order and payment status
            order.status = OrderStatusEnum.CANCELLED.value
            if order.payment_status != PaymentStatusEnum.PAID.value:
                order.payment_status = PaymentStatusEnum.FAILED.value

            self.db.commit()
            self.db.refresh(order)
            return order
        except Exception:
            self.db.rollback()
            raise

    def update_order_status(self, order_id: int, new_status: str) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ResourceNotFoundError("Order not found")

        allowed_next = ALLOWED_STATUS_TRANSITIONS.get(order.status, set())
        if new_status not in allowed_next and new_status != order.status:
            raise BusinessRuleError(
                f"Invalid status transition from '{order.status}' to '{new_status}'. Allowed: {list(allowed_next)}"
            )

        # Transitioning to Cancelled restores stock and adjusts loyalty points
        if new_status == OrderStatusEnum.CANCELLED.value and order.status != OrderStatusEnum.CANCELLED.value:
            return self._execute_cancellation(order)

        order.status = new_status
        if new_status == OrderStatusEnum.COMPLETED.value:
            order.payment_status = PaymentStatusEnum.PAID.value

        self.db.commit()
        self.db.refresh(order)
        return order
