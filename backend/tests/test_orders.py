from unittest.mock import patch
import pytest
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.cart import CartItem
from app.models.user import User, RoleEnum
from app.models.category import Category
from app.schemas.order import OrderCreate
from app.services.order_service import OrderService
from app.services.coupon_service import CouponService
from app.services.payment_service import PaymentService
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.user_repository import UserRepository
from tests.conftest import TestingSessionLocal

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

# --- Additional Order System Tests ---

def test_create_order_multiple_items_and_correct_totals(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]  # discount_price: 180
    p2 = seed_test_data["product_2"]  # price: 100

    order_payload = {
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [
            {"product_id": p1.id, "quantity": 2},  # 360
            {"product_id": p2.id, "quantity": 3}   # 300
        ]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_amount"] == 660.0
    assert data["discount_amount"] == 0.0
    assert data["final_amount"] == 660.0
    assert len(data["items"]) == 2

def test_create_order_consolidates_duplicate_product_items(client, customer_headers, seed_test_data, db_session):
    p1 = seed_test_data["product_1"]
    initial_stock = p1.stock_quantity

    order_payload = {
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [
            {"product_id": p1.id, "quantity": 1},
            {"product_id": p1.id, "quantity": 2}
        ]
    }
    res = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 3

    db_session.refresh(p1)
    assert p1.stock_quantity == initial_stock - 3

def test_create_order_zero_and_negative_quantity_rejected(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]

    res_zero = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 0}]
    }, headers=customer_headers)
    assert res_zero.status_code in [400, 422]

    res_neg = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": -3}]
    }, headers=customer_headers)
    assert res_neg.status_code in [400, 422]

def test_create_order_insufficient_stock_rejected(client, customer_headers, seed_test_data):
    p2 = seed_test_data["product_2"]  # stock: 5
    res = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p2.id, "quantity": 10}]
    }, headers=customer_headers)
    assert res.status_code == 400
    assert "Insufficient stock" in res.json()["detail"]

def test_create_order_nonexistent_product_rejected(client, customer_headers):
    res = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": 999999, "quantity": 1}]
    }, headers=customer_headers)
    assert res.status_code == 404

def test_create_order_empty_items_rejected(client, customer_headers):
    res = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": []
    }, headers=customer_headers)
    assert res.status_code == 400

def test_create_order_invalid_coupon_rejected(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "coupon_code": "DOESNOTEXIST",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    assert res.status_code == 400
    assert "Invalid or expired coupon" in res.json()["detail"]

def test_create_order_delivery_requires_address(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]

    # Delivery without address -> 400
    res_no_addr = client.post("/api/v1/orders/", json={
        "order_type": "Delivery",
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    assert res_no_addr.status_code == 400
    assert "Delivery address is required" in res_no_addr.json()["detail"]

    # Delivery with address -> 200
    res_with_addr = client.post("/api/v1/orders/", json={
        "order_type": "Delivery",
        "delivery_address": "456 Baker Street, Floor 2",
        "payment_method": "Cash on Delivery",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    assert res_with_addr.status_code == 200
    assert res_with_addr.json()["delivery_address"] == "456 Baker Street, Floor 2"

def test_create_order_invalid_order_type_rejected(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.post("/api/v1/orders/", json={
        "order_type": "Hyperloop",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    assert res.status_code == 400
    assert "Invalid order type" in res.json()["detail"]

def test_create_order_historical_price_snapshot(client, customer_headers, seed_test_data, db_session):
    p1 = seed_test_data["product_1"]  # discount_price: 180

    res = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    assert res.status_code == 200
    order_id = res.json()["id"]

    # Change product price in database
    p1.price = 500.0
    p1.discount_price = 450.0
    db_session.commit()

    # Retrieve order again: historical unit price and total must remain untouched
    res_get = client.get(f"/api/v1/orders/{order_id}", headers=customer_headers)
    assert res_get.status_code == 200
    data = res_get.json()
    assert data["items"][0]["price"] == 180.0
    assert data["total_amount"] == 180.0
    assert data["final_amount"] == 180.0

def test_customer_cancel_order_success_and_stock_restoration(client, customer_headers, seed_test_data, db_session):
    p1 = seed_test_data["product_1"]
    initial_stock = p1.stock_quantity
    user = seed_test_data["customer"]
    initial_points = user.loyalty_points

    # Place order
    res = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 2}]
    }, headers=customer_headers)
    assert res.status_code == 200
    order_id = res.json()["id"]
    final_amount = res.json()["final_amount"]
    earned_pts = int(final_amount * 0.1)

    db_session.refresh(p1)
    db_session.refresh(user)
    assert p1.stock_quantity == initial_stock - 2
    assert user.loyalty_points == initial_points + earned_pts

    # Customer cancels order
    res_cancel = client.post(f"/api/v1/orders/{order_id}/cancel", headers=customer_headers)
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "Cancelled"

    # Verify inventory was restored and points adjusted
    db_session.refresh(p1)
    db_session.refresh(user)
    assert p1.stock_quantity == initial_stock
    assert user.loyalty_points == initial_points

def test_customer_cancel_order_unauthorized(client, customer_headers, customer_b_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    order_id = res.json()["id"]

    # Bob attempts to cancel Alice's order -> 403 Forbidden
    res_cancel = client.post(f"/api/v1/orders/{order_id}/cancel", headers=customer_b_headers)
    assert res_cancel.status_code == 403

def test_customer_cancel_order_invalid_state(client, customer_headers, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    res = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)
    order_id = res.json()["id"]

    # Admin advances order to Baking
    client.put(f"/api/v1/admin/orders/{order_id}/status", json={"status": "Preparing"}, headers=admin_headers)
    client.put(f"/api/v1/admin/orders/{order_id}/status", json={"status": "Baking"}, headers=admin_headers)

    # Customer attempts to cancel after baking started -> 400 Bad Request
    res_cancel = client.post(f"/api/v1/orders/{order_id}/cancel", headers=customer_headers)
    assert res_cancel.status_code == 400
    assert "Baking has already started" in res_cancel.json()["detail"]

def test_admin_cancel_order_restores_inventory(client, customer_headers, admin_headers, seed_test_data, db_session):
    p1 = seed_test_data["product_1"]
    initial_stock = p1.stock_quantity

    res = client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 2}]
    }, headers=customer_headers)
    order_id = res.json()["id"]

    # Admin cancels order via status update
    res_cancel = client.put(f"/api/v1/admin/orders/{order_id}/status", json={"status": "Cancelled"}, headers=admin_headers)
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "Cancelled"

    # Inventory must be restored
    db_session.refresh(p1)
    assert p1.stock_quantity == initial_stock

def test_order_transaction_rollback_on_failure():
    session = TestingSessionLocal()
    try:
        user = User(
            full_name="Rollback Alice",
            email="rb_alice@test.com",
            hashed_password="secretpassword",
            role=RoleEnum.CUSTOMER.value,
            loyalty_points=100,
            is_active=True
        )
        cat = Category(name="Rollback Category", slug="rb-cat")
        session.add_all([user, cat])
        session.commit()

        prod = Product(
            name="Rollback Bread",
            slug="rb-bread",
            category_id=cat.id,
            description="Rollback test product",
            image_url="https://example.com/rb.jpg",
            price=150.0,
            stock_quantity=10,
            is_veg=True
        )
        session.add(prod)
        session.commit()

        p_id = prod.id
        u_id = user.id

        # Add cart item
        cart_item = CartItem(user_id=u_id, product_id=p_id, quantity=2)
        session.add(cart_item)
        session.commit()

        order_service = OrderService(
            order_repo=OrderRepository(session),
            product_repo=ProductRepository(session),
            cart_repo=CartRepository(session),
            user_repo=UserRepository(session),
            coupon_service=CouponService(None),
            payment_service=PaymentService(OrderRepository(session)),
            db=session
        )

        initial_orders_count = session.query(Order).count()

        # Force a failure inside the order creation transaction (e.g. during QR code generation)
        with patch("app.services.order_service.generate_qr_code", side_effect=RuntimeError("QR Generation Failed")):
            with pytest.raises(RuntimeError):
                order_service.create_order(
                    current_user=user,
                    order_in=OrderCreate(
                        order_type="Takeaway Pickup",
                        payment_method="Cash on Pickup"
                    )
                )

        # Verify atomic rollback:
        # 1. Product stock was NOT decremented
        fresh_prod = session.query(Product).filter(Product.id == p_id).first()
        assert fresh_prod.stock_quantity == 10
        # 2. No orphan order was created
        assert session.query(Order).count() == initial_orders_count
        # 3. Cart was NOT emptied
        cart_items = session.query(CartItem).filter(CartItem.user_id == u_id).all()
        assert len(cart_items) == 1
        assert cart_items[0].quantity == 2
        # 4. Loyalty points untouched
    finally:
        session.query(CartItem).filter(CartItem.user_id == u_id).delete()
        session.query(Product).filter(Product.id == p_id).delete()
        session.query(Category).filter(Category.slug == "rb-cat").delete()
        session.query(User).filter(User.id == u_id).delete()
        session.commit()
        session.close()

def test_unauthenticated_cannot_access_orders(client):
    assert client.post("/api/v1/orders/", json={}).status_code == 401
    assert client.get("/api/v1/orders/my-orders").status_code == 401
    assert client.get("/api/v1/orders/1").status_code == 401
    assert client.post("/api/v1/orders/1/cancel").status_code == 401

def test_admin_can_view_all_orders(client, admin_headers, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    client.post("/api/v1/orders/", json={
        "order_type": "Takeaway Pickup",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }, headers=customer_headers)

    res = client.get("/api/v1/admin/orders", headers=admin_headers)
    assert res.status_code == 200
    orders = res.json()
    assert len(orders) >= 1
    assert "items" in orders[0]
