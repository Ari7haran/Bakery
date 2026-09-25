from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.product_repository import ProductRepository
from app.repositories.review_repository import ReviewRepository
from app.services.review_service import ReviewService
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewOut,
    ReviewSortOption,
)

router = APIRouter(tags=["Reviews"])

def get_review_service(db: Session = Depends(get_db)) -> ReviewService:
    return ReviewService(
        review_repo=ReviewRepository(db),
        product_repo=ProductRepository(db),
    )

@router.get("/products/{product_id}/reviews", response_model=List[ReviewOut])
def get_product_reviews(
    product_id: int = Path(..., gt=0, description="Product ID must be greater than zero"),
    sort_by: Optional[ReviewSortOption] = Query(ReviewSortOption.newest, description="Sort order for reviews"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum items to return"),
    service: ReviewService = Depends(get_review_service)
):
    sort_val = sort_by.value if isinstance(sort_by, ReviewSortOption) else (sort_by or "newest")
    return service.get_reviews(
        product_id=product_id,
        sort_by=sort_val,
        skip=skip,
        limit=limit
    )

@router.post("/products/{product_id}/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_product_review(
    product_id: int = Path(..., gt=0, description="Product ID must be greater than zero"),
    review_in: ReviewCreate = ...,
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service)
):
    return service.add_review(
        user_id=current_user.id,
        review_in=review_in,
        product_id=product_id
    )

@router.post("/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    review_in: ReviewCreate,
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service)
):
    return service.add_review(
        user_id=current_user.id,
        review_in=review_in,
        product_id=review_in.product_id
    )

@router.put("/reviews/{review_id}", response_model=ReviewOut)
def update_review(
    review_id: int = Path(..., gt=0, description="Review ID must be greater than zero"),
    review_in: ReviewUpdate = ...,
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service)
):
    is_admin = current_user.role == "admin"
    return service.update_review(
        review_id=review_id,
        user_id=current_user.id,
        review_in=review_in,
        is_admin=is_admin
    )

@router.delete("/reviews/{review_id}")
def delete_review(
    review_id: int = Path(..., gt=0, description="Review ID must be greater than zero"),
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service)
):
    is_admin = current_user.role == "admin"
    service.delete_review(
        review_id=review_id,
        user_id=current_user.id,
        is_admin=is_admin
    )
    return {"message": "Review deleted successfully"}
