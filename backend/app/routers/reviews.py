from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.all_models import Review, Product, User
from app.schemas.schemas import ReviewCreate, ReviewOut
from app.routers.auth import get_current_user

router = APIRouter(tags=["Reviews"])

@router.get("/products/{product_id}/reviews", response_model=List[ReviewOut])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.product_id == product_id).order_by(Review.created_at.desc()).all()

@router.post("/reviews", response_model=ReviewOut)
def create_review(review_in: ReviewCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == review_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_review = Review(
        product_id=review_in.product_id,
        user_id=current_user.id,
        rating=review_in.rating,
        comment=review_in.comment
    )
    db.add(new_review)
    
    # Recalculate average rating
    all_reviews = db.query(Review).filter(Review.product_id == review_in.product_id).all()
    total_ratings = sum(r.rating for r in all_reviews) + review_in.rating
    cnt = len(all_reviews) + 1
    product.rating = round(total_ratings / cnt, 1)
    product.review_count = cnt

    db.commit()
    db.refresh(new_review)
    return new_review
