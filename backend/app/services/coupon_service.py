from datetime import datetime, timezone
from typing import Tuple
from app.repositories.coupon_repository import CouponRepository
from app.core.exceptions import BusinessRuleError, ResourceNotFoundError
from app.schemas.coupon import CouponValidationResult

class CouponService:
    def __init__(self, coupon_repo: CouponRepository):
        self.coupon_repo = coupon_repo

    def validate_coupon(self, code: str, order_amount: float) -> CouponValidationResult:
        coupon = self.coupon_repo.get_by_code(code)
        if not coupon:
            raise BusinessRuleError("Invalid or expired coupon code")

        if coupon.expiry_date and coupon.expiry_date < datetime.now(timezone.utc):
            raise BusinessRuleError("Coupon has expired")

        if order_amount < coupon.min_order_amount:
            raise BusinessRuleError(f"Minimum order amount for this coupon is ₹{coupon.min_order_amount}")

        discount = (order_amount * coupon.discount_percent) / 100.0
        discount = min(discount, coupon.max_discount_amount)

        return CouponValidationResult(
            valid=True,
            code=coupon.code,
            discount_percent=coupon.discount_percent,
            discount_amount=round(discount, 2)
        )

    def calculate_discount(self, code: str, order_amount: float) -> float:
        if not code or not code.strip():
            return 0.0
        res = self.validate_coupon(code.strip(), order_amount)
        return res.discount_amount
