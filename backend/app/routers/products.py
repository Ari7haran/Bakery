from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.all_models import Product, Category, Review, Banner
from app.schemas.schemas import ProductOut, ProductBase, CategoryOut

router = APIRouter(tags=["Products & Categories"])

@router.get("/categories", response_model=List[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

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
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if category_slug and category_slug != "all":
        query = query.join(Category).filter(Category.slug == category_slug)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(Product.name.ilike(search_pattern) | Product.description.ilike(search_pattern))
    
    if is_veg is not None:
        query = query.filter(Product.is_veg == is_veg)

    if is_featured is not None:
        query = query.filter(Product.is_featured == is_featured)

    if is_todays_fresh is not None:
        query = query.filter(Product.is_todays_fresh == is_todays_fresh)

    if is_popular is not None:
        query = query.filter(Product.is_popular == is_popular)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "rating":
        query = query.order_by(Product.rating.desc())
    elif sort_by == "newest":
        query = query.order_by(Product.created_at.desc())
    else: # popular default
        query = query.order_by(Product.review_count.desc(), Product.rating.desc())

    return query.all()

@router.get("/products/recommendations/{product_id}", response_model=List[ProductOut])
def get_ai_recommendations(product_id: int, db: Session = Depends(get_db)):
    target_product = db.query(Product).filter(Product.id == product_id).first()
    if not target_product:
        return db.query(Product).limit(4).all()
    
    # Smart recommendation: products in same category or complimentary snacks/beverages
    related = db.query(Product).filter(
        Product.id != product_id,
        (Product.category_id == target_product.category_id) | (Product.is_popular == True)
    ).limit(4).all()
    
    return related

@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/banners")
def get_banners(db: Session = Depends(get_db)):
    return db.query(Banner).filter(Banner.is_active == True).all()
