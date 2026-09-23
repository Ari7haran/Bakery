from typing import List, Optional
from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.banner_repository import BannerRepository
from app.repositories.review_repository import ReviewRepository
from app.core.exceptions import ResourceNotFoundError, BusinessRuleError
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
        search: Optional[str] = None,
        is_veg: Optional[bool] = None,
        is_featured: Optional[bool] = None,
        is_todays_fresh: Optional[bool] = None,
        is_popular: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = "popular",
    ) -> List[Product]:
        return self.product_repo.list_products(
            category_slug=category_slug,
            search=search,
            is_veg=is_veg,
            is_featured=is_featured,
            is_todays_fresh=is_todays_fresh,
            is_popular=is_popular,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
        )

    def get_product(self, product_id: int) -> Product:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ResourceNotFoundError(f"Product with id {product_id} not found")
        return product

    def get_recommendations(self, product_id: int) -> List[Product]:
        return self.product_repo.get_recommendations(product_id)

    def list_categories(self) -> List[Category]:
        return self.category_repo.list_all()

    def get_banners(self) -> List[Banner]:
        return self.banner_repo.list_active()

    def create_product(self, product_in: ProductBase) -> Product:
        category = self.category_repo.get_by_id(product_in.category_id)
        if not category:
            raise BusinessRuleError(f"Category with id {product_in.category_id} not found")

        existing_slug = self.product_repo.get_by_slug(product_in.slug)
        if existing_slug:
            raise BusinessRuleError(f"Product slug '{product_in.slug}' already exists")

        product = Product(**product_in.model_dump())
        return self.product_repo.add(product)

    def update_product(self, product_id: int, product_in: ProductBase) -> Product:
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

    def delete_product(self, product_id: int) -> None:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ResourceNotFoundError("Product not found")
        self.product_repo.delete(product)

    def get_reviews(self, product_id: int) -> List[Review]:
        return self.review_repo.list_by_product(product_id)

    def add_review(self, user_id: int, review_in: ReviewCreate) -> Review:
        product = self.product_repo.get_by_id(review_in.product_id)
        if not product:
            raise ResourceNotFoundError("Product not found")

        review = Review(
            product_id=review_in.product_id,
            user_id=user_id,
            rating=review_in.rating,
            comment=review_in.comment
        )
        self.review_repo.db.add(review)

        # Recalculate average rating
        all_reviews = self.review_repo.list_by_product(review_in.product_id)
        total_ratings = sum(r.rating for r in all_reviews) + review_in.rating
        cnt = len(all_reviews) + 1
        product.rating = round(total_ratings / cnt, 1)
        product.review_count = cnt

        self.review_repo.db.commit()
        self.review_repo.db.refresh(review)
        return review
