from typing import List, Optional
from app.repositories.review_repository import ReviewRepository
from app.repositories.product_repository import ProductRepository
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewOut, ReviewUserOut
from app.core.exceptions import (
    ResourceNotFoundError,
    ForbiddenError,
    ConflictError,
    ValidationError,
)

class ReviewService:
    def __init__(self, review_repo: ReviewRepository, product_repo: ProductRepository):
        self.review_repo = review_repo
        self.product_repo = product_repo

    def get_reviews(
        self,
        product_id: int,
        sort_by: str = "newest",
        skip: int = 0,
        limit: int = 20
    ) -> List[ReviewOut]:
        if product_id <= 0:
            raise ResourceNotFoundError(f"Product with id {product_id} not found")

        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ResourceNotFoundError(f"Product with id {product_id} not found")

        reviews = self.review_repo.list_by_product(
            product_id=product_id,
            sort_by=sort_by,
            skip=skip,
            limit=limit
        )

        verified_ids = self.review_repo.get_verified_purchaser_ids(product_id)
        
        output = []
        for r in reviews:
            user_out = ReviewUserOut(id=r.user.id, full_name=r.user.full_name) if r.user else None
            output.append(ReviewOut(
                id=r.id,
                product_id=r.product_id,
                user_id=r.user_id,
                rating=r.rating,
                comment=r.comment,
                created_at=r.created_at,
                user=user_out,
                is_verified_purchase=r.user_id in verified_ids
            ))
        return output

    def add_review(
        self,
        user_id: int,
        review_in: ReviewCreate,
        product_id: Optional[int] = None
    ) -> ReviewOut:
        target_product_id = product_id if product_id is not None else review_in.product_id
        if not target_product_id or target_product_id <= 0:
            raise ResourceNotFoundError("Valid product ID is required")

        product = self.product_repo.get_by_id(target_product_id)
        if not product:
            raise ResourceNotFoundError(f"Product with id {target_product_id} not found")

        # Enforce one review per user per product
        existing = self.review_repo.get_by_user_and_product(user_id, target_product_id)
        if existing:
            raise ConflictError("You have already reviewed this product. Please update your existing review.")

        comment = (review_in.comment or "").strip()
        review = Review(
            product_id=target_product_id,
            user_id=user_id,
            rating=review_in.rating,
            comment=comment
        )
        self.review_repo.db.add(review)
        self.review_repo.db.flush()

        # Recalculate average rating & review count
        self._recalculate_aggregates(target_product_id)

        self.review_repo.db.commit()
        self.review_repo.db.refresh(review)

        verified_ids = self.review_repo.get_verified_purchaser_ids(target_product_id)
        user_out = ReviewUserOut(id=review.user.id, full_name=review.user.full_name) if review.user else None
        return ReviewOut(
            id=review.id,
            product_id=review.product_id,
            user_id=review.user_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
            user=user_out,
            is_verified_purchase=review.user_id in verified_ids
        )

    def update_review(
        self,
        review_id: int,
        user_id: int,
        review_in: ReviewUpdate,
        is_admin: bool = False
    ) -> ReviewOut:
        if review_id <= 0:
            raise ResourceNotFoundError("Review not found")

        review = self.review_repo.get_by_id(review_id)
        if not review:
            raise ResourceNotFoundError(f"Review with id {review_id} not found")

        # Verify ownership
        if review.user_id != user_id and not is_admin:
            raise ForbiddenError("You are not authorized to edit this review")

        if review_in.rating is None and review_in.comment is None:
            raise ValidationError("At least one field (rating or comment) must be provided for update")

        if review_in.rating is not None:
            review.rating = review_in.rating

        if review_in.comment is not None:
            review.comment = review_in.comment.strip()

        self.review_repo.db.flush()
        self._recalculate_aggregates(review.product_id)
        self.review_repo.db.commit()
        self.review_repo.db.refresh(review)

        verified_ids = self.review_repo.get_verified_purchaser_ids(review.product_id)
        user_out = ReviewUserOut(id=review.user.id, full_name=review.user.full_name) if review.user else None
        return ReviewOut(
            id=review.id,
            product_id=review.product_id,
            user_id=review.user_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
            user=user_out,
            is_verified_purchase=review.user_id in verified_ids
        )

    def delete_review(
        self,
        review_id: int,
        user_id: int,
        is_admin: bool = False
    ) -> None:
        if review_id <= 0:
            raise ResourceNotFoundError("Review not found")

        review = self.review_repo.get_by_id(review_id)
        if not review:
            raise ResourceNotFoundError(f"Review with id {review_id} not found")

        # Verify ownership or admin privileges
        if review.user_id != user_id and not is_admin:
            raise ForbiddenError("You are not authorized to delete this review")

        product_id = review.product_id
        self.review_repo.delete(review)
        self.review_repo.db.flush()

        self._recalculate_aggregates(product_id)
        self.review_repo.db.commit()

    def _recalculate_aggregates(self, product_id: int) -> None:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return

        all_reviews = self.review_repo.get_all_for_product(product_id)
        if all_reviews:
            count = len(all_reviews)
            avg = round(sum(r.rating for r in all_reviews) / count, 2)
            product.rating = avg
            product.review_count = count
        else:
            product.rating = 0.0
            product.review_count = 0
        self.product_repo.db.flush()
