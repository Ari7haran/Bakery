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

def test_register_duplicate_email(client, seed_test_data):
    payload = {
        "full_name": "Duplicate Alice",
        "email": seed_test_data["customer"].email,
        "password": "password123"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "Email already registered" in response.json()["detail"]

def test_login_success(client, seed_test_data):
    payload = {
        "email": "alice@test.com",
        "password": "alicepass123"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "alice@test.com"

def test_login_invalid_password(client, seed_test_data):
    payload = {
        "email": "alice@test.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_me_endpoint_authorized(client, customer_headers):
    response = client.get("/api/v1/auth/me", headers=customer_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "alice@test.com"

def test_me_endpoint_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_admin_protection(client, customer_headers, admin_headers):
    # Customer gets 403 Forbidden
    res_cust = client.get("/api/v1/admin/users", headers=customer_headers)
    assert res_cust.status_code == 403

    # Admin gets 200 OK
    res_admin = client.get("/api/v1/admin/users", headers=admin_headers)
    assert res_admin.status_code == 200
