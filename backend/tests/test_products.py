def test_list_categories(client, seed_test_data):
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    cats = response.json()
    assert len(cats) >= 1
    assert cats[0]["slug"] == "bread"

def test_list_products(client, seed_test_data):
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 2

def test_filter_products_by_category(client, seed_test_data):
    response = client.get("/api/v1/products?category_slug=bread")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 2

def test_get_product_detail(client, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    response = client.get(f"/api/v1/products/{prod_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Sourdough Loaf"
    assert data["price"] == 200.0
    assert data["discount_price"] == 180.0

def test_get_product_not_found(client):
    response = client.get("/api/v1/products/99999")
    assert response.status_code == 404

def test_admin_create_product(client, admin_headers, seed_test_data):
    cat_id = seed_test_data["category"].id
    payload = {
        "name": "Brioche Bun",
        "slug": "brioche-bun",
        "category_id": cat_id,
        "description": "Rich golden buttery bun",
        "price": 60.0,
        "discount_price": 50.0,
        "is_veg": True,
        "stock_quantity": 30,
        "image_url": "https://example.com/brioche.jpg"
    }
    response = client.post("/api/v1/admin/products", json=payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Brioche Bun"
    assert data["slug"] == "brioche-bun"

def test_customer_cannot_create_product(client, customer_headers, seed_test_data):
    cat_id = seed_test_data["category"].id
    payload = {
        "name": "Hacked Product",
        "slug": "hacked-product",
        "category_id": cat_id,
        "description": "Should fail",
        "price": 10.0,
        "image_url": "https://example.com/hacked.jpg"
    }
    response = client.post("/api/v1/admin/products", json=payload, headers=customer_headers)
    assert response.status_code == 403
