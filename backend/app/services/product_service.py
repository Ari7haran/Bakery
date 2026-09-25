from typing import List, Optional
from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.banner_repository import BannerRepository
from app.repositories.review_repository import ReviewRepository
from app.core.exceptions import ResourceNotFoundError, BusinessRuleError, ValidationError, ConflictError
from app.models.product import Product
from app.models.category import Category
from app.models.banner import Banner
from app.models.review import Review
from app.schemas.product import ProductBase
from app.schemas.review import ReviewCreate

class ProductService:
    def __init__(
        self,
        product_repo: ProductRepository,
        category_repo: CategoryRepository,
        banner_repo: BannerRepository,
        review_repo: ReviewRepository
    ):
        self.product_repo = product_repo
        self.category_repo = category_repo
        self.banner_repo = banner_repo
        self.review_repo = review_repo

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
        if min_price is not None and min_price < 0:
            raise ValidationError("min_price cannot be negative")
        if max_price is not None and max_price < 0:
            raise ValidationError("max_price cannot be negative")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValidationError("min_price cannot be greater than max_price")
        if skip < 0:
            raise ValidationError("skip cannot be negative")
        if limit is not None and limit < 1:
            raise ValidationError("limit must be greater than zero")

        clean_search = search.strip() if search else None
        if not clean_search:
            clean_search = None

        return self.product_repo.list_products(
            category_slug=category_slug,
            category_id=category_id,
            search=clean_search,
            is_veg=is_veg,
            is_featured=is_featured,
            is_todays_fresh=is_todays_fresh,
            is_popular=is_popular,
            in_stock=in_stock,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            skip=skip,
            limit=limit,
        )

    def get_product(self, product_id: int) -> Product:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ResourceNotFoundError(f"Product with id {product_id} not found")
        return product

    def get_recommendations(self, product_id: int, limit: int = 4) -> List[Product]:
        target = self.product_repo.get_by_id(product_id)
        if not target:
            raise ResourceNotFoundError(f"Product with id {product_id} not found")

        if limit <= 0:
            return []

        return self.product_repo.get_recommendations(product_id, limit=limit)

    def list_categories(self) -> List[Category]:
        return self.category_repo.list_all()

    def get_banners(self) -> List[Banner]:
        return self.banner_repo.list_active()

    def create_product(self, product_in: ProductBase) -> Product:
        if product_in.stock_quantity < 0:
            raise BusinessRuleError("Stock quantity cannot be negative")
        if product_in.price < 0:
            raise BusinessRuleError("Price cannot be negative")
        if product_in.discount_price is not None and product_in.discount_price < 0:
            raise BusinessRuleError("Discount price cannot be negative")

        category = self.category_repo.get_by_id(product_in.category_id)
        if not category:
            raise BusinessRuleError(f"Category with id {product_in.category_id} not found")

        existing_slug = self.product_repo.get_by_slug(product_in.slug)
        if existing_slug:
            raise BusinessRuleError(f"Product slug '{product_in.slug}' already exists")

        product = Product(**product_in.model_dump())
        return self.product_repo.add(product)

    def update_product(self, product_id: int, product_in: ProductBase) -> Product:
        if product_in.stock_quantity < 0:
            raise BusinessRuleError("Stock quantity cannot be negative")
        if product_in.price < 0:
            raise BusinessRuleError("Price cannot be negative")
        if product_in.discount_price is not None and product_in.discount_price < 0:
            raise BusinessRuleError("Discount price cannot be negative")

        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ResourceNotFoundError("Product not found")

        category = self.category_repo.get_by_id(product_in.category_id)
        if not category:
            raise BusinessRuleError(f"Category with id {product_in.category_id} not found")

        for key, value in product_in.model_dump().items():
            setattr(product, key, value)

        self.product_repo.db.commit()
        self.product_repo.db.refresh(product)
        return product

    def update_product_stock(self, product_id: int, stock_quantity: int) -> Product:
        if stock_quantity < 0:
            raise BusinessRuleError("Stock quantity cannot be negative")

        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ResourceNotFoundError(f"Product with id {product_id} not found")

        product.stock_quantity = stock_quantity
        self.product_repo.db.commit()
        self.product_repo.db.refresh(product)
        return product

    def delete_product(self, product_id: int) -> None:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ResourceNotFoundError("Product not found")
        self.product_repo.delete(product)

    def get_reviews(self, product_id: int) -> List[Review]:
        if product_id <= 0:
            raise ResourceNotFoundError(f"Product with id {product_id} not found")
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ResourceNotFoundError(f"Product with id {product_id} not found")
        return self.review_repo.list_by_product(product_id)

    def add_review(self, user_id: int, review_in: ReviewCreate) -> Review:
        if not review_in.product_id or review_in.product_id <= 0:
            raise ResourceNotFoundError("Valid product ID is required")
        product = self.product_repo.get_by_id(review_in.product_id)
        if not product:
            raise ResourceNotFoundError(f"Product with id {review_in.product_id} not found")

        existing = self.review_repo.get_by_user_and_product(user_id, review_in.product_id)
        if existing:
            raise ConflictError("You have already reviewed this product.")

        review = Review(
            product_id=review_in.product_id,
            user_id=user_id,
            rating=review_in.rating,
            comment=(review_in.comment or "").strip()
        )
        self.review_repo.db.add(review)
        self.review_repo.db.flush()

        all_reviews = self.review_repo.get_all_for_product(review_in.product_id)
        if all_reviews:
            product.review_count = len(all_reviews)
            product.rating = round(sum(r.rating for r in all_reviews) / len(all_reviews), 2)
        else:
            product.review_count = 0
            product.rating = 0.0

        self.review_repo.db.commit()
        self.review_repo.db.refresh(review)
        return review
