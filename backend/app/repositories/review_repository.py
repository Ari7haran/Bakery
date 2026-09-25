from typing import List, Optional, Set
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.review import Review
from app.models.order import Order, OrderItem

class ReviewRepository(BaseRepository[Review]):
    def __init__(self, db: Session):
        super().__init__(Review, db)

    def list_by_product(
        self,
        product_id: int,
        sort_by: str = "newest",
        skip: int = 0,
        limit: int = 20
    ) -> List[Review]:
        query = self.db.query(Review).filter(Review.product_id == product_id)
        
        if sort_by == "oldest":
            query = query.order_by(Review.created_at.asc())
        elif sort_by == "highest_rating":
            query = query.order_by(Review.rating.desc(), Review.created_at.desc())
        elif sort_by == "lowest_rating":
            query = query.order_by(Review.rating.asc(), Review.created_at.desc())
        else:  # newest by default
            query = query.order_by(Review.created_at.desc())
            
        return query.offset(skip).limit(limit).all()

    def get_all_for_product(self, product_id: int) -> List[Review]:
        return (
            self.db.query(Review)
            .filter(Review.product_id == product_id)
            .all()
        )

    def get_by_user_and_product(self, user_id: int, product_id: int) -> Optional[Review]:
        return (
            self.db.query(Review)
            .filter(Review.user_id == user_id, Review.product_id == product_id)
            .first()
        )

    def count_by_product(self, product_id: int) -> int:
        return self.db.query(Review).filter(Review.product_id == product_id).count()

    def get_verified_purchaser_ids(self, product_id: int) -> Set[int]:
        results = (
            self.db.query(Order.user_id)
            .join(OrderItem, OrderItem.order_id == Order.id)
            .filter(
                OrderItem.product_id == product_id,
                Order.status != "Cancelled"
            )
            .all()
        )
        return {r[0] for r in results if r[0] is not None}
