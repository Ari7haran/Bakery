from datetime import timedelta
from app.core.security import create_access_token
from app.core.config import settings
from app.models.user import User

# --- Registration Tests ---

def test_register_success(client, seed_test_data):
    payload = {
        "full_name": "New Customer",
        "email": "newcustomer@test.com",
        "password": "securepassword123",
        "phone": "+1 555-0100"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newcustomer@test.com"
    assert data["user"]["role"] == "customer"
    assert data["user"]["loyalty_points"] == 100
    assert "password" not in data["user"]
    assert "hashed_password" not in data["user"]

def test_register_duplicate_email(client, seed_test_data):
    payload = {
        "full_name": "Duplicate Alice",
        "email": seed_test_data["customer"].email,
        "password": "password123"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "Email already registered" in response.json()["detail"]

def test_register_invalid_email(client):
    payload = {
        "full_name": "Invalid Email",
        "email": "not-a-valid-email",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422

def test_register_short_password(client):
    payload = {
        "full_name": "Short Password",
        "email": "short@test.com",
        "password": "123"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422

def test_register_blank_name(client):
    payload = {
        "full_name": "   ",
        "email": "blankname@test.com",
        "password": "validpassword123"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422

def test_register_password_stored_hashed_in_db(client, db_session):
    payload = {
        "full_name": "Hash Verification",
        "email": "hashcheck@test.com",
        "password": "mysecretpassword123"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200

    user = db_session.query(User).filter(User.email == "hashcheck@test.com").first()
    assert user is not None
    assert user.hashed_password != "mysecretpassword123"
    assert user.hashed_password.startswith("$2b$")

# --- Login Tests ---

def test_login_success(client, seed_test_data):
    payload = {
        "email": "alice@test.com",
        "password": "alicepass123"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "alice@test.com"
    assert "password" not in data["user"]
    assert "hashed_password" not in data["user"]

def test_login_invalid_password(client, seed_test_data):
    payload = {
        "email": "alice@test.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_login_nonexistent_user(client, seed_test_data):
    payload = {
        "email": "nonexistent@test.com",
        "password": "anyPassword123"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_login_inactive_user(client, seed_test_data, db_session):
    user_b = seed_test_data["customer_b"]
    user_b.is_active = False
    db_session.commit()

    payload = {
        "email": "bob@test.com",
        "password": "bobpass123"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "inactive" in response.json()["detail"].lower()

# --- JWT Token Validation & Bearer Auth Tests ---

def test_me_endpoint_authorized(client, customer_headers):
    response = client.get("/api/v1/auth/me", headers=customer_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "alice@test.com"

def test_me_endpoint_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_jwt_expired_token(client, seed_test_data):
    expired_token = create_access_token(
        subject=seed_test_data["customer"].id,
        expires_delta=timedelta(minutes=-10)
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401

def test_jwt_malformed_token_invalid_signature(client):
    headers = {"Authorization": "Bearer invalid.token.payload"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401

def test_jwt_malformed_token_non_integer_sub(client):
    token = create_access_token(subject="not-an-integer-id")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401

def test_jwt_nonexistent_user(client):
    token = create_access_token(subject=999999)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401

def test_jwt_wrong_scheme(client, seed_test_data):
    token = create_access_token(subject=seed_test_data["customer"].id)
    headers = {"Authorization": f"Basic {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401

# --- Authorization & Role Isolation Tests ---

def test_admin_protection(client, customer_headers, admin_headers):
    # Customer gets 403 Forbidden
    res_cust = client.get("/api/v1/admin/users", headers=customer_headers)
    assert res_cust.status_code == 403

    # Admin gets 200 OK
    res_admin = client.get("/api/v1/admin/users", headers=admin_headers)
    assert res_admin.status_code == 200

def test_customer_cannot_access_any_admin_endpoint(client, customer_headers):
    endpoints = [
        ("GET", "/api/v1/admin/analytics"),
        ("GET", "/api/v1/admin/orders"),
        ("GET", "/api/v1/admin/users"),
    ]
    for method, endpoint in endpoints:
        res = client.request(method, endpoint, headers=customer_headers)
        assert res.status_code == 403, f"Endpoint {endpoint} should be 403 for customers"

def test_admin_can_access_intended_admin_endpoints(client, admin_headers):
    res_analytics = client.get("/api/v1/admin/analytics", headers=admin_headers)
    assert res_analytics.status_code == 200
    res_orders = client.get("/api/v1/admin/orders", headers=admin_headers)
    assert res_orders.status_code == 200
    res_users = client.get("/api/v1/admin/users", headers=admin_headers)
    assert res_users.status_code == 200

def test_customer_order_ownership_isolation(client, seed_test_data, customer_headers, customer_b_headers):
    # Customer Alice creates an order
    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": seed_test_data["product_1"].id, "quantity": 1}]
    }
    create_res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert create_res.status_code == 200
    order_id = create_res.json()["id"]

    # Customer Alice can view her own order
    alice_view = client.get(f"/api/v1/orders/{order_id}", headers=customer_headers)
    assert alice_view.status_code == 200

    # Customer Bob cannot view Alice's order (403 Forbidden)
    bob_view = client.get(f"/api/v1/orders/{order_id}", headers=customer_b_headers)
    assert bob_view.status_code == 403

def test_customer_cart_ownership_isolation(client, seed_test_data, customer_headers, customer_b_headers):
    # Customer Alice adds an item to her cart
    cart_payload = {"product_id": seed_test_data["product_1"].id, "quantity": 1}
    add_res = client.post("/api/v1/user/cart", json=cart_payload, headers=customer_headers)
    assert add_res.status_code == 200
    cart_id = add_res.json()["id"]

    # Customer Bob cannot update Alice's cart item (404 Not Found)
    bob_update = client.put(f"/api/v1/user/cart/{cart_id}", json={"quantity": 5}, headers=customer_b_headers)
    assert bob_update.status_code == 404

    # Customer Bob cannot delete Alice's cart item (404 Not Found)
    bob_delete = client.delete(f"/api/v1/user/cart/{cart_id}", headers=customer_b_headers)
    assert bob_delete.status_code == 404

# --- Security Tests ---

def test_secrets_and_passwords_not_leaked(client, seed_test_data, customer_headers):
    # Verify me response has no password hash or secret
    me_res = client.get("/api/v1/auth/me", headers=customer_headers)
    raw_text = me_res.text
    assert "hashed_password" not in raw_text
    assert settings.SECRET_KEY not in raw_text
