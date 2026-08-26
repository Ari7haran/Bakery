# 🏛️ Sweet Crumbs Architecture & REST API Specification

## Architectural Overview
Sweet Crumbs Bakery is built using **Clean Layered Architecture** with distinct domain separation:

1. **Presentation Layer**: React 19 + TypeScript + Vite SPA, styled with custom Tailwind tokens and Framer Motion micro-interactions. State is managed via Context API and TanStack Query.
2. **API Layer**: FastAPI asynchronous endpoints structured under `routers/`, providing automatic OpenAPI/Swagger documentation, JSON serialization via Pydantic v2 schemas, and dependency injection for SQLAlchemy DB sessions.
3. **Domain & Data Layer**: SQLAlchemy 2.0 ORM with SQLite (development) and PostgreSQL/Docker (production) database drivers.

```text
[ React 19 Single Page App ] ──(REST API JSON + Bearer JWT)──> [ FastAPI Router Layer ]
                                                                       │
                                                            [ Pydantic Schemas ]
                                                                       │
                                                            [ Service & Repository ]
                                                                       │
                                                            [ SQLAlchemy ORM ]
                                                                       │
                                                            [ SQLite / PostgreSQL DB ]
```

---

## 📡 REST API Route Specifications

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register customer account & receive JWT | Public |
| `POST` | `/api/v1/auth/login` | Authenticate user & receive access token | Public |
| `GET` | `/api/v1/auth/me` | Fetch active logged-in user profile | Bearer JWT |
| `GET` | `/api/v1/categories` | List all 18 product categories | Public |
| `GET` | `/api/v1/products` | Query products with category, price & sort filters | Public |
| `GET` | `/api/v1/products/{id}` | Get product details, ingredients & stock | Public |
| `GET` | `/api/v1/products/recommendations/{id}` | Get AI recommended complimentary items | Public |
| `GET` | `/api/v1/user/cart` | Fetch active user cart items | Bearer JWT |
| `POST` | `/api/v1/user/cart` | Add item to cart | Bearer JWT |
| `POST` | `/api/v1/user/coupon/validate` | Validate promo code discount | Public |
| `POST` | `/api/v1/orders/` | Place takeaway pickup/delivery order & generate QR | Bearer JWT |
| `GET` | `/api/v1/orders/my-orders` | Fetch user's past order history | Bearer JWT |
| `GET` | `/api/v1/orders/{id}` | Get live tracking timeline & pickup QR code | Bearer JWT / Admin |
| `GET` | `/api/v1/admin/analytics` | Fetch revenue metrics & Recharts sales data | Admin Only |
| `GET` | `/api/v1/admin/orders` | Fetch all system orders | Admin Only |
| `PUT` | `/api/v1/admin/orders/{id}/status` | Update order status (*Baking, Packing, Ready*) | Admin Only |
| `POST` | `/api/v1/admin/products` | Create new product in inventory | Admin Only |
