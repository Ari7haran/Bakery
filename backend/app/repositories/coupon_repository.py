from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.coupon import Coupon

class CouponRepository(BaseRepository[Coupon]):
    def __init__(self, db: Session):
        super().__init__(Coupon, db)

    def get_by_code(self, code: str) -> Optional[Coupon]:
        return self.db.query(Coupon).filter(
            Coupon.code == code.upper(),
            Coupon.is_active == True
        ).first()
