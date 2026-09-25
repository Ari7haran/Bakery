import pytest
from app.models import Review, Order, OrderItem, OrderStatusEnum, PaymentStatusEnum

def test_get_reviews_empty(client, seed_test_data):
    """Product with no reviews returns empty list."""
    p_id = seed_test_data["product_1"].id
    res = client.get(f"/api/v1/products/{p_id}/reviews")
    assert res.status_code == 200
    assert res.json() == []

def test_get_reviews_nonexistent_product(client):
    """Nonexistent product returns 404."""
    res = client.get("/api/v1/products/99999/reviews")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_get_reviews_invalid_product_id(client):
    """Negative or zero product ID returns 404 or 422."""
    res = client.get("/api/v1/products/0/reviews")
    assert res.status_code in [404, 422]

def test_create_review_unauthenticated(client, seed_test_data):
    """Unauthenticated user cannot create review."""
    p_id = seed_test_data["product_1"].id
    payload = {"product_id": p_id, "rating": 5, "comment": "Delicious!"}
    res = client.post("/api/v1/reviews", json=payload)
    assert res.status_code == 401

def test_create_review_authenticated(client, customer_headers, seed_test_data):
    """Authenticated user can create a review with rating and comment."""
    p_id = seed_test_data["product_1"].id
    payload = {"product_id": p_id, "rating": 5, "comment": "Absolutely fabulous sourdough!"}
    res = client.post("/api/v1/reviews", json=payload, headers=customer_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["product_id"] == p_id
    assert data["rating"] == 5
    assert data["comment"] == "Absolutely fabulous sourdough!"
    assert data["user"]["full_name"] == seed_test_data["customer"].full_name
    assert "password" not in data["user"]
    assert "email" not in data["user"]
    assert "phone" not in data["user"]

def test_create_review_via_product_path(client, customer_b_headers, seed_test_data):
    """Create review via POST /api/v1/products/{product_id}/reviews."""
    p_id = seed_test_data["product_1"].id
    payload = {"rating": 4, "comment": "Crispy crust and chewy crumb"}
    res = client.post(f"/api/v1/products/{p_id}/reviews", json=payload, headers=customer_b_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["product_id"] == p_id
    assert data["rating"] == 4
    assert data["comment"] == "Crispy crust and chewy crumb"

def test_rating_boundary_values(client, customer_headers, customer_b_headers, seed_test_data):
    """Valid rating 1 and 5 accepted."""
    p1_id = seed_test_data["product_1"].id
    p2_id = seed_test_data["product_2"].id

    res1 = client.post(
        f"/api/v1/products/{p1_id}/reviews",
        json={"rating": 1, "comment": "Burnt crust"},
        headers=customer_headers
    )
    assert res1.status_code == 201
    assert res1.json()["rating"] == 1

    res2 = client.post(
        f"/api/v1/products/{p2_id}/reviews",
        json={"rating": 5, "comment": "Golden perfection"},
        headers=customer_b_headers
    )
    assert res2.status_code == 201
    assert res2.json()["rating"] == 5

def test_invalid_rating_rejected(client, customer_headers, seed_test_data):
    """Rating 0, negative, > 5, or invalid types are rejected with 422."""
    p_id = seed_test_data["product_1"].id

    for invalid_rating in [0, -1, 6, 10, "five"]:
        res = client.post(
            f"/api/v1/products/{p_id}/reviews",
            json={"rating": invalid_rating, "comment": "Test"},
            headers=customer_headers
        )
        assert res.status_code == 422

def test_create_review_nonexistent_product(client, customer_headers):
    """Review creation for nonexistent product returns 404."""
    res = client.post(
        "/api/v1/products/99999/reviews",
        json={"rating": 5, "comment": "Does not exist"},
        headers=customer_headers
    )
    assert res.status_code == 404

def test_duplicate_review_rejected_409(client, customer_headers, seed_test_data):
    """Duplicate review by same user for same product rejected with 409 Conflict."""
    p_id = seed_test_data["product_1"].id
    payload = {"rating": 5, "comment": "First review"}

    res1 = client.post(f"/api/v1/products/{p_id}/reviews", json=payload, headers=customer_headers)
    assert res1.status_code == 201

    # Second attempt should be rejected with 409
    res2 = client.post(f"/api/v1/products/{p_id}/reviews", json=payload, headers=customer_headers)
    assert res2.status_code == 409
    assert "already reviewed" in res2.json()["detail"].lower()

def test_review_ownership_edit_by_owner(client, customer_headers, seed_test_data):
    """Review owner can edit rating and comment."""
    p_id = seed_test_data["product_1"].id
    res_create = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 3, "comment": "Average loaf"},
        headers=customer_headers
    )
    assert res_create.status_code == 201
    rev_id = res_create.json()["id"]

    # Owner edits review
    res_update = client.put(
        f"/api/v1/reviews/{rev_id}",
        json={"rating": 4, "comment": "Actually enjoyed it toasted with butter!"},
        headers=customer_headers
    )
    assert res_update.status_code == 200
    updated = res_update.json()
    assert updated["rating"] == 4
    assert updated["comment"] == "Actually enjoyed it toasted with butter!"

def test_review_ownership_edit_rejected_for_non_owner(client, customer_headers, customer_b_headers, seed_test_data):
    """User B cannot edit User A's review (403 Forbidden)."""
    p_id = seed_test_data["product_1"].id
    res_create = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 5, "comment": "Alice's review"},
        headers=customer_headers
    )
    rev_id = res_create.json()["id"]

    # Customer B attempts to edit Alice's review
    res_edit = client.put(
        f"/api/v1/reviews/{rev_id}",
        json={"rating": 1, "comment": "Hacked comment"},
        headers=customer_b_headers
    )
    assert res_edit.status_code == 403
    assert "not authorized" in res_edit.json()["detail"].lower()

def test_review_ownership_delete_rejected_for_non_owner(client, customer_headers, customer_b_headers, seed_test_data):
    """User B cannot delete User A's review (403 Forbidden)."""
    p_id = seed_test_data["product_1"].id
    res_create = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 5, "comment": "Alice's review"},
        headers=customer_headers
    )
    rev_id = res_create.json()["id"]

    res_del = client.delete(f"/api/v1/reviews/{rev_id}", headers=customer_b_headers)
    assert res_del.status_code == 403
    assert "not authorized" in res_del.json()["detail"].lower()

def test_admin_can_delete_any_review(client, customer_headers, admin_headers, seed_test_data):
    """Administrator can delete customer review."""
    p_id = seed_test_data["product_1"].id
    res_create = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 2, "comment": "Needs salt"},
        headers=customer_headers
    )
    rev_id = res_create.json()["id"]

    res_del = client.delete(f"/api/v1/reviews/{rev_id}", headers=admin_headers)
    assert res_del.status_code == 200
    assert res_del.json()["message"] == "Review deleted successfully"

    # Confirm it no longer appears in product reviews
    res_get = client.get(f"/api/v1/products/{p_id}/reviews")
    assert not any(r["id"] == rev_id for r in res_get.json())

def test_owner_can_delete_own_review(client, customer_headers, seed_test_data):
    """Customer can delete their own review."""
    p_id = seed_test_data["product_1"].id
    res_create = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 5, "comment": "Deleting later"},
        headers=customer_headers
    )
    rev_id = res_create.json()["id"]

    res_del = client.delete(f"/api/v1/reviews/{rev_id}", headers=customer_headers)
    assert res_del.status_code == 200

    # Ensure 404 when querying deleted review
    res_del_again = client.delete(f"/api/v1/reviews/{rev_id}", headers=customer_headers)
    assert res_del_again.status_code == 404

def test_aggregate_rating_calculation(client, customer_headers, customer_b_headers, admin_headers, seed_test_data):
    """Average rating and review count recalculate accurately across create, update, and delete."""
    p_id = seed_test_data["product_1"].id

    # 1. First review: 5 stars
    res1 = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 5, "comment": "Great"},
        headers=customer_headers
    )
    assert res1.status_code == 201
    prod1 = client.get(f"/api/v1/products/{p_id}").json()
    assert prod1["rating"] == 5.0
    assert prod1["review_count"] == 1

    # 2. Second review: 3 stars (Average should be (5+3)/2 = 4.0)
    res2 = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 3, "comment": "Okay"},
        headers=customer_b_headers
    )
    assert res2.status_code == 201
    prod2 = client.get(f"/api/v1/products/{p_id}").json()
    assert prod2["rating"] == 4.0
    assert prod2["review_count"] == 2

    # 3. Customer B updates review from 3 to 1 star (Average should be (5+1)/2 = 3.0)
    rev2_id = res2.json()["id"]
    res_update = client.put(
        f"/api/v1/reviews/{rev2_id}",
        json={"rating": 1},
        headers=customer_b_headers
    )
    assert res_update.status_code == 200
    prod3 = client.get(f"/api/v1/products/{p_id}").json()
    assert prod3["rating"] == 3.0
    assert prod3["review_count"] == 2

    # 4. Customer B deletes review (Average should return to 5.0, count to 1)
    res_del = client.delete(f"/api/v1/reviews/{rev2_id}", headers=customer_b_headers)
    assert res_del.status_code == 200
    prod4 = client.get(f"/api/v1/products/{p_id}").json()
    assert prod4["rating"] == 5.0
    assert prod4["review_count"] == 1

    # 5. Customer A deletes review (Count should be 0, rating 0.0)
    rev1_id = res1.json()["id"]
    client.delete(f"/api/v1/reviews/{rev1_id}", headers=customer_headers)
    prod5 = client.get(f"/api/v1/products/{p_id}").json()
    assert prod5["rating"] == 0.0
    assert prod5["review_count"] == 0

def test_sorting_and_pagination(client, customer_headers, customer_b_headers, seed_test_data):
    """Test newest, oldest, highest_rating, lowest_rating, skip, and limit."""
    p_id = seed_test_data["product_1"].id

    # Create 2 reviews
    client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 2, "comment": "First review"},
        headers=customer_headers
    )
    client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 5, "comment": "Second review"},
        headers=customer_b_headers
    )

    # Highest rating sort
    res_high = client.get(f"/api/v1/products/{p_id}/reviews?sort_by=highest_rating")
    assert res_high.status_code == 200
    ratings_high = [r["rating"] for r in res_high.json()]
    assert ratings_high == [5, 2]

    # Lowest rating sort
    res_low = client.get(f"/api/v1/products/{p_id}/reviews?sort_by=lowest_rating")
    assert res_low.status_code == 200
    ratings_low = [r["rating"] for r in res_low.json()]
    assert ratings_low == [2, 5]

    # Pagination: limit=1
    res_pag = client.get(f"/api/v1/products/{p_id}/reviews?limit=1&skip=0")
    assert res_pag.status_code == 200
    assert len(res_pag.json()) == 1

    # Invalid sort option
    res_inv = client.get(f"/api/v1/products/{p_id}/reviews?sort_by=random_sort")
    assert res_inv.status_code == 422

    # Invalid limit (< 1 or > 100)
    res_bad_lim = client.get(f"/api/v1/products/{p_id}/reviews?limit=0")
    assert res_bad_lim.status_code == 422
    res_bad_lim2 = client.get(f"/api/v1/products/{p_id}/reviews?limit=105")
    assert res_bad_lim2.status_code == 422

def test_security_user_id_spoofing_ignored(client, customer_headers, seed_test_data):
    """Client cannot spoof review ownership by passing arbitrary user_id."""
    p_id = seed_test_data["product_1"].id
    # Attempt to spoof user_id as admin (999 or seed_test_data['admin'].id)
    payload = {
        "product_id": p_id,
        "rating": 5,
        "comment": "Spoof attempt",
        "user_id": seed_test_data["admin"].id
    }
    res = client.post("/api/v1/reviews", json=payload, headers=customer_headers)
    assert res.status_code == 201
    data = res.json()
    # Must be owned by the authenticated customer (Alice), NOT the spoofed admin
    assert data["user_id"] == seed_test_data["customer"].id
    assert data["user"]["id"] == seed_test_data["customer"].id

def test_security_script_and_sql_injection_safe(client, customer_headers, seed_test_data):
    """SQL injection and HTML script tags are stored and retrieved safely as text without crashing or executing."""
    p_id = seed_test_data["product_1"].id
    payload = {
        "product_id": p_id,
        "rating": 4,
        "comment": "<script>alert('xss')</script> '; DROP TABLE reviews; --"
    }
    res = client.post("/api/v1/reviews", json=payload, headers=customer_headers)
    assert res.status_code == 201
    assert res.json()["comment"] == "<script>alert('xss')</script> '; DROP TABLE reviews; --"

def test_excessively_long_comment_rejected(client, customer_headers, seed_test_data):
    """Comments exceeding 2000 characters are rejected with 422."""
    p_id = seed_test_data["product_1"].id
    long_comment = "A" * 2005
    payload = {"product_id": p_id, "rating": 5, "comment": long_comment}
    res = client.post("/api/v1/reviews", json=payload, headers=customer_headers)
    assert res.status_code == 422

def test_whitespace_only_comment_handled(client, customer_headers, seed_test_data):
    """Whitespace-only comment is cleaned to empty string."""
    p_id = seed_test_data["product_1"].id
    payload = {"product_id": p_id, "rating": 5, "comment": "   \n\t   "}
    res = client.post("/api/v1/reviews", json=payload, headers=customer_headers)
    assert res.status_code == 201
    assert res.json()["comment"] == ""

def test_verified_purchase_indicator(client, customer_headers, db_session, seed_test_data):
    """When a customer has purchased the product, review shows is_verified_purchase=True."""
    p_id = seed_test_data["product_1"].id
    user_id = seed_test_data["customer"].id

    # Create an order with product_1 for customer
    order = Order(
        order_number="ORD-TEST-REV-01",
        user_id=user_id,
        total_amount=200.0,
        final_amount=200.0,
        status=OrderStatusEnum.COMPLETED.value,
        payment_status=PaymentStatusEnum.PAID.value
    )
    db_session.add(order)
    db_session.flush()

    item = OrderItem(
        order_id=order.id,
        product_id=p_id,
        quantity=1,
        price=200.0
    )
    db_session.add(item)
    db_session.commit()

    # Customer submits review
    res = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 5, "comment": "I bought this and loved it!"},
        headers=customer_headers
    )
    assert res.status_code == 201
    assert res.json()["is_verified_purchase"] is True

def test_update_review_rating_only(client, customer_headers, seed_test_data):
    """Updating only rating preserves original comment."""
    p_id = seed_test_data["product_1"].id
    res = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 2, "comment": "Original persistent comment"},
        headers=customer_headers
    )
    rev_id = res.json()["id"]

    res_up = client.put(f"/api/v1/reviews/{rev_id}", json={"rating": 4}, headers=customer_headers)
    assert res_up.status_code == 200
    assert res_up.json()["rating"] == 4
    assert res_up.json()["comment"] == "Original persistent comment"

def test_update_review_comment_only(client, customer_headers, seed_test_data):
    """Updating only comment preserves original rating."""
    p_id = seed_test_data["product_1"].id
    res = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 5, "comment": "Original comment"},
        headers=customer_headers
    )
    rev_id = res.json()["id"]

    res_up = client.put(f"/api/v1/reviews/{rev_id}", json={"comment": "Brand new comment"}, headers=customer_headers)
    assert res_up.status_code == 200
    assert res_up.json()["rating"] == 5
    assert res_up.json()["comment"] == "Brand new comment"

def test_update_review_invalid_rating_rejected(client, customer_headers, seed_test_data):
    """Invalid rating in update request rejected with 422."""
    p_id = seed_test_data["product_1"].id
    res = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 3, "comment": "Initial review"},
        headers=customer_headers
    )
    rev_id = res.json()["id"]

    for bad_rating in [0, 6, -1]:
        res_bad = client.put(f"/api/v1/reviews/{rev_id}", json={"rating": bad_rating}, headers=customer_headers)
        assert res_bad.status_code == 422

def test_update_review_empty_payload_rejected(client, customer_headers, seed_test_data):
    """Update review with no fields provided is rejected with 422."""
    p_id = seed_test_data["product_1"].id
    res = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 3, "comment": "Initial review"},
        headers=customer_headers
    )
    rev_id = res.json()["id"]

    res_empty = client.put(f"/api/v1/reviews/{rev_id}", json={}, headers=customer_headers)
    assert res_empty.status_code == 422

def test_update_nonexistent_review_returns_404(client, customer_headers):
    """Updating nonexistent review returns 404."""
    res = client.put("/api/v1/reviews/99999", json={"rating": 5}, headers=customer_headers)
    assert res.status_code == 404

def test_delete_nonexistent_review_returns_404(client, customer_headers):
    """Deleting nonexistent review returns 404."""
    res = client.delete("/api/v1/reviews/99999", headers=customer_headers)
    assert res.status_code == 404

def test_sorting_oldest_vs_newest(client, customer_headers, customer_b_headers, seed_test_data):
    """Verify newest returns reviews in descending order and oldest in ascending order."""
    p_id = seed_test_data["product_1"].id
    res1 = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 4, "comment": "First entered"},
        headers=customer_headers
    )
    res2 = client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 5, "comment": "Second entered"},
        headers=customer_b_headers
    )
    id1 = res1.json()["id"]
    id2 = res2.json()["id"]

    res_new = client.get(f"/api/v1/products/{p_id}/reviews?sort_by=newest")
    ids_new = [r["id"] for r in res_new.json()]
    assert ids_new == [id2, id1]

    res_old = client.get(f"/api/v1/products/{p_id}/reviews?sort_by=oldest")
    ids_old = [r["id"] for r in res_old.json()]
    assert ids_old == [id1, id2]

def test_pagination_skip_offset(client, customer_headers, customer_b_headers, seed_test_data):
    """Verify skip offsets the results properly."""
    p_id = seed_test_data["product_1"].id
    client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 3, "comment": "First"},
        headers=customer_headers
    )
    client.post(
        f"/api/v1/products/{p_id}/reviews",
        json={"rating": 4, "comment": "Second"},
        headers=customer_b_headers
    )

    all_res = client.get(f"/api/v1/products/{p_id}/reviews?limit=10&skip=0").json()
    assert len(all_res) == 2

    skip_res = client.get(f"/api/v1/products/{p_id}/reviews?limit=10&skip=1").json()
    assert len(skip_res) == 1
    assert skip_res[0]["id"] == all_res[1]["id"]

