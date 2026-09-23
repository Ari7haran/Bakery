from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.banner_repository import BannerRepository
from app.repositories.review_repository import ReviewRepository
from app.services.product_service import ProductService
from app.schemas.review import ReviewCreate, ReviewOut

router = APIRouter(tags=["Reviews"])

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(
        product_repo=ProductRepository(db),
        category_repo=CategoryRepository(db),
        banner_repo=BannerRepository(db),
        review_repo=ReviewRepository(db)
    )

@router.get("/products/{product_id}/reviews", response_model=List[ReviewOut])
def get_product_reviews(product_id: int, service: ProductService = Depends(get_product_service)):
    return service.get_reviews(product_id)

@router.post("/reviews", response_model=ReviewOut)
def create_review(
    review_in: ReviewCreate,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service)
):
    return service.add_review(current_user.id, review_in)
