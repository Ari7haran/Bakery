import pytest
from app.models.product import Product

# --- 1. Product Stock Validation ---

def test_admin_update_valid_stock(client, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.put(f"/api/v1/admin/products/{p1.id}/stock", json={"stock_quantity": 50}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["stock_quantity"] == 50

def test_admin_update_zero_stock(client, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.put(f"/api/v1/admin/products/{p1.id}/stock", json={"stock_quantity": 0}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["stock_quantity"] == 0

def test_admin_update_negative_stock_rejected(client, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.put(f"/api/v1/admin/products/{p1.id}/stock", json={"stock_quantity": -10}, headers=admin_headers)
    assert res.status_code == 422

def test_admin_update_decimal_stock_rejected(client, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.put(f"/api/v1/admin/products/{p1.id}/stock", json={"stock_quantity": 12.5}, headers=admin_headers)
    assert res.status_code == 422

def test_admin_update_string_stock_rejected(client, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.put(f"/api/v1/admin/products/{p1.id}/stock", json={"stock_quantity": "fifty"}, headers=admin_headers)
    assert res.status_code == 422

def test_admin_update_null_stock_rejected(client, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.put(f"/api/v1/admin/products/{p1.id}/stock", json={"stock_quantity": None}, headers=admin_headers)
    assert res.status_code == 422

def test_admin_patch_stock(client, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.patch(f"/api/v1/admin/products/{p1.id}/stock", json={"stock_quantity": 18}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["stock_quantity"] == 18

# --- 2. Stock Availability & Order Boundary Values ---

def test_order_quantity_below_stock(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]  # stock is 15
    initial_stock = p1.stock_quantity
    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 3}]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 200

    # Stock should be initial_stock - 3
    prod_res = client.get(f"/api/v1/products/{p1.id}")
    assert prod_res.json()["stock_quantity"] == initial_stock - 3

def test_order_quantity_equal_to_stock(client, customer_headers, admin_headers, seed_test_data):
    p2 = seed_test_data["product_2"]  # stock is 5
    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p2.id, "quantity": 5}]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 200

    # Stock should now be 0 (out of stock)
    prod_res = client.get(f"/api/v1/products/{p2.id}")
    assert prod_res.json()["stock_quantity"] == 0

def test_order_quantity_above_stock_rejected(client, customer_headers, seed_test_data):
    p2 = seed_test_data["product_2"]  # stock is 5
    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p2.id, "quantity": 6}]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Insufficient stock" in res.json()["detail"]

def test_order_zero_stock_product_rejected(client, customer_headers, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    # Admin sets stock to 0
    client.put(f"/api/v1/admin/products/{p1.id}/stock", json={"stock_quantity": 0}, headers=admin_headers)

    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Insufficient stock" in res.json()["detail"]

# --- 3. Multi-Product & Independent Stock Deduction ---

def test_multiple_products_deduct_independently(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]  # 15
    p2 = seed_test_data["product_2"]  # 5
    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [
            {"product_id": p1.id, "quantity": 2},
            {"product_id": p2.id, "quantity": 3}
        ]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 200

    assert client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"] == 13
    assert client.get(f"/api/v1/products/{p2.id}").json()["stock_quantity"] == 2

def test_stock_deducted_exactly_once(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    init_stock = client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"]

    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 200

    # Stock should be decremented by exactly 1
    after_stock = client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"]
    assert after_stock == init_stock - 1

    # Fetching order details or tracking should not change stock
    order_id = res.json()["id"]
    client.get(f"/api/v1/orders/{order_id}", headers=customer_headers)
    assert client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"] == after_stock

# --- 4. Transaction Safety & Failed Checkout Rollback ---

def test_failed_checkout_invalid_coupon_preserves_stock(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    init_stock = client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"]

    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "coupon_code": "NONEXISTENT_COUPON_XYZ",
        "items": [{"product_id": p1.id, "quantity": 2}]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 400

    # Stock must remain unchanged
    current_stock = client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"]
    assert current_stock == init_stock

def test_failed_checkout_invalid_address_preserves_stock(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    init_stock = client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"]

    order_payload = {
        "order_type": "Delivery",
        "delivery_address": "   ",  # Blank address
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 2}]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 400

    # Stock must remain unchanged
    assert client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"] == init_stock

def test_failed_checkout_invalid_takeaway_slot_preserves_stock(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    init_stock = client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"]

    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "",  # Empty slot
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 2}]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 400

    # Stock must remain unchanged
    assert client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"] == init_stock

# --- 5. Cart Integration & Changing Stock ---

def test_cart_add_within_stock(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.post("/api/v1/user/cart", json={"product_id": p1.id, "quantity": 2}, headers=customer_headers)
    assert res.status_code == 200
    assert res.json()["quantity"] == 2

def test_cart_add_exceeding_stock(client, customer_headers, seed_test_data):
    p2 = seed_test_data["product_2"]  # stock is 5
    res = client.post("/api/v1/user/cart", json={"product_id": p2.id, "quantity": 10}, headers=customer_headers)
    assert res.status_code == 400
    assert "Insufficient stock" in res.json()["detail"]

def test_cart_update_exceeding_stock(client, customer_headers, seed_test_data):
    p2 = seed_test_data["product_2"]  # stock is 5
    add_res = client.post("/api/v1/user/cart", json={"product_id": p2.id, "quantity": 2}, headers=customer_headers)
    cart_id = add_res.json()["id"]

    res = client.put(f"/api/v1/user/cart/{cart_id}", json={"quantity": 8}, headers=customer_headers)
    assert res.status_code == 400
    assert "Insufficient stock" in res.json()["detail"]

def test_product_depleted_before_checkout_blocks_order(client, customer_headers, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    # Customer adds 2 items to cart
    client.post("/api/v1/user/cart", json={"product_id": p1.id, "quantity": 2}, headers=customer_headers)

    # Meanwhile, admin adjusts stock down to 1
    client.put(f"/api/v1/admin/products/{p1.id}/stock", json={"stock_quantity": 1}, headers=admin_headers)

    # Customer attempts to checkout using db cart
    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup"
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Insufficient stock" in res.json()["detail"]

# --- 6. Authorization & Security ---

def test_unauthenticated_stock_modification_rejected(client, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.put(f"/api/v1/admin/products/{p1.id}/stock", json={"stock_quantity": 100})
    assert res.status_code == 401

def test_customer_cannot_modify_stock(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.put(f"/api/v1/admin/products/{p1.id}/stock", json={"stock_quantity": 100}, headers=customer_headers)
    assert res.status_code == 403

def test_client_cannot_manipulate_server_stock(client, customer_headers, seed_test_data):
    p2 = seed_test_data["product_2"]  # stock is 5
    # Client attempts to pass fake high stock in items payload
    payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p2.id, "quantity": 10, "stock_quantity": 9999}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Insufficient stock" in res.json()["detail"]

# --- 7. Order Cancellation & Stock Restoration ---

def test_order_cancellation_restores_stock(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    init_stock = client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"]

    # Place order for 3 items
    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 3}]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 200
    order_id = res.json()["id"]

    # Stock is decremented by 3
    assert client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"] == init_stock - 3

    # Cancel the order
    cancel_res = client.post(f"/api/v1/orders/{order_id}/cancel", headers=customer_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "Cancelled"

    # Stock must be restored back to init_stock
    assert client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"] == init_stock

def test_admin_cancellation_restores_stock(client, customer_headers, admin_headers, seed_test_data):
    p2 = seed_test_data["product_2"]
    init_stock = client.get(f"/api/v1/products/{p2.id}").json()["stock_quantity"]

    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p2.id, "quantity": 2}]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    order_id = res.json()["id"]

    # Admin advances status to Preparing
    client.put(f"/api/v1/admin/orders/{order_id}/status", json={"status": "Preparing"}, headers=admin_headers)

    # Admin cancels order
    cancel_res = client.put(f"/api/v1/admin/orders/{order_id}/status", json={"status": "Cancelled"}, headers=admin_headers)
    assert cancel_res.status_code == 200

    # Stock must be restored
    assert client.get(f"/api/v1/products/{p2.id}").json()["stock_quantity"] == init_stock

def test_double_cancellation_prevented_no_double_restoration(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    init_stock = client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"]

    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 2}]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    order_id = res.json()["id"]

    # First cancel
    client.post(f"/api/v1/orders/{order_id}/cancel", headers=customer_headers)
    assert client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"] == init_stock

    # Second cancel attempt must fail
    res_second = client.post(f"/api/v1/orders/{order_id}/cancel", headers=customer_headers)
    assert res_second.status_code == 400
    assert "already cancelled" in res_second.json()["detail"].lower()

    # Stock must NOT be restored twice!
    assert client.get(f"/api/v1/products/{p1.id}").json()["stock_quantity"] == init_stock
