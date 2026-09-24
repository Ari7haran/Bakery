from typing import List, Optional
from enum import Enum
from fastapi import APIRouter, Depends, Query, Path
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

class ProductSortOption(str, Enum):
    popular = "popular"
    price_asc = "price_asc"
    price_desc = "price_desc"
    name_asc = "name_asc"
    name_desc = "name_desc"
    rating = "rating"
    newest = "newest"

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
    category_slug: Optional[str] = Query(None, description="Filter by category slug"),
    category_id: Optional[int] = Query(None, gt=0, description="Filter by category ID (must be > 0)"),
    search: Optional[str] = Query(None, max_length=100, description="Search term for name, description, or category"),
    q: Optional[str] = Query(None, max_length=100, description="Search term alias"),
    is_veg: Optional[bool] = Query(None, description="Filter vegetarian products"),
    is_featured: Optional[bool] = Query(None, description="Filter featured products"),
    is_todays_fresh: Optional[bool] = Query(None, description="Filter today's fresh products"),
    is_popular: Optional[bool] = Query(None, description="Filter popular products"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability (True = in stock, False = out of stock)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price (must be >= 0)"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price (must be >= 0)"),
    sort_by: Optional[ProductSortOption] = Query(ProductSortOption.popular, description="Sort order for products"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: Optional[int] = Query(100, ge=1, le=100, description="Maximum items to return"),
    service: ProductService = Depends(get_product_service)
):
    effective_search = search if search is not None else q
    sort_val = sort_by.value if isinstance(sort_by, ProductSortOption) else (sort_by or "popular")
    return service.list_products(
        category_slug=category_slug,
        category_id=category_id,
        search=effective_search,
        is_veg=is_veg,
        is_featured=is_featured,
        is_todays_fresh=is_todays_fresh,
        is_popular=is_popular,
        in_stock=in_stock,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_val,
        skip=skip,
        limit=limit,
    )

@router.get("/products/recommendations/{product_id}", response_model=List[ProductOut])
def get_ai_recommendations(
    product_id: int = Path(..., gt=0, description="Product ID must be greater than zero"),
    limit: int = Query(4, ge=1, le=20, description="Number of recommendations to return"),
    service: ProductService = Depends(get_product_service)
):
    return service.get_recommendations(product_id, limit=limit)

@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, service: ProductService = Depends(get_product_service)):
    return service.get_product(product_id)

@router.get("/banners", response_model=List[BannerOut])
def get_banners(service: ProductService = Depends(get_product_service)):
    return service.get_banners()
