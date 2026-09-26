import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.models import User, Category, Product, Coupon, RoleEnum, Notification
from app.main import app

# Create completely isolated in-memory SQLite engine for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def seed_test_data(db_session):
    # Create test admin
    admin = User(
        full_name="Admin User",
        email="admin@test.com",
        hashed_password=get_password_hash("adminpass123"),
        role=RoleEnum.ADMIN.value,
        loyalty_points=500,
        is_active=True
    )
    # Create test customer A
    customer = User(
        full_name="Customer Alice",
        email="alice@test.com",
        hashed_password=get_password_hash("alicepass123"),
        role=RoleEnum.CUSTOMER.value,
        loyalty_points=100,
        is_active=True
    )
    # Create test customer B
    customer_b = User(
        full_name="Customer Bob",
        email="bob@test.com",
        hashed_password=get_password_hash("bobpass123"),
        role=RoleEnum.CUSTOMER.value,
        loyalty_points=50,
        is_active=True
    )
    db_session.add_all([admin, customer, customer_b])
    db_session.flush()

    # Create test category
    cat = Category(
        name="Artisan Bread",
        slug="bread",
        description="Freshly baked artisan breads"
    )
    db_session.add(cat)
    db_session.flush()

    # Create test products
    p1 = Product(
        name="Sourdough Loaf",
        slug="sourdough-loaf",
        category_id=cat.id,
        description="Crusty sourdough bread",
        price=200.0,
        discount_price=180.0,
        stock_quantity=15,
        image_url="https://example.com/sourdough.jpg",
        is_veg=True,
        is_popular=True
    )
    p2 = Product(
        name="Baguette",
        slug="baguette",
        category_id=cat.id,
        description="Crisp French baguette",
        price=100.0,
        discount_price=None,
        stock_quantity=5,
        image_url="https://example.com/baguette.jpg",
        is_veg=True,
        is_popular=False
    )
    db_session.add_all([p1, p2])

    # Create test coupon
    coupon = Coupon(
        code="SAVE20",
        discount_percent=20.0,
        max_discount_amount=50.0,
        min_order_amount=150.0,
        is_active=True
    )
    db_session.add(coupon)
    db_session.commit()

    return {
        "admin": admin,
        "customer": customer,
        "customer_b": customer_b,
        "category": cat,
        "product_1": p1,
        "product_2": p2,
        "coupon": coupon
    }

@pytest.fixture
def admin_headers(seed_test_data):
    token = create_access_token(subject=seed_test_data["admin"].id, role="admin")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def customer_headers(seed_test_data):
    token = create_access_token(subject=seed_test_data["customer"].id, role="customer")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def customer_b_headers(seed_test_data):
    token = create_access_token(subject=seed_test_data["customer_b"].id, role="customer")
    return {"Authorization": f"Bearer {token}"}
