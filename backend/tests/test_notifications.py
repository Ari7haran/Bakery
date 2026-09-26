import pytest
from app.models.notification import Notification, NotificationTypeEnum, NotificationPriorityEnum
from app.models.user import User
from app.models.product import Product

# ==============================================================================
# 1. Basic Notification Operations
# ==============================================================================

def test_list_notifications_empty(client, customer_headers):
    res = client.get("/api/v1/notifications/", headers=customer_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["unread_count"] == 0

def test_create_and_list_notifications(client, customer_headers, seed_test_data, db_session):
    cust = seed_test_data["customer"]
    
    n1 = Notification(
        user_id=cust.id,
        title="Test Notification 1",
        message="Message 1",
        notification_type=NotificationTypeEnum.SYSTEM.value,
        priority=NotificationPriorityEnum.NORMAL.value,
        is_read=False
    )
    n2 = Notification(
        user_id=cust.id,
        title="Test Notification 2",
        message="Message 2",
        notification_type=NotificationTypeEnum.ORDER_STATUS.value,
        priority=NotificationPriorityEnum.HIGH.value,
        is_read=True
    )
    db_session.add_all([n1, n2])
    db_session.commit()

    # List all
    res = client.get("/api/v1/notifications/", headers=customer_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert data["unread_count"] == 1
    assert len(data["items"]) == 2

    # Filter unread
    res_unread = client.get("/api/v1/notifications/?is_read=false", headers=customer_headers)
    assert res_unread.status_code == 200
    assert res_unread.json()["total"] == 1
    assert res_unread.json()["items"][0]["title"] == "Test Notification 1"

def test_get_unread_count(client, customer_headers, seed_test_data, db_session):
    cust = seed_test_data["customer"]
    
    # 0 initially
    res0 = client.get("/api/v1/notifications/unread-count", headers=customer_headers)
    assert res0.status_code == 200
    assert res0.json()["unread_count"] == 0

    # Add 2 unread
    n1 = Notification(user_id=cust.id, title="A", message="A", is_read=False)
    n2 = Notification(user_id=cust.id, title="B", message="B", is_read=False)
    db_session.add_all([n1, n2])
    db_session.commit()

    res2 = client.get("/api/v1/notifications/unread-count", headers=customer_headers)
    assert res2.status_code == 200
    assert res2.json()["unread_count"] == 2

def test_mark_notification_as_read(client, customer_headers, seed_test_data, db_session):
    cust = seed_test_data["customer"]
    notif = Notification(user_id=cust.id, title="Unread", message="Unread text", is_read=False)
    db_session.add(notif)
    db_session.commit()

    res = client.put(f"/api/v1/notifications/{notif.id}/read", headers=customer_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_read"] is True
    assert data["read_at"] is not None

    # Verify unread count is now 0
    res_count = client.get("/api/v1/notifications/unread-count", headers=customer_headers)
    assert res_count.json()["unread_count"] == 0

def test_mark_all_notifications_as_read(client, customer_headers, seed_test_data, db_session):
    cust = seed_test_data["customer"]
    n1 = Notification(user_id=cust.id, title="N1", message="N1", is_read=False)
    n2 = Notification(user_id=cust.id, title="N2", message="N2", is_read=False)
    n3 = Notification(user_id=cust.id, title="N3", message="N3", is_read=True)
    db_session.add_all([n1, n2, n3])
    db_session.commit()

    res = client.put("/api/v1/notifications/mark-all-read", headers=customer_headers)
    assert res.status_code == 200
    assert res.json()["updated_count"] == 2

    # Verify unread count is 0
    res_count = client.get("/api/v1/notifications/unread-count", headers=customer_headers)
    assert res_count.json()["unread_count"] == 0

def test_delete_notification(client, customer_headers, seed_test_data, db_session):
    cust = seed_test_data["customer"]
    notif = Notification(user_id=cust.id, title="To Delete", message="Bye", is_read=False)
    db_session.add(notif)
    db_session.commit()

    res = client.delete(f"/api/v1/notifications/{notif.id}", headers=customer_headers)
    assert res.status_code == 200
    assert "dismissed" in res.json()["message"]

    # Verify gone from list
    res_list = client.get("/api/v1/notifications/", headers=customer_headers)
    assert res_list.json()["total"] == 0

# ==============================================================================
# 2. Security, Authentication & IDOR Protection
# ==============================================================================

def test_unauthenticated_access_rejected(client):
    assert client.get("/api/v1/notifications/").status_code == 401
    assert client.get("/api/v1/notifications/unread-count").status_code == 401
    assert client.put("/api/v1/notifications/1/read").status_code == 401
    assert client.put("/api/v1/notifications/mark-all-read").status_code == 401
    assert client.delete("/api/v1/notifications/1").status_code == 401

def test_user_isolation_list(client, customer_headers, customer_b_headers, seed_test_data, db_session):
    cust_a = seed_test_data["customer"]
    cust_b = seed_test_data["customer_b"]

    notif_a = Notification(user_id=cust_a.id, title="For Alice Only", message="Secret A")
    notif_b = Notification(user_id=cust_b.id, title="For Bob Only", message="Secret B")
    db_session.add_all([notif_a, notif_b])
    db_session.commit()

    # Alice only sees notif_a
    res_a = client.get("/api/v1/notifications/", headers=customer_headers)
    items_a = res_a.json()["items"]
    assert len(items_a) == 1
    assert items_a[0]["title"] == "For Alice Only"

    # Bob only sees notif_b
    res_b = client.get("/api/v1/notifications/", headers=customer_b_headers)
    items_b = res_b.json()["items"]
    assert len(items_b) == 1
    assert items_b[0]["title"] == "For Bob Only"

def test_idor_mark_read_forbidden(client, customer_b_headers, seed_test_data, db_session):
    cust_a = seed_test_data["customer"]
    notif_a = Notification(user_id=cust_a.id, title="Alice Notif", message="Text", is_read=False)
    db_session.add(notif_a)
    db_session.commit()

    # Bob attempts to mark Alice's notification as read -> 404 (IDOR protected)
    res = client.put(f"/api/v1/notifications/{notif_a.id}/read", headers=customer_b_headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Notification not found"

    # Alice's notification remains unread
    db_session.refresh(notif_a)
    assert notif_a.is_read is False

def test_idor_delete_forbidden(client, customer_b_headers, seed_test_data, db_session):
    cust_a = seed_test_data["customer"]
    notif_a = Notification(user_id=cust_a.id, title="Alice Notif", message="Text")
    db_session.add(notif_a)
    db_session.commit()

    # Bob attempts to delete Alice's notification -> 404 (IDOR protected)
    res = client.delete(f"/api/v1/notifications/{notif_a.id}", headers=customer_b_headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Notification not found"

    # Alice's notification still exists in DB
    db_session.refresh(notif_a)
    assert notif_a.id is not None

# ==============================================================================
# 3. Business Events Integration
# ==============================================================================

def test_order_creation_triggers_customer_and_admin_notifications(client, customer_headers, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]

    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Tomorrow",
        "pickup_time_slot": "05:00 PM - 05:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }

    res_order = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    assert res_order.status_code == 200
    order_data = res_order.json()

    # Check Customer notifications
    res_cust = client.get("/api/v1/notifications/", headers=customer_headers)
    assert res_cust.status_code == 200
    cust_items = res_cust.json()["items"]
    assert len(cust_items) >= 1
    confirm_notif = next((n for n in cust_items if order_data["order_number"] in n["title"]), None)
    assert confirm_notif is not None
    assert confirm_notif["notification_type"] == "order_created"
    assert confirm_notif["related_entity_id"] == order_data["id"]

    # Check Admin notifications
    res_admin = client.get("/api/v1/notifications/", headers=admin_headers)
    assert res_admin.status_code == 200
    admin_items = res_admin.json()["items"]
    admin_notif = next((n for n in admin_items if order_data["order_number"] in n["title"]), None)
    assert admin_notif is not None
    assert admin_notif["notification_type"] == "order_created"
    assert admin_notif["priority"] == "high"

def test_order_status_update_and_ready_for_pickup(client, customer_headers, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res_order = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    order_id = res_order.json()["id"]

    # State transitions: Received -> Preparing -> Baking -> Packing -> Ready for Pickup
    for next_status in ["Preparing", "Baking", "Packing", "Ready for Pickup"]:
        res_trans = client.put(
            f"/api/v1/admin/orders/{order_id}/status",
            json={"status": next_status},
            headers=admin_headers
        )
        assert res_trans.status_code == 200

    # Customer should have notifications for all transitions
    res_notif = client.get("/api/v1/notifications/", headers=customer_headers)
    items = res_notif.json()["items"]

    # Check for "Ready for Pickup" urgent notification
    ready_notif = next((n for n in items if "Ready for Counter Pickup" in n["title"]), None)
    assert ready_notif is not None
    assert ready_notif["priority"] == "urgent"
    assert ready_notif["notification_type"] == "order_status"

def test_order_cancellation_triggers_notification(client, customer_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res_order = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    order_id = res_order.json()["id"]

    # Cancel order
    res_cancel = client.post(f"/api/v1/orders/{order_id}/cancel", headers=customer_headers)
    assert res_cancel.status_code == 200

    # Verify cancellation notification
    res_notif = client.get("/api/v1/notifications/", headers=customer_headers)
    cancel_notif = next((n for n in res_notif.json()["items"] if "Cancelled" in n["title"]), None)
    assert cancel_notif is not None
    assert cancel_notif["notification_type"] == "order_cancelled"

def test_payment_reconciliation_triggers_notification(client, customer_headers, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    order_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res_order = client.post("/api/v1/orders/", json=order_payload, headers=customer_headers)
    order_id = res_order.json()["id"]

    # Admin marks payment as Paid
    res_pay = client.put(f"/api/v1/admin/orders/{order_id}/payment", headers=admin_headers)
    assert res_pay.status_code == 200

    # Customer receives payment confirmation
    res_notif = client.get("/api/v1/notifications/", headers=customer_headers)
    pay_notif = next((n for n in res_notif.json()["items"] if "Payment Received" in n["title"]), None)
    assert pay_notif is not None
    assert pay_notif["notification_type"] == "payment"

def test_low_stock_notification_for_admin(client, admin_headers, seed_test_data):
    p2 = seed_test_data["product_2"]  # initial stock is 5
    
    # Update stock to 3 (<= 5 threshold)
    res_stock = client.put(
        f"/api/v1/admin/products/{p2.id}/stock",
        json={"stock_quantity": 3},
        headers=admin_headers
    )
    assert res_stock.status_code == 200

    # Verify admin received low stock alert
    res_admin = client.get("/api/v1/notifications/", headers=admin_headers)
    alert_notif = next((n for n in res_admin.json()["items"] if "Low Stock Alert" in n["title"]), None)
    assert alert_notif is not None
    assert alert_notif["notification_type"] == "inventory"

# ==============================================================================
# 4. Validation & Edge Cases
# ==============================================================================

def test_invalid_notification_id_404(client, customer_headers):
    assert client.put("/api/v1/notifications/99999/read", headers=customer_headers).status_code == 404
    assert client.delete("/api/v1/notifications/99999", headers=customer_headers).status_code == 404

def test_pagination_validation(client, customer_headers):
    # Negative skip
    assert client.get("/api/v1/notifications/?skip=-1", headers=customer_headers).status_code == 422
    # Limit > 100
    assert client.get("/api/v1/notifications/?limit=101", headers=customer_headers).status_code == 422
    # Limit 0
    assert client.get("/api/v1/notifications/?limit=0", headers=customer_headers).status_code == 422

def test_mark_all_read_when_empty(client, customer_headers):
    res = client.put("/api/v1/notifications/mark-all-read", headers=customer_headers)
    assert res.status_code == 200
    assert res.json()["updated_count"] == 0

def test_mark_as_read_idempotent(client, customer_headers, seed_test_data, db_session):
    cust = seed_test_data["customer"]
    notif = Notification(user_id=cust.id, title="Test", message="Test", is_read=False)
    db_session.add(notif)
    db_session.commit()

    # First mark as read
    res1 = client.put(f"/api/v1/notifications/{notif.id}/read", headers=customer_headers)
    assert res1.status_code == 200
    assert res1.json()["is_read"] is True

    # Second mark as read (idempotent, succeeds)
    res2 = client.put(f"/api/v1/notifications/{notif.id}/read", headers=customer_headers)
    assert res2.status_code == 200
    assert res2.json()["is_read"] is True
