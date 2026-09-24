import pytest
from app.models.cart import CartItem

# --- 1. Basic Cart Operations ---

def test_add_to_cart_and_get_cart(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    payload = {"product_id": prod_id, "quantity": 2}
    add_res = client.post("/api/v1/user/cart", json=payload, headers=customer_headers)
    assert add_res.status_code == 200
    data = add_res.json()
    assert data["quantity"] == 2
    assert data["product_id"] == prod_id
    assert data["subtotal"] == 360.0  # 180.0 discount_price * 2

    # Get cart
    get_res = client.get("/api/v1/user/cart", headers=customer_headers)
    assert get_res.status_code == 200
    items = get_res.json()
    assert len(items) == 1
    assert items[0]["product_id"] == prod_id
    assert items[0]["quantity"] == 2
    assert items[0]["subtotal"] == 360.0

def test_cart_update_quantity(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    add_res = client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": 2}, headers=customer_headers)
    cart_id = add_res.json()["id"]

    # Update quantity to 4
    update_res = client.put(f"/api/v1/user/cart/{cart_id}", json={"quantity": 4}, headers=customer_headers)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["quantity"] == 4
    assert data["subtotal"] == 720.0  # 180.0 * 4

def test_cart_remove_item(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    add_res = client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": 1}, headers=customer_headers)
    cart_id = add_res.json()["id"]

    del_res = client.delete(f"/api/v1/user/cart/{cart_id}", headers=customer_headers)
    assert del_res.status_code == 200
    assert del_res.json()["message"] == "Cart item removed"

    # Verify cart is empty
    get_res = client.get("/api/v1/user/cart", headers=customer_headers)
    assert len(get_res.json()) == 0

def test_cart_clear(client, customer_headers, seed_test_data):
    p1_id = seed_test_data["product_1"].id
    p2_id = seed_test_data["product_2"].id
    client.post("/api/v1/user/cart", json={"product_id": p1_id, "quantity": 1}, headers=customer_headers)
    client.post("/api/v1/user/cart", json={"product_id": p2_id, "quantity": 2}, headers=customer_headers)

    clear_res = client.delete("/api/v1/user/cart-clear", headers=customer_headers)
    assert clear_res.status_code == 200
    assert clear_res.json()["message"] == "Cart cleared"

    get_res = client.get("/api/v1/user/cart", headers=customer_headers)
    assert len(get_res.json()) == 0

def test_get_empty_cart(client, customer_headers, seed_test_data):
    get_res = client.get("/api/v1/user/cart", headers=customer_headers)
    assert get_res.status_code == 200
    assert get_res.json() == []

# --- 2. Product Validation ---

def test_add_nonexistent_product(client, customer_headers):
    response = client.post("/api/v1/user/cart", json={"product_id": 99999, "quantity": 1}, headers=customer_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_add_to_cart_exceeding_stock(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_2"].id  # stock is 5
    payload = {"product_id": prod_id, "quantity": 10}
    response = client.post("/api/v1/user/cart", json=payload, headers=customer_headers)
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

def test_add_to_cart_invalid_product_id(client, customer_headers):
    res_zero = client.post("/api/v1/user/cart", json={"product_id": 0, "quantity": 1}, headers=customer_headers)
    assert res_zero.status_code == 422

    res_neg = client.post("/api/v1/user/cart", json={"product_id": -5, "quantity": 1}, headers=customer_headers)
    assert res_neg.status_code == 422

    res_str = client.post("/api/v1/user/cart", json={"product_id": "invalid", "quantity": 1}, headers=customer_headers)
    assert res_str.status_code == 422

def test_add_to_cart_missing_product_id(client, customer_headers):
    response = client.post("/api/v1/user/cart", json={"quantity": 1}, headers=customer_headers)
    assert response.status_code == 422

# --- 3. Quantity Validation ---

def test_add_to_cart_quantity_zero(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    response = client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": 0}, headers=customer_headers)
    assert response.status_code == 422

def test_add_to_cart_negative_quantity(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    response = client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": -2}, headers=customer_headers)
    assert response.status_code == 422

def test_add_to_cart_decimal_quantity(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    response = client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": 2.5}, headers=customer_headers)
    assert response.status_code == 422

def test_add_to_cart_string_quantity(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    response = client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": "three"}, headers=customer_headers)
    assert response.status_code == 422

def test_add_to_cart_null_quantity(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    response = client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": None}, headers=customer_headers)
    assert response.status_code == 422

def test_add_to_cart_missing_quantity_defaults_to_one(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    response = client.post("/api/v1/user/cart", json={"product_id": prod_id}, headers=customer_headers)
    assert response.status_code == 200
    assert response.json()["quantity"] == 1

def test_update_cart_quantity_zero_or_negative(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    add_res = client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": 2}, headers=customer_headers)
    cart_id = add_res.json()["id"]

    res_zero = client.put(f"/api/v1/user/cart/{cart_id}", json={"quantity": 0}, headers=customer_headers)
    assert res_zero.status_code == 422

    res_neg = client.put(f"/api/v1/user/cart/{cart_id}", json={"quantity": -1}, headers=customer_headers)
    assert res_neg.status_code == 422

def test_update_cart_exceeding_stock(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_2"].id  # stock is 5
    add_res = client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": 2}, headers=customer_headers)
    cart_id = add_res.json()["id"]

    res = client.put(f"/api/v1/user/cart/{cart_id}", json={"quantity": 10}, headers=customer_headers)
    assert res.status_code == 400
    assert "Insufficient stock" in res.json()["detail"]

# --- 4. Duplicate Products & Aggregation ---

def test_add_same_product_twice_aggregates_quantity(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    res1 = client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": 2}, headers=customer_headers)
    assert res1.status_code == 200
    assert res1.json()["quantity"] == 2

    res2 = client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": 3}, headers=customer_headers)
    assert res2.status_code == 200
    assert res2.json()["quantity"] == 5

    # Verify database has only 1 row for this user & product
    get_res = client.get("/api/v1/user/cart", headers=customer_headers)
    items = get_res.json()
    assert len(items) == 1
    assert items[0]["quantity"] == 5

def test_add_same_product_twice_exceeding_stock_rejected(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_2"].id  # stock is 5
    client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": 3}, headers=customer_headers)

    # Adding 3 more when stock is 5 (total 6) must fail
    res = client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": 3}, headers=customer_headers)
    assert res.status_code == 400
    assert "Stock limit" in res.json()["detail"]

# --- 5. Authorization & Isolation ---

def test_unauthenticated_cart_access(client, seed_test_data):
    assert client.get("/api/v1/user/cart").status_code == 401
    assert client.post("/api/v1/user/cart", json={"product_id": 1, "quantity": 1}).status_code == 401
    assert client.put("/api/v1/user/cart/1", json={"quantity": 2}).status_code == 401
    assert client.delete("/api/v1/user/cart/1").status_code == 401
    assert client.delete("/api/v1/user/cart-clear").status_code == 401

def test_cart_user_isolation(client, customer_headers, customer_b_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    # Alice adds item
    add_res = client.post("/api/v1/user/cart", json={"product_id": prod_id, "quantity": 1}, headers=customer_headers)
    cart_id = add_res.json()["id"]

    # Bob's cart should be empty
    bob_cart = client.get("/api/v1/user/cart", headers=customer_b_headers).json()
    assert len(bob_cart) == 0

    # Bob cannot update or delete Alice's cart item
    bob_update = client.put(f"/api/v1/user/cart/{cart_id}", json={"quantity": 5}, headers=customer_b_headers)
    assert bob_update.status_code == 404

    bob_del = client.delete(f"/api/v1/user/cart/{cart_id}", headers=customer_b_headers)
    assert bob_del.status_code == 404

def test_customer_cannot_clear_another_user_cart(client, customer_headers, customer_b_headers, seed_test_data):
    p1_id = seed_test_data["product_1"].id
    # Alice has item
    client.post("/api/v1/user/cart", json={"product_id": p1_id, "quantity": 2}, headers=customer_headers)
    # Bob clears his cart
    client.delete("/api/v1/user/cart-clear", headers=customer_b_headers)

    # Alice's cart must still have her item
    alice_cart = client.get("/api/v1/user/cart", headers=customer_headers).json()
    assert len(alice_cart) == 1
    assert alice_cart[0]["quantity"] == 2

# --- 6. Pricing Authority & Calculation ---

def test_client_cannot_manipulate_product_price(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id  # actual discount_price is 180.0
    # Client tries to pass price = 1.0
    payload = {"product_id": prod_id, "quantity": 2, "price": 1.0, "subtotal": 2.0}
    add_res = client.post("/api/v1/user/cart", json=payload, headers=customer_headers)
    assert add_res.status_code == 200
    data = add_res.json()
    # Server authoritative price remains 180.0, subtotal 360.0
    assert data["product"]["discount_price"] == 180.0
    assert data["subtotal"] == 360.0

def test_cart_multiple_products_subtotal(client, customer_headers, seed_test_data):
    p1_id = seed_test_data["product_1"].id  # discount_price: 180.0
    p2_id = seed_test_data["product_2"].id  # price: 100.0, discount_price: None
    client.post("/api/v1/user/cart", json={"product_id": p1_id, "quantity": 2}, headers=customer_headers)
    client.post("/api/v1/user/cart", json={"product_id": p2_id, "quantity": 3}, headers=customer_headers)

    get_res = client.get("/api/v1/user/cart", headers=customer_headers)
    items = get_res.json()
    assert len(items) == 2
    item_map = {item["product_id"]: item for item in items}
    assert item_map[p1_id]["subtotal"] == 360.0  # 180 * 2
    assert item_map[p2_id]["subtotal"] == 300.0  # 100 * 3

# --- 7. Cart to Order Checkout Integration ---

def test_successful_takeaway_checkout_clears_db_cart(client, customer_headers, seed_test_data):
    p1_id = seed_test_data["product_1"].id
    # Add to cart
    client.post("/api/v1/user/cart", json={"product_id": p1_id, "quantity": 2}, headers=customer_headers)

    # Place takeaway order using db cart (items=None)
    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Tomorrow",
        "pickup_time_slot": "10:00 AM - 11:00 AM",
        "payment_method": "Cash on Pickup",
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 200
    assert res.json()["final_amount"] == 360.0

    # DB cart must now be empty
    cart_res = client.get("/api/v1/user/cart", headers=customer_headers)
    assert len(cart_res.json()) == 0

def test_successful_delivery_checkout_clears_db_cart(client, customer_headers, seed_test_data):
    p2_id = seed_test_data["product_2"].id
    client.post("/api/v1/user/cart", json={"product_id": p2_id, "quantity": 2}, headers=customer_headers)

    # Place delivery order
    order_payload = {
        "order_type": "Delivery",
        "delivery_address": "456 Oak Avenue, Apt 2B, Springfield",
        "payment_method": "Cash on Delivery",
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 200
    assert res.json()["final_amount"] == 200.0

    # DB cart must now be empty
    cart_res = client.get("/api/v1/user/cart", headers=customer_headers)
    assert len(cart_res.json()) == 0

def test_failed_checkout_preserves_cart(client, customer_headers, seed_test_data):
    p1_id = seed_test_data["product_1"].id
    client.post("/api/v1/user/cart", json={"product_id": p1_id, "quantity": 2}, headers=customer_headers)

    # Attempt order with invalid payment method to trigger failure
    bad_payload = {
        "order_type": "Delivery",
        "delivery_address": "456 Oak Avenue, Apt 2B, Springfield",
        "payment_method": "INVALID_METHOD",
    }
    res = client.post("/api/v1/orders/", json=bad_payload, headers=customer_headers)
    assert res.status_code == 400

    # Cart must be preserved!
    cart_res = client.get("/api/v1/user/cart", headers=customer_headers)
    assert len(cart_res.json()) == 1
    assert cart_res.json()[0]["quantity"] == 2

def test_empty_cart_checkout_rejected(client, customer_headers):
    # Ensure cart is empty
    client.delete("/api/v1/user/cart-clear", headers=customer_headers)

    # Attempt order without items payload and empty DB cart
    payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 05:00 PM",
        "payment_method": "Cash on Pickup",
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()

def test_empty_items_list_checkout_rejected(client, customer_headers):
    payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 05:00 PM",
        "payment_method": "Cash on Pickup",
        "items": []
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "no items" in res.json()["detail"].lower()

# --- 8. Coupon Validation (Preserved) ---

def test_coupon_validation(client, seed_test_data):
    # Valid coupon
    res_valid = client.post("/api/v1/user/coupon/validate", json={"code": "SAVE20", "order_amount": 200.0})
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert data["valid"] is True
    assert data["discount_percent"] == 20.0
    assert data["discount_amount"] == 40.0  # 20% of 200 is 40 (max is 50)

    # Below minimum order amount
    res_below = client.post("/api/v1/user/coupon/validate", json={"code": "SAVE20", "order_amount": 100.0})
    assert res_below.status_code == 400
    assert "Minimum order amount" in res_below.json()["detail"]
