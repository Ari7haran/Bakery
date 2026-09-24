import pytest
from app.models.order import Order
from app.models.product import Product

# ============================================================================
# DELIVERY TESTS (1 - 10)
# ============================================================================

def test_valid_delivery_order(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Delivery",
        "delivery_address": "742 Evergreen Terrace, Sector 4, Springfield",
        "payment_method": "Cash on Delivery",
        "notes": "Please ring the bell twice",
        "items": [{"product_id": p1.id, "quantity": 2}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["order_type"] == "Delivery"
    assert data["delivery_address"] == "742 Evergreen Terrace, Sector 4, Springfield"
    assert data["payment_method"] == "Cash on Delivery"
    assert data["pickup_date"] is None
    assert data["pickup_time_slot"] is None
    assert data["pickup_number"] is None
    assert data["status"] == "Received"
    assert data["notes"] == "Please ring the bell twice"

def test_delivery_without_address(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Delivery",
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Delivery address is required" in res.json()["detail"]

def test_delivery_with_blank_address(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Delivery",
        "delivery_address": "",
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Delivery address is required" in res.json()["detail"]

def test_delivery_with_whitespace_only_address(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Delivery",
        "delivery_address": "     \t \n   ",
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Delivery address is required" in res.json()["detail"]

def test_delivery_with_valid_address(client, customer_headers, seed_test_data):
    p2 = seed_test_data["product_2"]
    payload = {
        "order_type": "Delivery",
        "delivery_address": "Suite 101, Baker Street Bakery Lane, City",
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p2.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 200
    assert res.json()["delivery_address"] == "Suite 101, Baker Street Bakery Lane, City"

def test_invalid_order_type(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Drone Express",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Invalid order type" in res.json()["detail"]

def test_delivery_unauthenticated_access(client):
    res = client.post("/api/v1/orders/", json={
        "order_type": "Delivery",
        "delivery_address": "123 Main St",
        "payment_method": "Cash on Delivery"
    })
    assert res.status_code == 401

def test_delivery_cross_user_access(client, customer_headers, customer_b_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    # Alice places a delivery order
    res_a = client.post("/api/v1/orders/", json={
        "order_type": "Delivery",
        "delivery_address": "Alice's Secret Cottage, Woods Lane",
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    order_id = res_a.json()["id"]

    # Bob tries to view Alice's delivery order
    res_b = client.get(f"/api/v1/orders/{order_id}", headers=customer_b_headers)
    assert res_b.status_code == 403

def test_delivery_order_retrieval(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res_create = client.post("/api/v1/orders/", json={
        "order_type": "Delivery",
        "delivery_address": "42 Wallaby Way, Sydney",
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    order_id = res_create.json()["id"]

    res_get = client.get(f"/api/v1/orders/{order_id}", headers=customer_headers)
    assert res_get.status_code == 200
    data = res_get.json()
    assert data["id"] == order_id
    assert data["order_type"] == "Delivery"
    assert data["delivery_address"] == "42 Wallaby Way, Sydney"

def test_delivery_cancellation_if_eligible(client, customer_headers, seed_test_data, db_session):
    p1 = seed_test_data["product_1"]
    initial_stock = p1.stock_quantity

    res_create = client.post("/api/v1/orders/", json={
        "order_type": "Delivery",
        "delivery_address": "10 Downing Street, London",
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 2}]
    }, headers=customer_headers)
    order_id = res_create.json()["id"]

    db_session.refresh(p1)
    assert p1.stock_quantity == initial_stock - 2

    # Cancel eligible order in Received state
    res_cancel = client.post(f"/api/v1/orders/{order_id}/cancel", headers=customer_headers)
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "Cancelled"

    db_session.refresh(p1)
    assert p1.stock_quantity == initial_stock

# ============================================================================
# TAKEAWAY TESTS (11 - 17)
# ============================================================================

def test_valid_takeaway_order(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Tomorrow",
        "pickup_time_slot": "10:00 AM - 10:30 AM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["order_type"] == "Takeaway Pickup"
    assert data["pickup_date"] == "Tomorrow"
    assert data["pickup_time_slot"] == "10:00 AM - 10:30 AM"
    assert data["pickup_number"] is not None
    assert data["delivery_address"] is None
    assert data["payment_method"] == "Cash on Pickup"

def test_takeaway_without_pickup_date(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Takeaway Pickup",
        "pickup_time_slot": "10:00 AM - 10:30 AM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Pickup date is required" in res.json()["detail"]

def test_takeaway_without_pickup_time_slot(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Pickup time slot is required" in res.json()["detail"]

def test_takeaway_with_blank_or_whitespace_pickup_date(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "    ",
        "pickup_time_slot": "10:00 AM - 10:30 AM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Pickup date is required" in res.json()["detail"]

def test_takeaway_with_blank_or_whitespace_pickup_time_slot(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "  \t  ",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Pickup time slot is required" in res.json()["detail"]

def test_takeaway_order_retrieval(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res_create = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "02:00 PM - 02:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    order_id = res_create.json()["id"]

    res_get = client.get(f"/api/v1/orders/{order_id}", headers=customer_headers)
    assert res_get.status_code == 200
    data = res_get.json()
    assert data["order_type"] == "Takeaway Pickup"
    assert data["pickup_date"] == "Today"
    assert data["pickup_time_slot"] == "02:00 PM - 02:30 PM"
    assert data["pickup_number"] is not None

def test_takeaway_cancellation_if_eligible(client, customer_headers, seed_test_data, db_session):
    p1 = seed_test_data["product_1"]
    initial_stock = p1.stock_quantity

    res_create = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    order_id = res_create.json()["id"]

    res_cancel = client.post(f"/api/v1/orders/{order_id}/cancel", headers=customer_headers)
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "Cancelled"

    db_session.refresh(p1)
    assert p1.stock_quantity == initial_stock

# ============================================================================
# FIELD COMBINATIONS & INTEGRITY (18 - 24)
# ============================================================================

def test_delivery_with_pickup_fields_rejected(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Delivery",
        "delivery_address": "123 High Street, Downtown",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Delivery orders cannot contain pickup scheduling fields" in res.json()["detail"]

def test_takeaway_with_delivery_address_rejected(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "delivery_address": "123 High Street, Downtown",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Takeaway orders cannot contain a delivery address" in res.json()["detail"]

def test_missing_order_type_rejected(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Order type is required" in res.json()["detail"]

def test_invalid_payload_types(client, customer_headers):
    # Invalid items structure
    res = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "items": "not-a-list"
    }, headers=customer_headers)
    assert res.status_code == 422

def test_delivery_excessively_long_address_rejected(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Delivery",
        "delivery_address": "A" * 501,
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "Delivery address cannot exceed 500 characters" in res.json()["detail"]

def test_delivery_empty_string_address_rejected(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Delivery",
        "delivery_address": "",
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=payload, headers=customer_headers)
    assert res.status_code == 400

def test_takeaway_excessively_long_pickup_fields_rejected(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res_date = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "pickup_date": "D" * 51,
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    assert res_date.status_code == 400
    assert "Pickup date cannot exceed 50 characters" in res_date.json()["detail"]

# ============================================================================
# AUTHORIZATION TESTS (25 - 29)
# ============================================================================

def test_customer_cannot_update_order_status(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    order_id = res.json()["id"]

    res_put = client.put(f"/api/v1/admin/orders/{order_id}/status", json={"status": "Completed"}, headers=customer_headers)
    assert res_put.status_code == 403

def test_customer_cannot_update_payment_status(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    order_id = res.json()["id"]

    res_put = client.put(f"/api/v1/admin/orders/{order_id}/payment", headers=customer_headers)
    assert res_put.status_code == 403

def test_customer_cannot_access_another_user_order(client, customer_headers, customer_b_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    order_id = res.json()["id"]

    res_b = client.get(f"/api/v1/orders/{order_id}", headers=customer_b_headers)
    assert res_b.status_code == 403

def test_customer_cannot_access_another_user_delivery_information(client, customer_headers, customer_b_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.post("/api/v1/orders/", json={
        "order_type": "Delivery",
        "delivery_address": "Secret Confidential Manor, Hilltop",
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    order_id = res.json()["id"]

    # Bob attempts to get Alice's delivery order info
    res_b = client.get(f"/api/v1/orders/{order_id}", headers=customer_b_headers)
    assert res_b.status_code == 403
    assert "Secret Confidential Manor" not in res_b.text

def test_admin_can_access_authorized_order_management(client, admin_headers, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res_del = client.post("/api/v1/orders/", json={
        "order_type": "Delivery",
        "delivery_address": "88 Riverside Blvd, Apt 12A",
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    order_id = res_del.json()["id"]

    # Admin lists orders and sees delivery info
    res_admin = client.get("/api/v1/admin/orders", headers=admin_headers)
    assert res_admin.status_code == 200
    orders = res_admin.json()
    matched = next((o for o in orders if o["id"] == order_id), None)
    assert matched is not None
    assert matched["order_type"] == "Delivery"
    assert matched["delivery_address"] == "88 Riverside Blvd, Apt 12A"

    # Admin updates status to Preparing
    res_status = client.put(f"/api/v1/admin/orders/{order_id}/status", json={"status": "Preparing"}, headers=admin_headers)
    assert res_status.status_code == 200
    assert res_status.json()["status"] == "Preparing"
