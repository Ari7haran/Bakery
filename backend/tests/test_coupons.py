import pytest
from datetime import datetime, timezone, timedelta
from app.models import Coupon, Order, OrderItem, OrderStatusEnum, PaymentStatusEnum

# ----------------- 1. Customer Coupon Validation Tests -----------------

def test_validate_coupon_success(client, seed_test_data):
    """Valid active coupon with order amount meeting minimum returns discount."""
    payload = {"code": "SAVE20", "order_amount": 250.0}
    res = client.post("/api/v1/coupons/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["code"] == "SAVE20"
    # 20% of 250 = 50.0 (max discount cap is 50.0)
    assert data["discount_amount"] == 50.0
    assert data["final_amount"] == 200.0

def test_validate_coupon_legacy_user_route(client, seed_test_data):
    """Verify backward compatibility of /api/v1/user/coupon/validate route."""
    payload = {"code": "SAVE20", "order_amount": 200.0}
    res = client.post("/api/v1/user/coupon/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["code"] == "SAVE20"
    assert data["discount_amount"] == 40.0

def test_validate_coupon_case_insensitive_and_whitespace(client, seed_test_data):
    """Coupon codes are trimmed and case-insensitive."""
    payload = {"code": "  save20  ", "order_amount": 200.0}
    res = client.post("/api/v1/coupons/validate", json=payload)
    assert res.status_code == 200
    assert res.json()["code"] == "SAVE20"
    assert res.json()["discount_amount"] == 40.0

def test_validate_coupon_below_minimum_order_rejected(client, seed_test_data):
    """Order amount below min_order_amount returns 400 BusinessRuleError."""
    payload = {"code": "SAVE20", "order_amount": 100.0}
    res = client.post("/api/v1/coupons/validate", json=payload)
    assert res.status_code == 400
    assert "minimum order amount" in res.json()["detail"].lower()

def test_validate_coupon_exact_minimum_order_accepted(client, seed_test_data):
    """Order amount exactly equal to min_order_amount (150.0) is accepted."""
    payload = {"code": "SAVE20", "order_amount": 150.0}
    res = client.post("/api/v1/coupons/validate", json=payload)
    assert res.status_code == 200
    # 20% of 150 = 30.0
    assert res.json()["discount_amount"] == 30.0

def test_validate_coupon_max_discount_cap(client, seed_test_data):
    """Discount amount does not exceed max_discount_amount."""
    # 20% of 1000 = 200, but SAVE20 max_discount_amount is 50.0
    payload = {"code": "SAVE20", "order_amount": 1000.0}
    res = client.post("/api/v1/coupons/validate", json=payload)
    assert res.status_code == 200
    assert res.json()["discount_amount"] == 50.0
    assert res.json()["final_amount"] == 950.0

def test_validate_coupon_nonexistent_code(client):
    """Nonexistent coupon code returns 400 with invalid message."""
    payload = {"code": "NONEXISTENT999", "order_amount": 500.0}
    res = client.post("/api/v1/coupons/validate", json=payload)
    assert res.status_code == 400
    assert "invalid or expired" in res.json()["detail"].lower()

def test_validate_coupon_empty_code_rejected(client):
    """Empty or whitespace-only coupon code rejected with 422."""
    for empty_code in ["", "   "]:
        res = client.post("/api/v1/coupons/validate", json={"code": empty_code, "order_amount": 200.0})
        assert res.status_code in [400, 422]

def test_validate_coupon_negative_amount_rejected(client):
    """Negative order amount rejected with 422."""
    res = client.post("/api/v1/coupons/validate", json={"code": "SAVE20", "order_amount": -50.0})
    assert res.status_code == 422

def test_validate_inactive_coupon_rejected(client, db_session):
    """Inactive coupon cannot be applied."""
    inactive_coupon = Coupon(
        code="INACTIVE10",
        discount_percent=10.0,
        max_discount_amount=50.0,
        min_order_amount=100.0,
        is_active=False
    )
    db_session.add(inactive_coupon)
    db_session.commit()

    res = client.post("/api/v1/coupons/validate", json={"code": "INACTIVE10", "order_amount": 200.0})
    assert res.status_code == 400
    assert "invalid or expired" in res.json()["detail"].lower()

def test_validate_expired_coupon_rejected(client, db_session):
    """Expired coupon is rejected."""
    past_date = datetime.now(timezone.utc) - timedelta(days=2)
    expired_coupon = Coupon(
        code="EXPIRED50",
        discount_percent=50.0,
        max_discount_amount=100.0,
        min_order_amount=100.0,
        is_active=True,
        expiry_date=past_date
    )
    db_session.add(expired_coupon)
    db_session.commit()

    res = client.post("/api/v1/coupons/validate", json={"code": "EXPIRED50", "order_amount": 200.0})
    assert res.status_code == 400
    assert "expired" in res.json()["detail"].lower()

def test_list_active_coupons_for_customers(client, seed_test_data):
    """Customers can list active, unexpired coupons."""
    res = client.get("/api/v1/coupons")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert any(c["code"] == "SAVE20" for c in data)
    assert all(c["is_active"] is True for c in data)

# ----------------- 2. Admin Coupon Management Tests -----------------

def test_admin_list_all_coupons(client, admin_headers, seed_test_data):
    """Admin can list all coupons."""
    res = client.get("/api/v1/admin/coupons", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_admin_list_coupons_requires_admin_auth(client, customer_headers):
    """Regular customer cannot access admin coupon list (403)."""
    res = client.get("/api/v1/admin/coupons", headers=customer_headers)
    assert res.status_code == 403

def test_admin_create_coupon_success(client, admin_headers):
    """Admin creates a new coupon."""
    future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    payload = {
        "code": "FESTIVE30",
        "discount_percent": 30.0,
        "max_discount_amount": 300.0,
        "min_order_amount": 500.0,
        "is_active": True,
        "expiry_date": future_date
    }
    res = client.post("/api/v1/admin/coupons", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["code"] == "FESTIVE30"
    assert data["discount_percent"] == 30.0
    assert data["max_discount_amount"] == 300.0
    assert data["min_order_amount"] == 500.0
    assert data["is_active"] is True

def test_admin_create_duplicate_coupon_rejected(client, admin_headers, seed_test_data):
    """Creating coupon with existing code returns 409 Conflict."""
    payload = {
        "code": "SAVE20",  # Already seeded
        "discount_percent": 15.0,
        "max_discount_amount": 50.0,
        "min_order_amount": 100.0
    }
    res = client.post("/api/v1/admin/coupons", json=payload, headers=admin_headers)
    assert res.status_code == 409
    assert "already exists" in res.json()["detail"].lower()

def test_admin_create_coupon_invalid_discount_percent(client, admin_headers):
    """Discount percent must be between 0 and 100."""
    for bad_percent in [-10.0, 105.0]:
        payload = {
            "code": "BADPERCENT",
            "discount_percent": bad_percent,
            "max_discount_amount": 50.0,
            "min_order_amount": 100.0
        }
        res = client.post("/api/v1/admin/coupons", json=payload, headers=admin_headers)
        assert res.status_code == 422

def test_admin_create_coupon_negative_amounts_rejected(client, admin_headers):
    """Negative min order amount or max discount rejected with 422."""
    payload_bad_min = {
        "code": "BADMIN",
        "discount_percent": 10.0,
        "max_discount_amount": 50.0,
        "min_order_amount": -100.0
    }
    res1 = client.post("/api/v1/admin/coupons", json=payload_bad_min, headers=admin_headers)
    assert res1.status_code == 422

    payload_bad_max = {
        "code": "BADMAX",
        "discount_percent": 10.0,
        "max_discount_amount": -50.0,
        "min_order_amount": 100.0
    }
    res2 = client.post("/api/v1/admin/coupons", json=payload_bad_max, headers=admin_headers)
    assert res2.status_code == 422

def test_admin_get_coupon_by_id(client, admin_headers, seed_test_data):
    """Admin retrieves coupon by ID."""
    coupon_id = seed_test_data["coupon"].id
    res = client.get(f"/api/v1/admin/coupons/{coupon_id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["id"] == coupon_id
    assert res.json()["code"] == "SAVE20"

def test_admin_get_nonexistent_coupon_returns_404(client, admin_headers):
    """Querying nonexistent coupon ID returns 404."""
    res = client.get("/api/v1/admin/coupons/99999", headers=admin_headers)
    assert res.status_code == 404

def test_admin_update_coupon(client, admin_headers, seed_test_data):
    """Admin updates coupon parameters."""
    coupon_id = seed_test_data["coupon"].id
    payload = {
        "discount_percent": 25.0,
        "max_discount_amount": 80.0
    }
    res = client.put(f"/api/v1/admin/coupons/{coupon_id}", json=payload, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["discount_percent"] == 25.0
    assert data["max_discount_amount"] == 80.0

def test_admin_delete_coupon(client, admin_headers, db_session):
    """Admin deletes a coupon."""
    temp_coupon = Coupon(
        code="TEMPDELETE",
        discount_percent=10.0,
        max_discount_amount=50.0,
        min_order_amount=100.0,
        is_active=True
    )
    db_session.add(temp_coupon)
    db_session.commit()
    c_id = temp_coupon.id

    res = client.delete(f"/api/v1/admin/coupons/{c_id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["message"] == "Coupon deleted successfully"

    # Confirm it cannot be queried
    res_get = client.get(f"/api/v1/admin/coupons/{c_id}", headers=admin_headers)
    assert res_get.status_code == 404

# ----------------- 3. Order Integration & Security Tests -----------------

def test_create_order_with_valid_coupon(client, customer_headers, seed_test_data):
    """Creating an order with valid coupon applies discount and computes final amount."""
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Tomorrow",
        "pickup_time_slot": "10:00 AM - 10:30 AM",
        "coupon_code": "SAVE20",
        "items": [{"product_id": p1.id, "quantity": 1}]  # 180.0 (discount price)
    }
    res = client.post("/api/v1/orders", json=payload, headers=customer_headers)
    assert res.status_code == 200
    data = res.json()
    # 20% of 180.0 = 36.0 discount
    assert data["total_amount"] == 180.0
    assert data["discount_amount"] == 36.0
    assert data["final_amount"] == 144.0

def test_create_order_with_invalid_coupon_rejected(client, customer_headers, seed_test_data):
    """Order creation with invalid coupon returns 400."""
    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Tomorrow",
        "pickup_time_slot": "10:00 AM - 10:30 AM",
        "coupon_code": "INVALID_PROMO",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res = client.post("/api/v1/orders", json=payload, headers=customer_headers)
    assert res.status_code == 400
    assert "invalid or expired" in res.json()["detail"].lower()

def test_discount_cannot_exceed_total_amount(client, customer_headers, db_session, seed_test_data):
    """100% discount with high cap does not result in negative final amount."""
    free_coupon = Coupon(
        code="FREE100",
        discount_percent=100.0,
        max_discount_amount=1000.0,
        min_order_amount=50.0,
        is_active=True
    )
    db_session.add(free_coupon)
    db_session.commit()

    p1 = seed_test_data["product_1"]
    payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Tomorrow",
        "pickup_time_slot": "10:00 AM - 10:30 AM",
        "coupon_code": "FREE100",
        "items": [{"product_id": p1.id, "quantity": 1}]  # 180.0
    }
    res = client.post("/api/v1/orders", json=payload, headers=customer_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_amount"] == 180.0
    assert data["discount_amount"] == 180.0
    assert data["final_amount"] == 0.0

def test_security_sql_injection_code_handled_safely(client):
    """SQL injection strings in coupon code are handled safely as plain text."""
    payload = {"code": "'; DROP TABLE coupons; --", "order_amount": 500.0}
    res = client.post("/api/v1/coupons/validate", json=payload)
    assert res.status_code == 400
    assert "invalid or expired" in res.json()["detail"].lower()

def test_security_excessive_coupon_length_rejected(client):
    """Codes exceeding 50 characters are rejected with 422."""
    payload = {"code": "A" * 55, "order_amount": 500.0}
    res = client.post("/api/v1/coupons/validate", json=payload)
    assert res.status_code == 422
