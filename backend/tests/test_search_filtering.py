import pytest
from app.models.category import Category
from app.models.product import Product

# ==============================================================================
# STEP #10 — SEARCH & FILTERING TEST SUITE
# ==============================================================================

# --- 1. Product Search Tests ---

def test_search_by_product_name(client, seed_test_data):
    # Sourdough Loaf is seeded in conftest
    res = client.get("/api/v1/products?search=Sourdough")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any("Sourdough" in item["name"] for item in data)

def test_search_case_insensitivity(client, seed_test_data):
    res_lower = client.get("/api/v1/products?search=sourdough")
    res_upper = client.get("/api/v1/products?search=SOURDOUGH")
    res_mixed = client.get("/api/v1/products?search=SoUrDoUgH")
    assert res_lower.status_code == 200
    assert res_upper.status_code == 200
    assert res_mixed.status_code == 200
    data_lower = res_lower.json()
    data_upper = res_upper.json()
    data_mixed = res_mixed.json()
    assert len(data_lower) == len(data_upper) == len(data_mixed)
    assert [p["id"] for p in data_lower] == [p["id"] for p in data_upper]

def test_search_partial_term(client, seed_test_data):
    res = client.get("/api/v1/products?search=sour")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any("Sourdough" in item["name"] for item in data)

def test_search_multi_word(client, seed_test_data):
    res = client.get("/api/v1/products?search=sourdough loaf")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Sourdough Loaf"

def test_search_whitespace_handling(client, seed_test_data):
    res = client.get("/api/v1/products?search=   sourdough   ")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any("Sourdough" in item["name"] for item in data)

def test_search_whitespace_only_returns_all(client, seed_test_data):
    res_all = client.get("/api/v1/products")
    res_space = client.get("/api/v1/products?search=   ")
    assert res_all.status_code == 200
    assert res_space.status_code == 200
    assert len(res_all.json()) == len(res_space.json())

def test_search_query_alias_q(client, seed_test_data):
    res = client.get("/api/v1/products?q=sourdough")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any("Sourdough" in item["name"] for item in data)

def test_search_no_matching_products(client, seed_test_data):
    res = client.get("/api/v1/products?search=NonExistentArtisanalAstronautFood999")
    assert res.status_code == 200
    assert res.json() == []

def test_search_special_characters_safe(client, seed_test_data):
    res = client.get("/api/v1/products?search=%25%27%20OR%201=1--")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_search_excessive_length_rejected(client):
    long_string = "a" * 101
    res = client.get(f"/api/v1/products?search={long_string}")
    assert res.status_code == 422


# --- 2. Category Filtering Tests ---

def test_filter_by_category_slug(client, seed_test_data):
    res = client.get("/api/v1/products?category_slug=bread")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2
    for item in data:
        assert item["category_id"] == seed_test_data["category"].id

def test_filter_by_category_id(client, seed_test_data):
    cat_id = seed_test_data["category"].id
    res = client.get(f"/api/v1/products?category_id={cat_id}")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2
    for item in data:
        assert item["category_id"] == cat_id

def test_filter_by_nonexistent_category(client):
    res_slug = client.get("/api/v1/products?category_slug=nonexistent-category-slug-999")
    assert res_slug.status_code == 200
    assert res_slug.json() == []

    res_id = client.get("/api/v1/products?category_id=999999")
    assert res_id.status_code == 200
    assert res_id.json() == []

def test_invalid_category_id_rejected(client):
    res = client.get("/api/v1/products?category_id=0")
    assert res.status_code == 422
    res_neg = client.get("/api/v1/products?category_id=-5")
    assert res_neg.status_code == 422


# --- 3. Price Filtering Tests ---

def test_filter_min_price(client, seed_test_data):
    # product_1 price=200, product_2 price=100
    res = client.get("/api/v1/products?min_price=150")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert all(item["price"] >= 150 for item in data)

def test_filter_max_price(client, seed_test_data):
    res = client.get("/api/v1/products?max_price=150")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert all(item["price"] <= 150 for item in data)

def test_filter_price_range(client, seed_test_data):
    res = client.get("/api/v1/products?min_price=90&max_price=210")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2
    assert all(90 <= item["price"] <= 210 for item in data)

def test_negative_price_rejected(client):
    res_min = client.get("/api/v1/products?min_price=-10")
    assert res_min.status_code == 422
    res_max = client.get("/api/v1/products?max_price=-50")
    assert res_max.status_code == 422

def test_min_price_greater_than_max_price_rejected(client):
    res = client.get("/api/v1/products?min_price=500&max_price=200")
    assert res.status_code == 422
    assert "min_price cannot be greater than max_price" in res.text


# --- 4. Availability / Inventory Integration Tests (Step #8) ---

def test_filter_in_stock_products_only(client, db_session, seed_test_data):
    cat = seed_test_data["category"]
    out_of_stock_item = Product(
        name="Zero Stock Croissant",
        slug="zero-stock-croissant",
        category_id=cat.id,
        description="Currently out of stock",
        price=120.0,
        stock_quantity=0,
        image_url="https://example.com/zero.jpg",
        is_popular=True
    )
    db_session.add(out_of_stock_item)
    db_session.commit()
    db_session.refresh(out_of_stock_item)

    # When in_stock=true, out_of_stock_item MUST NOT appear
    res = client.get("/api/v1/products?in_stock=true")
    assert res.status_code == 200
    data = res.json()
    ids = [item["id"] for item in data]
    assert out_of_stock_item.id not in ids
    assert all(item["stock_quantity"] > 0 for item in data)

def test_filter_out_of_stock_products_only(client, db_session, seed_test_data):
    cat = seed_test_data["category"]
    sold_out_baguette = Product(
        name="Sold Out Baguette",
        slug="sold-out-baguette",
        category_id=cat.id,
        description="All sold out",
        price=90.0,
        stock_quantity=0,
        image_url="https://example.com/soldout.jpg",
        is_popular=False
    )
    db_session.add(sold_out_baguette)
    db_session.commit()
    db_session.refresh(sold_out_baguette)

    # When in_stock=false, only stock_quantity == 0 products appear
    res = client.get("/api/v1/products?in_stock=false")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    ids = [item["id"] for item in data]
    assert sold_out_baguette.id in ids
    assert all(item["stock_quantity"] == 0 for item in data)


# --- 5. Sorting Tests ---

def test_sort_by_price_asc(client, seed_test_data):
    res = client.get("/api/v1/products?sort_by=price_asc")
    assert res.status_code == 200
    data = res.json()
    prices = [item["price"] for item in data]
    assert prices == sorted(prices)

def test_sort_by_price_desc(client, seed_test_data):
    res = client.get("/api/v1/products?sort_by=price_desc")
    assert res.status_code == 200
    data = res.json()
    prices = [item["price"] for item in data]
    assert prices == sorted(prices, reverse=True)

def test_sort_by_name_asc(client, seed_test_data):
    res = client.get("/api/v1/products?sort_by=name_asc")
    assert res.status_code == 200
    data = res.json()
    names = [item["name"].lower() for item in data]
    assert names == sorted(names)

def test_sort_by_name_desc(client, seed_test_data):
    res = client.get("/api/v1/products?sort_by=name_desc")
    assert res.status_code == 200
    data = res.json()
    names = [item["name"].lower() for item in data]
    assert names == sorted(names, reverse=True)

def test_sort_by_rating(client, seed_test_data):
    res = client.get("/api/v1/products?sort_by=rating")
    assert res.status_code == 200
    data = res.json()
    ratings = [item["rating"] for item in data]
    assert ratings == sorted(ratings, reverse=True)

def test_sort_by_newest(client, db_session, seed_test_data):
    cat = seed_test_data["category"]
    brand_new_item = Product(
        name="Brand New Hot Bread",
        slug="brand-new-hot-bread",
        category_id=cat.id,
        description="Just pulled out of oven",
        price=150.0,
        stock_quantity=10,
        image_url="https://example.com/hot.jpg",
        is_popular=False
    )
    db_session.add(brand_new_item)
    db_session.commit()
    db_session.refresh(brand_new_item)

    res = client.get("/api/v1/products?sort_by=newest")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 3
    # The newly created item should be ranked first
    assert data[0]["id"] == brand_new_item.id

def test_invalid_sort_value_rejected(client):
    res = client.get("/api/v1/products?sort_by=sql_injection_attempt")
    assert res.status_code == 422


# --- 6. Search Relevance Ranking ---

def test_search_relevance_ranks_exact_name_above_description_match(client, db_session, seed_test_data):
    cat = seed_test_data["category"]
    # Product 1: Exact name match for "Tart"
    p_exact = Product(
        name="Tart",
        slug="artisanal-lemon-tart",
        category_id=cat.id,
        description="Fresh citrus pastry",
        price=180.0,
        stock_quantity=15,
        image_url="https://example.com/tart.jpg",
        is_popular=False,
        review_count=1,
        rating=4.0
    )
    # Product 2: Description-only match for "tart" with higher reviews
    p_desc = Product(
        name="Chocolate Mousse Cake",
        slug="choc-mousse-tart-desc",
        category_id=cat.id,
        description="Served with a side of fruit tart reduction",
        price=350.0,
        stock_quantity=10,
        image_url="https://example.com/mousse.jpg",
        is_popular=True,
        review_count=500,
        rating=5.0
    )
    db_session.add_all([p_exact, p_desc])
    db_session.commit()
    db_session.refresh(p_exact)
    db_session.refresh(p_desc)

    res = client.get("/api/v1/products?search=Tart")
    assert res.status_code == 200
    data = res.json()
    ids = [item["id"] for item in data]
    assert p_exact.id in ids
    assert p_desc.id in ids
    # Exact name match must be ranked before description match
    assert ids.index(p_exact.id) < ids.index(p_desc.id)


# --- 7. Combined Filter Combinations ---

def test_combined_search_category_price_and_in_stock(client, seed_test_data):
    cat_slug = seed_test_data["category"].slug
    res = client.get(
        f"/api/v1/products?search=Sourdough&category_slug={cat_slug}&min_price=100&max_price=300&in_stock=true"
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Sourdough Loaf"
    assert data[0]["price"] == 200.0
    assert data[0]["stock_quantity"] > 0

def test_combined_filters_mutually_exclusive_yield_empty(client, seed_test_data):
    # Sourdough Loaf price is 200.0; filtering min_price=300 must yield empty list
    res = client.get("/api/v1/products?search=Sourdough&min_price=300")
    assert res.status_code == 200
    assert res.json() == []


# --- 8. Pagination & Limit Tests ---

def test_pagination_limit(client, seed_test_data):
    res = client.get("/api/v1/products?limit=1")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1

def test_pagination_skip(client, seed_test_data):
    res_all = client.get("/api/v1/products")
    res_skip = client.get("/api/v1/products?skip=1")
    assert res_all.status_code == 200
    assert res_skip.status_code == 200
    all_data = res_all.json()
    skip_data = res_skip.json()
    assert len(skip_data) == len(all_data) - 1
    assert skip_data[0]["id"] == all_data[1]["id"]

def test_invalid_pagination_rejected(client):
    res_skip = client.get("/api/v1/products?skip=-1")
    assert res_skip.status_code == 422
    res_limit = client.get("/api/v1/products?limit=0")
    assert res_limit.status_code == 422
    res_max_limit = client.get("/api/v1/products?limit=101")
    assert res_max_limit.status_code == 422
