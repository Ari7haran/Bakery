from datetime import datetime, timezone
from typing import List, Optional
from app.repositories.coupon_repository import CouponRepository
from app.models.coupon import Coupon
from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
    ConflictError,
    ValidationError,
)
from app.schemas.coupon import (
    CouponCreate,
    CouponUpdate,
    CouponValidationResult,
)

def is_coupon_expired(expiry_date: Optional[datetime]) -> bool:
    if not expiry_date:
        return False
    now = datetime.now(timezone.utc)
    if expiry_date.tzinfo is None:
        expiry_date = expiry_date.replace(tzinfo=timezone.utc)
    return expiry_date < now

class CouponService:
    def __init__(self, coupon_repo: CouponRepository):
        self.coupon_repo = coupon_repo

    def validate_coupon(self, code: str, order_amount: float) -> CouponValidationResult:
        if order_amount < 0:
            raise ValidationError("Order amount cannot be negative")

        if not code or not code.strip():
            raise BusinessRuleError("Coupon code is required")

        clean_code = code.strip().upper()
        coupon = self.coupon_repo.get_by_code(clean_code)
        if not coupon:
            raise BusinessRuleError("Invalid or expired coupon code")

        if not coupon.is_active:
            raise BusinessRuleError("Invalid or expired coupon code")

        if is_coupon_expired(coupon.expiry_date):
            raise BusinessRuleError("Coupon has expired")

        if order_amount < coupon.min_order_amount:
            raise BusinessRuleError(f"Minimum order amount for this coupon is ₹{coupon.min_order_amount}")

        raw_discount = (order_amount * coupon.discount_percent) / 100.0
        discount = min(raw_discount, coupon.max_discount_amount)
        discount = min(discount, order_amount)
        discount = round(discount, 2)
        final_amount = max(0.0, round(order_amount - discount, 2))

        return CouponValidationResult(
            valid=True,
            code=coupon.code,
            discount_percent=coupon.discount_percent,
            discount_amount=discount,
            min_order_amount=coupon.min_order_amount,
            max_discount_amount=coupon.max_discount_amount,
            final_amount=final_amount,
            message="Coupon applied successfully"
        )

    def calculate_discount(self, code: str, order_amount: float) -> float:
        if not code or not code.strip():
            return 0.0
        res = self.validate_coupon(code.strip(), order_amount)
        return res.discount_amount

    def list_active_coupons(self) -> List[Coupon]:
        return self.coupon_repo.list_active()

    def list_all_coupons(self, skip: int = 0, limit: int = 100) -> List[Coupon]:
        return self.coupon_repo.list_all(skip=skip, limit=limit)

    def get_coupon(self, coupon_id: int) -> Coupon:
        if coupon_id <= 0:
            raise ResourceNotFoundError(f"Coupon with id {coupon_id} not found")
        coupon = self.coupon_repo.get_by_id(coupon_id)
        if not coupon:
            raise ResourceNotFoundError(f"Coupon with id {coupon_id} not found")
        return coupon

    def create_coupon(self, coupon_in: CouponCreate) -> Coupon:
        clean_code = coupon_in.code.strip().upper()
        if not clean_code:
            raise ValidationError("Coupon code cannot be empty")

        existing = self.coupon_repo.get_by_code(clean_code)
        if existing:
            raise ConflictError(f"Coupon with code '{clean_code}' already exists")

        if coupon_in.expiry_date and is_coupon_expired(coupon_in.expiry_date):
            raise ValidationError("Expiry date must be in the future")

        coupon = Coupon(
            code=clean_code,
            discount_percent=coupon_in.discount_percent,
            max_discount_amount=coupon_in.max_discount_amount,
            min_order_amount=coupon_in.min_order_amount,
            is_active=coupon_in.is_active,
            expiry_date=coupon_in.expiry_date
        )
        self.coupon_repo.add(coupon)
        return coupon

    def update_coupon(self, coupon_id: int, coupon_in: CouponUpdate) -> Coupon:
        coupon = self.get_coupon(coupon_id)

        if coupon_in.code is not None:
            new_code = coupon_in.code.strip().upper()
            if new_code != coupon.code:
                existing = self.coupon_repo.get_by_code(new_code)
                if existing:
                    raise ConflictError(f"Coupon with code '{new_code}' already exists")
                coupon.code = new_code

        if coupon_in.discount_percent is not None:
            coupon.discount_percent = coupon_in.discount_percent
        if coupon_in.max_discount_amount is not None:
            coupon.max_discount_amount = coupon_in.max_discount_amount
        if coupon_in.min_order_amount is not None:
            coupon.min_order_amount = coupon_in.min_order_amount
        if coupon_in.is_active is not None:
            coupon.is_active = coupon_in.is_active
        if coupon_in.expiry_date is not None:
            if is_coupon_expired(coupon_in.expiry_date):
                raise ValidationError("Expiry date must be in the future")
            coupon.expiry_date = coupon_in.expiry_date

        self.coupon_repo.db.commit()
        self.coupon_repo.db.refresh(coupon)
        return coupon

    def delete_coupon(self, coupon_id: int) -> None:
        coupon = self.get_coupon(coupon_id)
        self.coupon_repo.delete(coupon)
