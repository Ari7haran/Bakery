# 🥐 Sweet Crumbs Bakery E-Commerce Application

Sweet Crumbs Bakery is a production-grade full-stack e-commerce web platform built with **Python FastAPI** and **React + JavaScript + Vite + Tailwind CSS**.

It enables bakery customers to browse freshly baked sourdoughs, custom celebration cakes, and warm snacks, schedule express takeaway pickup time slots, generate QR counter pickup codes, and track live baking timeline status in real-time.

---

## 🌟 Key Features

### 🛍️ Customer Features
- **Modern Bakery UI**: High aesthetic design with cream, brown, chocolate & terracotta orange palette, dark mode toggle, and responsive layouts.
- **Express Takeaway Pickup**: Pick custom dates & time slots for counter collection with instant QR code receipts.
- **Doorstep Delivery**: Order warm bakery delicacies delivered to your home.
- **Cash-Only Fulfillment**: Safe, cash-on-pickup and cash-on-delivery workflows.
- **AI Product Recommendations**: Dynamic suggestions for complimentary snacks, beverages, and frequently bought together items.
- **Product Catalog**: 18 product categories (Bread, Cookies, Pastries, Cupcakes, Birthday Cakes, Pizzas, Combos, etc.) with Veg/Eggless indicators, price filters, and instant search.
- **Live Order Tracking**: Visual timeline tracking from *Order Received → Preparing → Baking → Packing → Ready for Counter Pickup → Completed*.
- **Loyalty Rewards**: Earn VIP points on every purchase (10% of order value) & redeemable coupons.

### 🛡️ Admin Management
- **Dashboard Analytics**: Gross revenue, order volume, monthly sales, customer metrics, and sales charts.
- **Order Pipeline & State Transitions**: Controlled state machine (*Received → Preparing → Baking → Packing → Ready for Pickup → Completed*).
- **Cash Payment Reconciliation**: Explicit administrative control to mark orders as PAID upon cash receipt (`PUT /api/v1/admin/orders/{id}/payment`).
- **Product & Category CRUD**: Manage inventory levels, stock quantities, prices, descriptions, and add new items.

---

## 🏗️ Production Backend Architecture

The backend follows a clean, decoupled **Router → Service → Repository → SQLAlchemy → Database** architecture:

```text
backend/
├── app/
│   ├── main.py                         # App factory, CORS, exception handlers, router registration
│   │
│   ├── core/                           # System Core
│   │   ├── config.py                   # Pydantic Settings reading from .env
│   │   ├── database.py                 # Engine, SessionLocal, Base, get_db dependency
│   │   ├── security.py                 # Password hashing (bcrypt) & JWT encoding/decoding
│   │   ├── dependencies.py             # Auth dependencies (get_current_user, get_current_admin)
│   │   └── exceptions.py               # Custom domain exceptions & handlers
│   │
│   ├── models/                         # Domain-separated SQLAlchemy ORM Models
│   │   ├── __init__.py                 # Re-exports all models
│   │   ├── all_models.py               # Backward-compatible facade
│   │   ├── user.py                     # User, Address, RoleEnum
│   │   ├── product.py                  # Product, ProductImage
│   │   ├── category.py                 # Category
│   │   ├── cart.py                     # CartItem, WishlistItem
│   │   ├── order.py                    # Order, OrderItem, Status & Payment Enums
│   │   ├── coupon.py                   # Coupon
│   │   ├── review.py                   # Review
│   │   └── banner.py                   # Banner
│   │
│   ├── schemas/                        # Domain-separated Pydantic Schemas
│   │   ├── __init__.py                 # Re-exports all schemas
│   │   ├── schemas.py                  # Backward-compatible facade
│   │   ├── auth.py                     # Token, UserLogin, UserRegister
│   │   ├── user.py                     # UserOut
│   │   ├── product.py                  # ProductBase, ProductOut, ProductImageOut
│   │   ├── category.py                 # CategoryBase, CategoryOut
│   │   ├── cart.py                     # CartItemAdd, CartItemUpdate, CartItemOut
│   │   ├── order.py                    # OrderItemInput, OrderCreate, OrderOut, StatusUpdates
│   │   ├── coupon.py                   # CouponApply, CouponOut, CouponValidationResult
│   │   ├── review.py                   # ReviewCreate, ReviewOut
│   │   └── analytics.py                # AnalyticsOut
│   │
│   ├── repositories/                   # Data Access Layer (Pure SQLAlchemy queries)
│   │   ├── base_repository.py          # Generic CRUD repository
│   │   ├── user_repository.py          # User persistence & lookups
│   │   ├── product_repository.py       # Catalog queries, filters & stock deduction
│   │   ├── category_repository.py      # Category lookups
│   │   ├── cart_repository.py          # Cart & wishlist scoped queries
│   │   ├── order_repository.py          # Order creation & analytics aggregation
│   │   ├── coupon_repository.py        # Coupon lookup
│   │   ├── review_repository.py        # Product reviews
│   │   └── banner_repository.py        # Active promotional banners
│   │
│   ├── services/                       # Business Logic Layer
│   │   ├── auth_service.py             # User registration, authentication, JWT issuance
│   │   ├── product_service.py          # Catalog logic, AI recommendations, reviews
│   │   ├── cart_service.py             # Cart validation, stock availability, wishlist
│   │   ├── coupon_service.py           # Expiry check, order minimums, discount cap calculation
│   │   ├── payment_service.py          # Cash-only rule enforcement, admin payment status updates
│   │   ├── order_service.py            # Server pricing, atomic stock deduction, state transitions
│   │   └── admin_service.py            # Analytics compilation & user management
│   │
│   ├── api/
│   │   ├── router.py                   # Master API router for /api/v1
│   │   └── v1/                         # Slim HTTP endpoints
│   │       ├── auth.py
│   │       ├── products.py
│   │       ├── cart.py
│   │       ├── orders.py
│   │       ├── reviews.py
│   │       └── admin.py
│   │
│   ├── database/
│   │   └── session.py                  # Backward-compatible re-export from core.database
│   │
│   └── utils/
│       ├── qr_code.py                  # Order number, pickup ID & QR code image generator
│       └── seed_data.py                # Database seeder
│
├── tests/                              # Automated Pytest Suite
│   ├── conftest.py                     # In-memory test DB, test client & auth fixtures
│   ├── test_auth.py                    # Auth, tokens, admin protection
│   ├── test_products.py                # Catalog, search, filters, recommendations
│   ├── test_cart.py                    # Cart limits, user isolation, coupons
│   ├── test_orders.py                  # Order creation, cash flow, stock deduction, lifecycle
│   └── test_admin.py                   # Analytics, order management, payment updates
│
├── .env.example
├── requirements.txt
└── sweet_crumbs.db
```

---

## 💳 Cash-Only Payment Architecture

Sweet Crumbs Bakery is strictly a **CASH ONLY** bakery:
1. **Allowed Methods**: `"Cash on Pickup"` and `"Cash on Delivery"`.
2. **Online Payment Rejection**: If a client attempts to submit `"Online Payment"`, `"Card"`, or `"UPI"`, the backend returns `400 Bad Request`.
3. **Immutable Customer Status**: The backend authoritatively assigns `payment_status = "Pending"`. Customers cannot mark orders as paid.
4. **Admin Reconciliation**: Only authorized staff/admin can mark payment as `"Paid"` upon receiving cash at the counter or via delivery courier (`PUT /api/v1/admin/orders/{id}/payment`).

---

## 🔄 Order Lifecycle State Machine

Order state transitions follow a strictly controlled state machine:
- `Received` → `Preparing` (or `Cancelled`)
- `Preparing` → `Baking` (or `Cancelled`)
- `Baking` → `Packing` (or `Cancelled`)
- `Packing` → `Ready for Pickup` (or `Cancelled`)
- `Ready for Pickup` → `Completed` (or `Cancelled`)
- Once `Completed` or `Cancelled`, no further status changes are permitted.
- Transitioning to `Completed` automatically marks payment as `Paid`.

---

## 🚀 How to Run Locally

### 1. Run Backend (FastAPI)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Root Healthcheck: `http://localhost:8000/`

### 2. Run Automated Tests
```powershell
cd backend
.\venv\Scripts\python -m pytest tests -v
```

### 3. Run Frontend (React Vite)
```powershell
cd frontend
npm run dev
```
- Frontend Application: `http://localhost:5173`

---

## 🔑 Demo Account Credentials

- **Admin Account**: `admin@sweetcrumbs.com` / `admin123`
- **Customer Account**: `sarah@example.com` / `customer123`
