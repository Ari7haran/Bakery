import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError, ValidationError
from app.models.notification import Notification, NotificationTypeEnum, NotificationPriorityEnum
from app.models.user import User, RoleEnum
from app.models.order import Order
from app.models.product import Product
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(
        self,
        notification_repo: NotificationRepository,
        user_repo: Optional[UserRepository] = None,
        db: Optional[Session] = None
    ):
        self.notification_repo = notification_repo
        self.user_repo = user_repo
        self.db = db

    def get_user_notifications(
        self,
        current_user: User,
        is_read: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        if skip < 0:
            raise ValidationError("skip cannot be negative")
        if limit < 1 or limit > 100:
            raise ValidationError("limit must be between 1 and 100")

        items = self.notification_repo.list_by_user(
            user_id=current_user.id,
            is_read=is_read,
            skip=skip,
            limit=limit
        )
        total = self.notification_repo.count_by_user(
            user_id=current_user.id,
            is_read=is_read
        )
        unread_count = self.notification_repo.count_unread_by_user(current_user.id)

        return {
            "items": items,
            "total": total,
            "unread_count": unread_count,
            "skip": skip,
            "limit": limit
        }

    def get_unread_count(self, current_user: User) -> int:
        return self.notification_repo.count_unread_by_user(current_user.id)

    def mark_notification_read(self, current_user: User, notification_id: int) -> Notification:
        if notification_id <= 0:
            raise ResourceNotFoundError("Notification not found")
        notification = self.notification_repo.mark_as_read(current_user.id, notification_id)
        if not notification:
            # IDOR protection: return 404 whether notification does not exist or belongs to another user
            raise ResourceNotFoundError("Notification not found")
        return notification

    def mark_all_read(self, current_user: User) -> int:
        return self.notification_repo.mark_all_read(current_user.id)

    def delete_notification(self, current_user: User, notification_id: int) -> None:
        if notification_id <= 0:
            raise ResourceNotFoundError("Notification not found")
        success = self.notification_repo.delete_user_notification(current_user.id, notification_id)
        if not success:
            # IDOR protection: return 404 whether notification does not exist or belongs to another user
            raise ResourceNotFoundError("Notification not found")

    # -------------------------------------------------------------
    # Business Event Dispatchers
    # -------------------------------------------------------------

    def notify_order_created(self, order: Order, commit: bool = False) -> None:
        """
        Dispatches order confirmation notification to the customer,
        and an alert to all active admin staff.
        """
        try:
            # 1. Customer notification
            if order.user_id:
                if order.order_type == "Takeaway Pickup":
                    slot_info = f"on {order.pickup_date} ({order.pickup_time_slot or 'Express'})"
                    msg = (
                        f"Your takeaway order has been confirmed! Scheduled for pickup {slot_info}. "
                        f"Express Counter Pickup #{order.pickup_number}."
                    )
                else:
                    dest = order.delivery_address or "your doorstep"
                    msg = f"Your delivery order has been confirmed! Warm delicacies will be dispatched to {dest}."

                self.notification_repo.create_notification(
                    user_id=order.user_id,
                    title=f"Order #{order.order_number} Confirmed! 🥐",
                    message=msg,
                    notification_type=NotificationTypeEnum.ORDER_CREATED.value,
                    priority=NotificationPriorityEnum.NORMAL.value,
                    link_url=f"/track?orderId={order.id}",
                    related_entity_type="order",
                    related_entity_id=order.id,
                    commit=commit
                )

            # 2. Admin notification (to all active admins)
            if self.user_repo:
                admins = self.user_repo.get_admins()
                for admin in admins:
                    # Do not duplicate if admin is the one who placed the order
                    if admin.id != order.user_id:
                        self.notification_repo.create_notification(
                            user_id=admin.id,
                            title=f"New {order.order_type} Order #{order.order_number}",
                            message=(
                                f"New order received for ₹{order.final_amount:.2f}. "
                                f"Fulfillment: {order.order_type}. Payment: {order.payment_method}."
                            ),
                            notification_type=NotificationTypeEnum.ORDER_CREATED.value,
                            priority=NotificationPriorityEnum.HIGH.value,
                            link_url="/admin",
                            related_entity_type="order",
                            related_entity_id=order.id,
                            commit=commit
                        )
        except Exception as e:
            logger.warning(f"Failed to generate order creation notification for order {order.id}: {e}")

    def notify_order_status_update(self, order: Order, old_status: str, new_status: str, commit: bool = False) -> None:
        """
        Dispatches order status transition notification to the customer.
        Special emphasis on 'Ready for Pickup' and 'Cancelled'.
        """
        if not order.user_id or old_status == new_status:
            return

        try:
            status_map = {
                "Preparing": (
                    f"Order #{order.order_number} - Dough Prep Started 🥣",
                    "Our master bakers have started crafting your artisanal bakery treats!",
                    NotificationPriorityEnum.NORMAL.value,
                    NotificationTypeEnum.ORDER_STATUS.value
                ),
                "Baking": (
                    f"Order #{order.order_number} - In Stone Oven 🔥",
                    "Your treats are baking to golden, crispy perfection right now in our ovens!",
                    NotificationPriorityEnum.NORMAL.value,
                    NotificationTypeEnum.ORDER_STATUS.value
                ),
                "Packing": (
                    f"Order #{order.order_number} - Warm Packing 🛍️",
                    "Your order is being carefully packed warm in eco-friendly bakery boxes.",
                    NotificationPriorityEnum.NORMAL.value,
                    NotificationTypeEnum.ORDER_STATUS.value
                ),
                "Ready for Pickup": (
                    f"Order #{order.order_number} is Ready for Counter Pickup! ✨",
                    (
                        f"Your warm order is fresh & waiting at our express counter! "
                        f"Present pickup number #{order.pickup_number} or your QR code to collect."
                    ),
                    NotificationPriorityEnum.URGENT.value,
                    NotificationTypeEnum.ORDER_STATUS.value
                ),
                "Completed": (
                    f"Order #{order.order_number} Completed! 🎉",
                    "Your order has been collected. Thank you for visiting Sweet Crumbs Bakery!",
                    NotificationPriorityEnum.NORMAL.value,
                    NotificationTypeEnum.ORDER_STATUS.value
                ),
                "Cancelled": (
                    f"Order #{order.order_number} Cancelled",
                    "Your bakery order has been cancelled. Any deducted stock or points have been restored.",
                    NotificationPriorityEnum.HIGH.value,
                    NotificationTypeEnum.ORDER_CANCELLED.value
                ),
            }

            info = status_map.get(new_status)
            if not info:
                title = f"Order #{order.order_number} Status Updated"
                msg = f"Your order status has changed to: {new_status}."
                priority = NotificationPriorityEnum.NORMAL.value
                ntype = NotificationTypeEnum.ORDER_STATUS.value
            else:
                title, msg, priority, ntype = info

            self.notification_repo.create_notification(
                user_id=order.user_id,
                title=title,
                message=msg,
                notification_type=ntype,
                priority=priority,
                link_url=f"/track?orderId={order.id}",
                related_entity_type="order",
                related_entity_id=order.id,
                commit=commit
            )
        except Exception as e:
            logger.warning(f"Failed to generate status update notification for order {order.id}: {e}")

    def notify_order_cancelled(self, order: Order, commit: bool = False) -> None:
        """Dispatches cancellation notice to customer."""
        self.notify_order_status_update(order, order.status, "Cancelled", commit=commit)

    def notify_payment_reconciled(self, order: Order, commit: bool = False) -> None:
        """Dispatches cash payment received confirmation to the customer."""
        if not order.user_id:
            return

        try:
            self.notification_repo.create_notification(
                user_id=order.user_id,
                title=f"Payment Received for Order #{order.order_number} 💳",
                message=(
                    f"Your cash payment of ₹{order.final_amount:.2f} via {order.payment_method} "
                    f"has been verified and marked as Paid."
                ),
                notification_type=NotificationTypeEnum.PAYMENT.value,
                priority=NotificationPriorityEnum.NORMAL.value,
                link_url=f"/track?orderId={order.id}",
                related_entity_type="order",
                related_entity_id=order.id,
                commit=commit
            )
        except Exception as e:
            logger.warning(f"Failed to generate payment notification for order {order.id}: {e}")

    def notify_low_stock(self, product: Product, threshold: int = 5, commit: bool = False) -> None:
        """
        Dispatches low-stock or out-of-stock warning to all active administrators.
        """
        if not self.user_repo:
            return

        try:
            admins = self.user_repo.get_admins()
            if not admins:
                return

            if product.stock_quantity == 0:
                title = f"Out of Stock Alert: {product.name} 🚨"
                message = f"Product '{product.name}' is completely out of stock! Needs immediate restocking."
                priority = NotificationPriorityEnum.URGENT.value
            else:
                title = f"Low Stock Alert: {product.name} ⚠️"
                message = f"Product '{product.name}' inventory is low ({product.stock_quantity} remaining, threshold: {threshold})."
                priority = NotificationPriorityEnum.HIGH.value

            for admin in admins:
                self.notification_repo.create_notification(
                    user_id=admin.id,
                    title=title,
                    message=message,
                    notification_type=NotificationTypeEnum.INVENTORY.value,
                    priority=priority,
                    link_url="/admin",
                    related_entity_type="product",
                    related_entity_id=product.id,
                    commit=commit
                )
        except Exception as e:
            logger.warning(f"Failed to generate low stock notification for product {product.id}: {e}")
