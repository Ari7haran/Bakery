import pytest
from app.models.category import Category
from app.models.order import Order, OrderItem
from app.models.product import Product

# --- 1. Recommendation Retrieval & Status Codes ---

def test_get_recommendations_valid_product(client, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.get(f"/api/v1/products/recommendations/{p1.id}")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) <= 4

def test_get_recommendations_nonexistent_product(client):
    res = client.get("/api/v1/products/recommendations/99999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_get_recommendations_invalid_product_id(client):
    res_zero = client.get("/api/v1/products/recommendations/0")
    assert res_zero.status_code == 422

    res_neg = client.get("/api/v1/products/recommendations/-3")
    assert res_neg.status_code == 422

    res_str = client.get("/api/v1/products/recommendations/abc")
    assert res_str.status_code == 422

# --- 2. Limit Validation & Boundary Values ---

def test_get_recommendations_custom_limit(client, db_session, seed_test_data):
    cat = seed_test_data["category"]
    p1 = seed_test_data["product_1"]
    p3 = Product(
        name="Ciabatta",
        slug="ciabatta",
        category_id=cat.id,
        description="Italian bread",
        price=120.0,
        stock_quantity=10,
        image_url="https://example.com/ciabatta.jpg"
    )
    db_session.add(p3)
    db_session.commit()

    res = client.get(f"/api/v1/products/recommendations/{p1.id}?limit=2")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2

def test_get_recommendations_minimum_limit(client, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.get(f"/api/v1/products/recommendations/{p1.id}?limit=1")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1

def test_get_recommendations_maximum_limit(client, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.get(f"/api/v1/products/recommendations/{p1.id}?limit=20")
    assert res.status_code == 200
    data = res.json()
    assert len(data) <= 20

def test_get_recommendations_invalid_limit(client, seed_test_data):
    p1 = seed_test_data["product_1"]
    # limit = 0 -> 422
    assert client.get(f"/api/v1/products/recommendations/{p1.id}?limit=0").status_code == 422

    # negative limit -> 422
    assert client.get(f"/api/v1/products/recommendations/{p1.id}?limit=-5").status_code == 422

    # excessively large limit exceeding max 20 -> 422
    assert client.get(f"/api/v1/products/recommendations/{p1.id}?limit=50").status_code == 422

# --- 3. Filtering: Target Exclusion & Deduplication ---

def test_current_product_excluded_from_recommendations(client, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.get(f"/api/v1/products/recommendations/{p1.id}?limit=10")
    assert res.status_code == 200
    rec_ids = [item["id"] for item in res.json()]
    assert p1.id not in rec_ids

def test_no_duplicate_products_in_recommendations(client, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.get(f"/api/v1/products/recommendations/{p1.id}?limit=10")
    assert res.status_code == 200
    rec_ids = [item["id"] for item in res.json()]
    assert len(rec_ids) == len(set(rec_ids))

# --- 4. Relevance & Ranking ---

def test_same_category_products_prioritized(client, db_session, seed_test_data):
    cat = seed_test_data["category"]
    p1 = seed_test_data["product_1"]

    # Create another product in the exact same category
    p_same_cat = Product(
        name="Rye Sourdough Bread",
        slug="rye-sourdough-bread",
        category_id=cat.id,
        description="Fresh hearty rye sourdough",
        price=220.0,
        stock_quantity=20,
        image_url="https://example.com/rye.jpg",
        is_veg=True,
        is_popular=False
    )
    db_session.add(p_same_cat)
    db_session.commit()
    db_session.refresh(p_same_cat)

    res = client.get(f"/api/v1/products/recommendations/{p1.id}?limit=4")
    assert res.status_code == 200
    data = res.json()
    rec_ids = [item["id"] for item in data]
    # Product in the same category must be included in recommendations
    assert p_same_cat.id in rec_ids

def test_frequently_bought_together_co_occurrence(client, db_session, seed_test_data):
    customer = seed_test_data["customer"]
    p1 = seed_test_data["product_1"]
    p2 = seed_test_data["product_2"]

    # Create an order where p1 and p2 were bought together
    order = Order(
        order_number="TEST-CO-BUY-101",
        user_id=customer.id,
        total_amount=300.0,
        discount_amount=0.0,
        final_amount=300.0,
        order_type="Takeaway Pickup",
        status="Completed",
        payment_method="Cash on Pickup",
        payment_status="Paid"
    )
    db_session.add(order)
    db_session.flush()

    item1 = OrderItem(order_id=order.id, product_id=p1.id, quantity=1, price=180.0)
    item2 = OrderItem(order_id=order.id, product_id=p2.id, quantity=1, price=100.0)
    db_session.add_all([item1, item2])
    db_session.commit()

    # When querying recommendations for p1, p2 should be returned as top frequently bought together
    res = client.get(f"/api/v1/products/recommendations/{p1.id}?limit=4")
    assert res.status_code == 200
    data = res.json()
    rec_ids = [item["id"] for item in data]
    assert p2.id in rec_ids
    # p2 should be the very first recommendation because it was co-purchased
    assert rec_ids[0] == p2.id

def test_in_stock_products_prioritized_over_out_of_stock(client, db_session, seed_test_data):
    cat = seed_test_data["category"]
    p1 = seed_test_data["product_1"]

    # Product A: Out of stock (0)
    p_out = Product(
        name="Out of Stock Brioche",
        slug="out-of-stock-brioche",
        category_id=cat.id,
        description="Unavailable",
        price=100.0,
        stock_quantity=0,
        image_url="https://example.com/out.jpg",
        is_popular=True
    )
    # Product B: In stock (10)
    p_in = Product(
        name="Fresh Available Brioche",
        slug="fresh-available-brioche",
        category_id=cat.id,
        description="Available",
        price=100.0,
        stock_quantity=10,
        image_url="https://example.com/in.jpg",
        is_popular=True
    )
    db_session.add_all([p_out, p_in])
    db_session.commit()
    db_session.refresh(p_out)
    db_session.refresh(p_in)

    res = client.get(f"/api/v1/products/recommendations/{p1.id}?limit=10")
    assert res.status_code == 200
    data = res.json()

    # Find indexes of both products
    idx_in = next((i for i, item in enumerate(data) if item["id"] == p_in.id), None)
    idx_out = next((i for i, item in enumerate(data) if item["id"] == p_out.id), None)

    assert idx_in is not None
    if idx_out is not None:
        # In-stock product must be ranked before out-of-stock product
        assert idx_in < idx_out

def test_public_access_no_auth_required(client, seed_test_data):
    p1 = seed_test_data["product_1"]
    # Request without Authorization headers
    res = client.get(f"/api/v1/products/recommendations/{p1.id}")
    assert res.status_code == 200

def test_isolated_category_product_fallback_to_popular_catalog_products(client, db_session, seed_test_data):
    # Category with only ONE product in it
    isolated_cat = Category(name="Solo Category", slug="solo-category", description="Only one product")
    db_session.add(isolated_cat)
    db_session.commit()
    db_session.refresh(isolated_cat)

    solo_prod = Product(
        name="Solo Artisanal Loaf",
        slug="solo-artisanal-loaf",
        category_id=isolated_cat.id,
        description="The only one of its kind",
        price=150.0,
        stock_quantity=5,
        image_url="https://example.com/solo.jpg",
        is_popular=True
    )
    db_session.add(solo_prod)
    db_session.commit()
    db_session.refresh(solo_prod)

    # When requesting recommendations for solo_prod, there are no same-category items,
    # so it must fall back to other catalog products (e.g. product_1, product_2)
    res = client.get(f"/api/v1/products/recommendations/{solo_prod.id}?limit=2")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    rec_ids = [item["id"] for item in data]
    assert solo_prod.id not in rec_ids

def test_limit_greater_than_available_catalog_returns_all_available_gracefully(client, seed_test_data):
    p1 = seed_test_data["product_1"]
    # Request limit=20 when catalog only has a few items
    res = client.get(f"/api/v1/products/recommendations/{p1.id}?limit=20")
    assert res.status_code == 200
    data = res.json()
    # It should not fail, should not exceed available items, and should exclude p1
    assert isinstance(data, list)
    assert len(data) > 0
    assert len(data) <= 20
    assert all(item["id"] != p1.id for item in data)
