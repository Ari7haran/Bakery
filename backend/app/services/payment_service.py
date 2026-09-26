from typing import Optional
from app.core.exceptions import BusinessRuleError, ResourceNotFoundError
from app.models.order import Order, PaymentStatusEnum, PaymentMethodEnum
from app.repositories.order_repository import OrderRepository
from app.services.notification_service import NotificationService

# Allowed cash payment representations
ALLOWED_PAYMENT_METHODS = {
    PaymentMethodEnum.CASH.value.upper(),
    PaymentMethodEnum.CASH_ON_PICKUP.value.upper(),
    PaymentMethodEnum.CASH_ON_DELIVERY.value.upper(),
    "CASH",
    "CASH ON PICKUP",
    "CASH ON DELIVERY",
}

class PaymentService:
    def __init__(self, order_repo: OrderRepository, notification_service: Optional[NotificationService] = None):
        self.order_repo = order_repo
        self.notification_service = notification_service

    def validate_payment_method(self, payment_method: str) -> str:
        """
        Validates that the payment method is CASH only.
        Rejects online payments (Card, Stripe, UPI, Online Payment) with 400 Bad Request.
        """
        if not payment_method:
            return PaymentMethodEnum.CASH_ON_PICKUP.value

        normalized = payment_method.strip().upper()

        if normalized in {"ONLINE PAYMENT", "CARD", "STRIPE", "RAZORPAY", "UPI", "CREDIT CARD", "DEBIT CARD"}:
            raise BusinessRuleError(
                "Online payment methods are disabled. Sweet Crumbs Bakery currently accepts CASH ONLY (Cash on Pickup / Cash on Delivery)."
            )

        if normalized not in ALLOWED_PAYMENT_METHODS:
            raise BusinessRuleError(
                f"Unsupported payment method: '{payment_method}'. Allowed methods: 'Cash on Pickup', 'Cash on Delivery', 'CASH'."
            )

        # Standardize return label
        if "DELIVERY" in normalized:
            return PaymentMethodEnum.CASH_ON_DELIVERY.value
        return PaymentMethodEnum.CASH_ON_PICKUP.value

    def get_initial_payment_status(self) -> str:
        """Backend strictly sets initial payment status to Pending."""
        return PaymentStatusEnum.PENDING.value

    def mark_payment_paid(self, order_id: int) -> Order:
        """
        Authorized staff/admin endpoint to mark an order payment as PAID.
        """
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ResourceNotFoundError("Order not found")

        if order.payment_status == PaymentStatusEnum.PAID.value:
            return order

        updated_order = self.order_repo.update_payment_status(order, PaymentStatusEnum.PAID.value)
        if self.notification_service:
            self.notification_service.notify_payment_reconciled(updated_order, commit=True)
        return updated_order
