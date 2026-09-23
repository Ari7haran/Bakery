from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.product import Product
from app.models.category import Category

class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(Product, db)

    def get_by_slug(self, slug: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.slug == slug).first()

    def get_by_ids(self, ids: List[int]) -> List[Product]:
        return self.db.query(Product).filter(Product.id.in_(ids)).all()

    def list_products(
        self,
        category_slug: Optional[str] = None,
        search: Optional[str] = None,
        is_veg: Optional[bool] = None,
        is_featured: Optional[bool] = None,
        is_todays_fresh: Optional[bool] = None,
        is_popular: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = "popular",
    ) -> List[Product]:
        query = self.db.query(Product)

        if category_slug and category_slug != "all":
            query = query.join(Category).filter(Category.slug == category_slug)

        if search:
            pattern = f"%{search}%"
            query = query.filter(Product.name.ilike(pattern) | Product.description.ilike(pattern))

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
        else:  # default popular
            query = query.order_by(Product.review_count.desc(), Product.rating.desc())

        return query.all()

    def get_recommendations(self, product_id: int, limit: int = 4) -> List[Product]:
        target = self.get_by_id(product_id)
        if not target:
            return self.db.query(Product).limit(limit).all()

        return self.db.query(Product).filter(
            Product.id != product_id,
            (Product.category_id == target.category_id) | (Product.is_popular == True)
        ).limit(limit).all()

    def deduct_stock(self, product: Product, quantity: int) -> Product:
        product.stock_quantity -= quantity
        self.db.commit()
        self.db.refresh(product)
        return product
