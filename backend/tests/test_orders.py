def test_create_order_cash_flow_and_stock_deduction(client, customer_headers, seed_test_data, db_session):
    p1 = seed_test_data["product_1"]  # price: 200, discount_price: 180, initial stock: 15
    initial_stock = p1.stock_quantity

    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "coupon_code": "SAVE20",
        "items": [{"product_id": p1.id, "quantity": 2}]
    }

    response = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert response.status_code == 200
    order_data = response.json()

    # Authoritative calculation: 2 * 180 = 360. 20% discount on 360 = 72, capped at 50 -> final: 310
    assert order_data["total_amount"] == 360.0
    assert order_data["discount_amount"] == 50.0
    assert order_data["final_amount"] == 310.0

    # Payment status strictly Pending
    assert order_data["payment_status"] == "Pending"
    assert order_data["payment_method"] == "Cash on Pickup"
    assert order_data["status"] == "Received"
    assert order_data["pickup_number"] is not None
    assert order_data["qr_code_data"] is not None

    # Verify inventory was decremented
    db_session.refresh(p1)
    assert p1.stock_quantity == initial_stock - 2

def test_reject_online_payment(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    order_payload = {
        "order_type": "Takeaway Pickup",
        "payment_method": "Online Payment",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    response = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert response.status_code == 400
    assert "CASH ONLY" in response.json()["detail"]

def test_order_user_isolation(client, customer_headers, customer_b_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    # Alice places an order
    order_payload = {
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res_order = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    order_id = res_order.json()["id"]

    # Bob tries to access Alice's order -> 403 Forbidden
    res_bob = client.get(f"/api/v1/orders/{order_id}", headers=customer_b_headers)
    assert res_bob.status_code == 403

def test_order_status_state_machine(client, customer_headers, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    # Alice places order
    order_payload = {
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    order_id = res.json()["id"]

    # Valid step 1: Received -> Preparing
    res_step1 = client.put(f"/api/v1/admin/orders/{order_id}/status", json={"status": "Preparing"}, headers=admin_headers)
    assert res_step1.status_code == 200
    assert res_step1.json()["status"] == "Preparing"

    # Valid step 2: Preparing -> Baking
    res_step2 = client.put(f"/api/v1/admin/orders/{order_id}/status", json={"status": "Baking"}, headers=admin_headers)
    assert res_step2.status_code == 200
    assert res_step2.json()["status"] == "Baking"

    # Valid step 3: Baking -> Packing
    res_step3 = client.put(f"/api/v1/admin/orders/{order_id}/status", json={"status": "Packing"}, headers=admin_headers)
    assert res_step3.status_code == 200
    assert res_step3.json()["status"] == "Packing"

    # Valid step 4: Packing -> Ready for Pickup
    res_step4 = client.put(f"/api/v1/admin/orders/{order_id}/status", json={"status": "Ready for Pickup"}, headers=admin_headers)
    assert res_step4.status_code == 200
    assert res_step4.json()["status"] == "Ready for Pickup"

    # Valid step 5: Ready for Pickup -> Completed (also marks payment Paid automatically)
    res_step5 = client.put(f"/api/v1/admin/orders/{order_id}/status", json={"status": "Completed"}, headers=admin_headers)
    assert res_step5.status_code == 200
    assert res_step5.json()["status"] == "Completed"
    assert res_step5.json()["payment_status"] == "Paid"

    # Invalid backward step: Completed -> Preparing should be rejected with 400
    res_invalid = client.put(f"/api/v1/admin/orders/{order_id}/status", json={"status": "Preparing"}, headers=admin_headers)
    assert res_invalid.status_code == 400
    assert "Invalid status transition" in res_invalid.json()["detail"]
