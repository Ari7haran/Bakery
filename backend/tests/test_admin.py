import pytest
from app.models.order import Order, OrderStatusEnum, PaymentStatusEnum
from app.models.product import Product

def test_admin_analytics_basic(client, admin_headers):
    response = client.get("/api/v1/admin/analytics", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    # Backward compatible fields
    assert "total_revenue" in data
    assert "today_orders" in data
    assert "monthly_sales" in data
    assert "customer_count" in data
    assert "popular_products" in data
    assert "sales_chart" in data
    # Enhanced Step #14 fields
    assert "order_metrics" in data
    assert "revenue_metrics" in data
    assert "inventory_metrics" in data
    assert "customer_metrics" in data
    assert "status_breakdown" in data

def test_admin_analytics_unauthenticated(client):
    response = client.get("/api/v1/admin/analytics")
    assert response.status_code == 401

def test_admin_analytics_customer_forbidden(client, customer_headers):
    response = client.get("/api/v1/admin/analytics", headers=customer_headers)
    assert response.status_code == 403

def test_admin_analytics_empty_database(client, admin_headers):
    response = client.get("/api/v1/admin/analytics?period=today", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["total_revenue"], (int, float))
    assert isinstance(data["today_orders"], int)
    assert isinstance(data["popular_products"], list)
    assert isinstance(data["sales_chart"], list)

def test_admin_analytics_kpi_and_revenue_real_data(client, customer_headers, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]

    # 1. Place order 1 -> Paid & Completed
    order_1_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "04:00 PM - 04:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res1 = client.post("/api/v1/orders/", json=order_1_payload, headers=customer_headers)
    assert res1.status_code == 201
    o1_id = res1.json()["id"]
    # Admin marks order 1 as Paid and transitions to Completed
    client.put(f"/api/v1/admin/orders/{o1_id}/payment", headers=admin_headers)
    client.put(f"/api/v1/admin/orders/{o1_id}/status", json={"status": "Preparing"}, headers=admin_headers)
    client.put(f"/api/v1/admin/orders/{o1_id}/status", json={"status": "Baking"}, headers=admin_headers)
    client.put(f"/api/v1/admin/orders/{o1_id}/status", json={"status": "Packing"}, headers=admin_headers)
    client.put(f"/api/v1/admin/orders/{o1_id}/status", json={"status": "Ready for Pickup"}, headers=admin_headers)
    client.put(f"/api/v1/admin/orders/{o1_id}/status", json={"status": "Completed"}, headers=admin_headers)

    # 2. Place order 2 -> Received & Pending payment
    order_2_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "05:00 PM - 05:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 2}]
    }
    res2 = client.post("/api/v1/orders/", json=order_2_payload, headers=customer_headers)
    assert res2.status_code == 201

    # 3. Place order 3 -> Cancelled
    order_3_payload = {
        "order_type": "Takeaway Pickup",
        "pickup_date": "Today",
        "pickup_time_slot": "06:00 PM - 06:30 PM",
        "payment_method": "Cash on Pickup",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    res3 = client.post("/api/v1/orders/", json=order_3_payload, headers=customer_headers)
    assert res3.status_code == 201
    o3_id = res3.json()["id"]
    client.put(f"/api/v1/admin/orders/{o3_id}/status", json={"status": "Cancelled"}, headers=admin_headers)

    # Fetch analytics
    an_res = client.get("/api/v1/admin/analytics?period=all", headers=admin_headers)
    assert an_res.status_code == 200
    data = an_res.json()

    # Verify Revenue: strictly from completed/paid order 1, excluding unpaid order 2 and cancelled order 3
    expected_revenue = p1.price * 1
    assert data["total_revenue"] == expected_revenue
    assert data["revenue_metrics"]["total_revenue"] == expected_revenue
    assert data["revenue_metrics"]["average_order_value"] == expected_revenue

    # Verify Order Counts
    assert data["order_metrics"]["total_orders"] >= 3
    assert data["order_metrics"]["completed_orders"] >= 1
    assert data["order_metrics"]["cancelled_orders"] >= 1
    assert data["order_metrics"]["pending_orders"] >= 1

    # Verify Status Breakdown
    sb = data["status_breakdown"]
    assert sb["completed"] >= 1
    assert sb["cancelled"] >= 1
    assert sb["received"] >= 1

def test_admin_analytics_date_periods(client, admin_headers):
    for period in ["today", "7d", "30d", "this_month", "all"]:
        res = client.get(f"/api/v1/admin/analytics?period={period}", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["period"] == period

def test_admin_analytics_custom_date_range(client, admin_headers):
    # Valid custom range
    res = client.get(
        "/api/v1/admin/analytics?period=custom&start_date=2026-09-01&end_date=2026-09-26",
        headers=admin_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["period"] == "custom"
    assert data["start_date"] == "2026-09-01"
    assert data["end_date"] == "2026-09-26"

    # Missing start_date or end_date
    res_missing = client.get("/api/v1/admin/analytics?period=custom", headers=admin_headers)
    assert res_missing.status_code == 400

    # Inverted date range
    res_inv = client.get(
        "/api/v1/admin/analytics?period=custom&start_date=2026-09-26&end_date=2026-09-01",
        headers=admin_headers
    )
    assert res_inv.status_code == 400

    # Malformed date
    res_bad = client.get(
        "/api/v1/admin/analytics?period=custom&start_date=not-a-date&end_date=2026-09-26",
        headers=admin_headers
    )
    assert res_bad.status_code == 400

def test_admin_analytics_inventory_metrics(client, admin_headers, seed_test_data, db_session):
    p1 = seed_test_data["product_1"]
    p2 = seed_test_data["product_2"]

    # Set p1 to out-of-stock (0) and p2 to low-stock (3)
    p1.stock_quantity = 0
    p2.stock_quantity = 3
    db_session.commit()

    res = client.get("/api/v1/admin/analytics", headers=admin_headers)
    assert res.status_code == 200
    inv = res.json()["inventory_metrics"]
    assert inv["out_of_stock_products"] >= 1
    assert inv["low_stock_products"] >= 1

    attention_items = inv["items_requiring_attention"]
    assert len(attention_items) >= 2
    item_names = [item["name"] for item in attention_items]
    assert p1.name in item_names
    assert p2.name in item_names

def test_admin_analytics_customer_metrics(client, admin_headers, seed_test_data):
    res = client.get("/api/v1/admin/analytics", headers=admin_headers)
    assert res.status_code == 200
    cm = res.json()["customer_metrics"]
    assert cm["total_customers"] >= 1
    assert isinstance(cm["top_customers"], list)

def test_admin_analytics_sub_endpoints(client, admin_headers):
    # Overview
    res_ov = client.get("/api/v1/admin/analytics/overview", headers=admin_headers)
    assert res_ov.status_code == 200
    assert "total_revenue" in res_ov.json()

    # Inventory
    res_inv = client.get("/api/v1/admin/analytics/inventory", headers=admin_headers)
    assert res_inv.status_code == 200
    assert "total_products" in res_inv.json()
    assert "items_requiring_attention" in res_inv.json()

    # Orders
    res_ord = client.get("/api/v1/admin/analytics/orders", headers=admin_headers)
    assert res_ord.status_code == 200
    assert "total_orders" in res_ord.json()

    # Customers
    res_cust = client.get("/api/v1/admin/analytics/customers", headers=admin_headers)
    assert res_cust.status_code == 200
    assert "total_customers" in res_cust.json()

def test_admin_analytics_customer_forbidden_sub_endpoints(client, customer_headers):
    assert client.get("/api/v1/admin/analytics/overview", headers=customer_headers).status_code == 403
    assert client.get("/api/v1/admin/analytics/inventory", headers=customer_headers).status_code == 403
    assert client.get("/api/v1/admin/analytics/orders", headers=customer_headers).status_code == 403
    assert client.get("/api/v1/admin/analytics/customers", headers=customer_headers).status_code == 403

def test_admin_mark_payment_paid(client, customer_headers, admin_headers, seed_test_data):
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
    assert res_order.json()["payment_status"] == "Pending"

    # Customer tries to mark as paid via admin endpoint -> 403 Forbidden
    res_cust = client.put(f"/api/v1/admin/orders/{order_id}/payment", headers=customer_headers)
    assert res_cust.status_code == 403

    # Admin marks as paid -> 200 OK
    res_admin = client.put(f"/api/v1/admin/orders/{order_id}/payment", headers=admin_headers)
    assert res_admin.status_code == 200
    assert res_admin.json()["payment_status"] == "Paid"
