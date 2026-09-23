# 🏛️ Sweet Crumbs Architecture & REST API Specification

## Architectural Overview
Sweet Crumbs Bakery is built using a clean, scalable **Layered Architecture** adhering to separation of concerns:

```text
[ Presentation Layer: React 19 + Vite SPA ]
                      │
           (HTTP / JSON + Bearer JWT)
                      ▼
[ API Routers (app/api/v1/) ]
   - Request validation (Pydantic v2)
   - Dependency injection & Auth guards
   - HTTP response codes
                      ▼
[ Business Logic Services (app/services/) ]
   - Price & coupon calculations (server-side authoritative)
   - Inventory availability & stock deduction
   - Cash-only payment enforcement
   - Order lifecycle state machine
                      ▼
[ Repositories (app/repositories/) ]
   - Data access abstraction
   - CRUD operations & query construction
                      ▼
[ SQLAlchemy 2.0 ORM (app/models/) ]
                      ▼
[ SQLite (Development) / PostgreSQL (Production) ]
```

---

## 📡 REST API Route Specifications

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register customer account & receive JWT | Public |
| `POST` | `/api/v1/auth/login` | Authenticate user & receive access token | Public |
| `POST` | `/api/v1/auth/login-form` | OAuth2 password request form authentication | Public |
| `GET` | `/api/v1/auth/me` | Fetch active logged-in user profile | Bearer JWT |
| `GET` | `/api/v1/categories` | List all 18 product categories | Public |
| `GET` | `/api/v1/products` | Query products with category, price & sort filters | Public |
| `GET` | `/api/v1/products/{id}` | Get product details, ingredients & stock | Public |
| `GET` | `/api/v1/products/recommendations/{id}` | Get AI recommended complimentary items | Public |
| `GET` | `/api/v1/banners` | Fetch active promotional banners | Public |
| `GET` | `/api/v1/products/{id}/reviews` | Fetch reviews for a product | Public |
| `POST` | `/api/v1/reviews` | Submit product review & update rating | Bearer JWT |
| `GET` | `/api/v1/user/cart` | Fetch active user cart items | Bearer JWT |
| `POST` | `/api/v1/user/cart` | Add item to cart with stock validation | Bearer JWT |
| `PUT` | `/api/v1/user/cart/{id}` | Update cart item quantity | Bearer JWT |
| `DELETE` | `/api/v1/user/cart/{id}` | Remove item from cart | Bearer JWT |
| `DELETE` | `/api/v1/user/cart-clear` | Clear all items from user cart | Bearer JWT |
| `GET` | `/api/v1/user/wishlist` | Fetch user wishlist products | Bearer JWT |
| `POST` | `/api/v1/user/wishlist/toggle/{product_id}` | Add or remove product from wishlist | Bearer JWT |
| `POST` | `/api/v1/user/coupon/validate` | Authoritative server coupon discount validation | Public |
| `POST` | `/api/v1/orders/` | Place order (Cash on Pickup / Delivery), deduct stock & generate QR | Bearer JWT |
| `GET` | `/api/v1/orders/my-orders` | Fetch user's order history (scoped to authenticated user) | Bearer JWT |
| `GET` | `/api/v1/orders/{id}` | Get order details & pickup QR code (user isolation enforced) | Bearer JWT / Admin |
| `GET` | `/api/v1/admin/analytics` | Fetch revenue metrics, order counts & sales charts | Admin Only |
| `GET` | `/api/v1/admin/orders` | Fetch all bakery orders | Admin Only |
| `PUT` | `/api/v1/admin/orders/{id}/status` | Transition order status through state machine | Admin Only |
| `PUT` | `/api/v1/admin/orders/{id}/payment` | Mark order payment status as PAID upon cash receipt | Admin Only |
| `POST` | `/api/v1/admin/products` | Create new product in inventory | Admin Only |
| `PUT` | `/api/v1/admin/products/{id}` | Update existing product details & inventory stock | Admin Only |
| `DELETE` | `/api/v1/admin/products/{id}` | Delete product from catalog | Admin Only |
| `GET` | `/api/v1/admin/users` | List all registered user accounts | Admin Only |

---

## 🔒 Security & User Isolation Architecture

1. **Password Security**: Passwords are never stored as plaintext; securely hashed using salted `bcrypt` and verified using constant-time comparison.
2. **JWT Authentication**: Centralized in `app.core.security`. Tokens encode user identity and role with standard expiration.
3. **Admin Authorization**: Enforced on the backend via `get_current_admin` dependency; front-end checks are strictly aesthetic.
4. **Data Isolation**: All user-owned data (Cart, Wishlist, Orders, Profile) requires token ownership. Accessing another user's order via `GET /api/v1/orders/{id}` returns `403 Forbidden` unless the caller has admin credentials.
5. **Authoritative Server Pricing**: Client prices sent in payloads are discarded. Subtotals, coupon discounts, and final totals are computed strictly from database prices.
6. **Cash Payment Guarantee**: Orders are locked to `payment_status = "Pending"`. Online payments are rejected. Only administrators can transition an order to `payment_status = "Paid"`.
