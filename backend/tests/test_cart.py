def test_add_to_cart_and_get_cart(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_1"].id
    payload = {"product_id": prod_id, "quantity": 2}
    add_res = client.post("/api/v1/user/cart", json=payload, headers=customer_headers)
    assert add_res.status_code == 200
    assert add_res.json()["quantity"] == 2

    # Get cart
    get_res = client.get("/api/v1/user/cart", headers=customer_headers)
    assert get_res.status_code == 200
    items = get_res.json()
    assert len(items) == 1
    assert items[0]["product_id"] == prod_id
    assert items[0]["quantity"] == 2

def test_add_to_cart_exceeding_stock(client, customer_headers, seed_test_data):
    prod_id = seed_test_data["product_2"].id  # stock is 5
    payload = {"product_id": prod_id, "quantity": 10}
    response = client.post("/api/v1/user/cart", json=payload, headers=customer_headers)
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

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
