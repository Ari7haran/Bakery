import pytest
from sqlalchemy.exc import IntegrityError
from app.models import CartItem, Product, Review, OrderItem

def test_foreign_key_enforcement(db_session, seed_test_data):
    """
    Attempt to insert an OrderItem with a non-existent order_id.
    Expected: SQLite/SQLAlchemy raises IntegrityError due to PRAGMA foreign_keys = ON.
    """
    p = seed_test_data["product_1"]
    invalid_item = OrderItem(
        order_id=999999,  # Non-existent order ID
        product_id=p.id,
        quantity=1,
        price=100.0
    )
    db_session.add(invalid_item)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

def test_quantity_constraint(db_session, seed_test_data):
    """
    Attempt to insert a CartItem with quantity <= 0.
    Expected: CheckConstraint fails, raising IntegrityError.
    """
    u = seed_test_data["customer"]
    p = seed_test_data["product_1"]
    invalid_cart = CartItem(
        user_id=u.id,
        product_id=p.id,
        quantity=0  # Invalid non-positive quantity
    )
    db_session.add(invalid_cart)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

def test_product_price_constraint(db_session, seed_test_data):
    """
    Attempt to insert product with invalid negative price.
    Expected: CheckConstraint fails, raising IntegrityError.
    """
    cat = seed_test_data["category"]
    invalid_prod = Product(
        name="Negative Price Bread",
        slug="negative-price-bread",
        category_id=cat.id,
        description="Invalid product",
        price=-50.0,  # Invalid negative price
        stock_quantity=10,
        image_url="https://example.com/neg.jpg"
    )
    db_session.add(invalid_prod)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

def test_review_rating_constraint(db_session, seed_test_data):
    """
    Attempt to insert review with rating outside 1-5 (e.g. 0 or 6).
    Expected: CheckConstraint fails, raising IntegrityError.
    """
    u = seed_test_data["customer"]
    p = seed_test_data["product_1"]
    invalid_review = Review(
        product_id=p.id,
        user_id=u.id,
        rating=6,  # Invalid rating > 5
        comment="Too high"
    )
    db_session.add(invalid_review)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

def test_duplicate_cart_item_constraint(db_session, seed_test_data):
    """
    Attempt to insert two CartItems with identical (user_id, product_id).
    Expected: UniqueConstraint fails, raising IntegrityError.
    """
    u = seed_test_data["customer"]
    p = seed_test_data["product_1"]

    item1 = CartItem(user_id=u.id, product_id=p.id, quantity=1)
    db_session.add(item1)
    db_session.flush()

    item2 = CartItem(user_id=u.id, product_id=p.id, quantity=2)
    db_session.add(item2)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()
