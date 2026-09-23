from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# SQLite connection arguments for multithreading in FastAPI
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Enforce foreign key constraints on every SQLite connection.
    SQLite requires 'PRAGMA foreign_keys = ON;' on each connection.
    """
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()
    except Exception:
        pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db_indexes(bind_engine):
    """
    Idempotently and safely creates performance indexes and unique constraints
    identified during the database audit without dropping tables or losing data.
    """
    statements = [
        # Orders indexes
        "CREATE INDEX IF NOT EXISTS ix_orders_user_id ON orders (user_id);",
        "CREATE INDEX IF NOT EXISTS ix_orders_created_at ON orders (created_at);",
        "CREATE INDEX IF NOT EXISTS ix_orders_status ON orders (status);",
        "CREATE INDEX IF NOT EXISTS ix_orders_payment_status ON orders (payment_status);",
        # Order items indexes
        "CREATE INDEX IF NOT EXISTS ix_order_items_order_id ON order_items (order_id);",
        "CREATE INDEX IF NOT EXISTS ix_order_items_product_id ON order_items (product_id);",
        # Product and category indexes
        "CREATE INDEX IF NOT EXISTS ix_products_category_id ON products (category_id);",
        "CREATE INDEX IF NOT EXISTS ix_product_images_product_id ON product_images (product_id);",
        # Cart and wishlist indexes & unique constraints
        "CREATE INDEX IF NOT EXISTS ix_cart_items_user_id ON cart_items (user_id);",
        "CREATE INDEX IF NOT EXISTS ix_cart_items_product_id ON cart_items (product_id);",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_cart_user_product ON cart_items (user_id, product_id);",
        "CREATE INDEX IF NOT EXISTS ix_wishlist_items_user_id ON wishlist_items (user_id);",
        "CREATE INDEX IF NOT EXISTS ix_wishlist_items_product_id ON wishlist_items (product_id);",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_wishlist_user_product ON wishlist_items (user_id, product_id);",
        # Addresses and reviews indexes & unique constraints
        "CREATE INDEX IF NOT EXISTS ix_addresses_user_id ON addresses (user_id);",
        "CREATE INDEX IF NOT EXISTS ix_reviews_product_id ON reviews (product_id);",
        "CREATE INDEX IF NOT EXISTS ix_reviews_user_id ON reviews (user_id);",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_review_user_product ON reviews (user_id, product_id);",
    ]
    with bind_engine.connect() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        conn.commit()
