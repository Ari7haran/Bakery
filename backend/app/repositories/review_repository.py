from typing import List
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.review import Review

class ReviewRepository(BaseRepository[Review]):
    def __init__(self, db: Session):
        super().__init__(Review, db)

    def list_by_product(self, product_id: int) -> List[Review]:
        return (
            self.db.query(Review)
            .filter(Review.product_id == product_id)
            .order_by(Review.created_at.desc())
            .all()
        )
