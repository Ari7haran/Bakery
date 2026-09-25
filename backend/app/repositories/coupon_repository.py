from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.coupon import Coupon

class CouponRepository(BaseRepository[Coupon]):
    def __init__(self, db: Session):
        super().__init__(Coupon, db)

    def get_by_code(self, code: str) -> Optional[Coupon]:
        clean = code.strip().upper()
        return self.db.query(Coupon).filter(Coupon.code == clean).first()

    def get_active_by_code(self, code: str) -> Optional[Coupon]:
        clean = code.strip().upper()
        return self.db.query(Coupon).filter(
            Coupon.code == clean,
            Coupon.is_active == True
        ).first()

    def list_active(self) -> List[Coupon]:
        now = datetime.now(timezone.utc)
        return (
            self.db.query(Coupon)
            .filter(
                Coupon.is_active == True,
                (Coupon.expiry_date.is_(None) | (Coupon.expiry_date >= now))
            )
            .order_by(Coupon.discount_percent.desc())
            .all()
        )

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Coupon]:
        return (
            self.db.query(Coupon)
            .order_by(Coupon.id.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_all(self) -> int:
        return self.db.query(Coupon).count()
