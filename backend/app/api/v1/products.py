from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.banner_repository import BannerRepository
from app.repositories.review_repository import ReviewRepository
from app.services.product_service import ProductService
from app.schemas.product import ProductOut
from app.schemas.category import CategoryOut
from app.schemas.banner import BannerOut

router = APIRouter(tags=["Products & Categories"])

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(
        product_repo=ProductRepository(db),
        category_repo=CategoryRepository(db),
        banner_repo=BannerRepository(db),
        review_repo=ReviewRepository(db)
    )

@router.get("/categories", response_model=List[CategoryOut])
def get_categories(service: ProductService = Depends(get_product_service)):
    return service.list_categories()

@router.get("/products", response_model=List[ProductOut])
def get_products(
    category_slug: Optional[str] = None,
    search: Optional[str] = None,
    is_veg: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    is_todays_fresh: Optional[bool] = None,
    is_popular: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query("popular", enum=["popular", "price_asc", "price_desc", "rating", "newest"]),
    service: ProductService = Depends(get_product_service)
):
    return service.list_products(
        category_slug=category_slug,
        search=search,
        is_veg=is_veg,
        is_featured=is_featured,
        is_todays_fresh=is_todays_fresh,
        is_popular=is_popular,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by
    )

@router.get("/products/recommendations/{product_id}", response_model=List[ProductOut])
def get_ai_recommendations(product_id: int, service: ProductService = Depends(get_product_service)):
    return service.get_recommendations(product_id)

@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, service: ProductService = Depends(get_product_service)):
    return service.get_product(product_id)

@router.get("/banners", response_model=List[BannerOut])
def get_banners(service: ProductService = Depends(get_product_service)):
    return service.get_banners()
