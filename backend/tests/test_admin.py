def test_admin_analytics(client, admin_headers):
    response = client.get("/api/v1/admin/analytics", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "today_orders" in data
    assert "monthly_sales" in data
    assert "customer_count" in data
    assert "popular_products" in data
    assert "sales_chart" in data

def test_admin_mark_payment_paid(client, customer_headers, admin_headers, seed_test_data):
    p1 = seed_test_data["product_1"]
    # Customer places order
    order_payload = {
        "order_type": "Takeaway Pickup",
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
