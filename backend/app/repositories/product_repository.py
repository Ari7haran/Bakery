from typing import Optional, List
from sqlalchemy import func, or_, and_, case
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.product import Product
from app.models.category import Category
from app.models.order import OrderItem

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
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        is_veg: Optional[bool] = None,
        is_featured: Optional[bool] = None,
        is_todays_fresh: Optional[bool] = None,
        is_popular: Optional[bool] = None,
        in_stock: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = "popular",
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> List[Product]:
        query = self.db.query(Product)
        joined_category = False

        if category_slug and category_slug != "all":
            query = query.join(Category, Product.category_id == Category.id)
            query = query.filter(Category.slug == category_slug)
            joined_category = True

        if category_id is not None:
            query = query.filter(Product.category_id == category_id)

        clean_search = search.strip() if search else None
        if clean_search:
            if not joined_category:
                query = query.outerjoin(Category, Product.category_id == Category.id)
                joined_category = True

            pattern = f"%{clean_search}%"
            words = clean_search.split()
            if len(words) > 1:
                word_conditions = [
                    (
                        Product.name.ilike(f"%{w}%")
                        | Product.description.ilike(f"%{w}%")
                        | Category.name.ilike(f"%{w}%")
                    )
                    for w in words
                ]
                query = query.filter(
                    or_(
                        Product.name.ilike(pattern),
                        Product.description.ilike(pattern),
                        Category.name.ilike(pattern),
                        and_(*word_conditions)
                    )
                )
            else:
                query = query.filter(
                    Product.name.ilike(pattern)
                    | Product.description.ilike(pattern)
                    | Category.name.ilike(pattern)
                )

        if in_stock is True:
            query = query.filter(Product.stock_quantity > 0)
        elif in_stock is False:
            query = query.filter(Product.stock_quantity == 0)

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

        # Deterministic sorting
        if sort_by == "price_asc":
            query = query.order_by(Product.price.asc(), Product.id.asc())
        elif sort_by == "price_desc":
            query = query.order_by(Product.price.desc(), Product.id.asc())
        elif sort_by == "name_asc":
            query = query.order_by(Product.name.asc(), Product.id.asc())
        elif sort_by == "name_desc":
            query = query.order_by(Product.name.desc(), Product.id.asc())
        elif sort_by == "rating":
            query = query.order_by(Product.rating.desc(), Product.review_count.desc(), Product.id.asc())
        elif sort_by == "newest":
            query = query.order_by(Product.created_at.desc(), Product.id.asc())
        else:  # default "popular"
            if clean_search:
                pattern = f"%{clean_search}%"
                relevance = case(
                    (func.lower(Product.name) == clean_search.lower(), 1),
                    (func.lower(Product.name).like(f"{clean_search.lower()}%"), 2),
                    (Product.name.ilike(pattern), 3),
                    (Category.name.ilike(pattern), 4),
                    else_=5
                )
                query = query.order_by(
                    relevance.asc(),
                    Product.is_popular.desc(),
                    Product.rating.desc(),
                    Product.review_count.desc(),
                    Product.id.asc()
                )
            else:
                query = query.order_by(
                    Product.is_popular.desc(),
                    Product.review_count.desc(),
                    Product.rating.desc(),
                    Product.id.asc()
                )

        if skip > 0:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def get_frequently_bought_together(self, product_id: int, limit: int = 4) -> List[Product]:
        """Find products ordered together with product_id in completed/existing orders."""
        order_ids = (
            self.db.query(OrderItem.order_id)
            .filter(OrderItem.product_id == product_id)
            .distinct()
        )
        co_products = (
            self.db.query(Product)
            .join(OrderItem, OrderItem.product_id == Product.id)
            .filter(
                OrderItem.order_id.in_(order_ids),
                Product.id != product_id
            )
            .group_by(Product.id)
            .order_by(
                (Product.stock_quantity > 0).desc(),
                func.count(OrderItem.id).desc(),
                Product.rating.desc(),
                Product.review_count.desc()
            )
            .limit(limit)
            .all()
        )
        return co_products

    def get_category_recommendations(self, category_id: int, exclude_product_id: int, limit: int = 4) -> List[Product]:
        """Find complementary products in the same category."""
        return (
            self.db.query(Product)
            .filter(
                Product.category_id == category_id,
                Product.id != exclude_product_id
            )
            .order_by(
                (Product.stock_quantity > 0).desc(),
                Product.is_popular.desc(),
                Product.rating.desc(),
                Product.review_count.desc()
            )
            .limit(limit)
            .all()
        )

    def get_popular_recommendations(self, exclude_ids: List[int], limit: int = 4) -> List[Product]:
        """Find top popular/rated products excluding specified IDs."""
        query = self.db.query(Product)
        if exclude_ids:
            query = query.filter(~Product.id.in_(exclude_ids))
        return (
            query.order_by(
                (Product.stock_quantity > 0).desc(),
                Product.is_popular.desc(),
                Product.rating.desc(),
                Product.review_count.desc()
            )
            .limit(limit)
            .all()
        )

    def get_recommendations(self, product_id: int, limit: int = 4) -> List[Product]:
        target = self.get_by_id(product_id)
        if not target:
            return []

        recommended: List[Product] = []
        seen_ids = {product_id}

        # 1. Frequently bought together
        for p in self.get_frequently_bought_together(product_id, limit=limit):
            if p.id not in seen_ids:
                recommended.append(p)
                seen_ids.add(p.id)
                if len(recommended) >= limit:
                    return recommended

        # 2. Same category complements
        for p in self.get_category_recommendations(target.category_id, product_id, limit=limit):
            if p.id not in seen_ids:
                recommended.append(p)
                seen_ids.add(p.id)
                if len(recommended) >= limit:
                    return recommended

        # 3. Popular catalog items fallback
        remaining = limit - len(recommended)
        if remaining > 0:
            for p in self.get_popular_recommendations(list(seen_ids), limit=remaining):
                if p.id not in seen_ids:
                    recommended.append(p)
                    seen_ids.add(p.id)
                    if len(recommended) >= limit:
                        break

        return recommended

    def deduct_stock(self, product: Product, quantity: int) -> Product:
        product.stock_quantity -= quantity
        self.db.commit()
        self.db.refresh(product)
        return product
