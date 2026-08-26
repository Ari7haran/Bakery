# 🥐 Sweet Crumbs Bakery E-Commerce Application

Sweet Crumbs Bakery is an enterprise-grade full-stack e-commerce web platform built with **Python FastAPI** and **React 19 + TypeScript + Vite + Tailwind CSS**.

It enables bakery customers to browse freshly baked sourdoughs, custom celebration cakes, and warm snacks, schedule express takeaway pickup time slots, generate QR counter pickup codes, and track live baking timeline status in real-time.

---

## 🌟 Key Features

### 🛍️ Customer Features
- **Modern Bakery UI**: High aesthetic design with cream, brown, chocolate & terracotta orange palette, dark mode toggle, and glassmorphism.
- **Express Takeaway Pickup**: Pick custom dates & time slots for counter collection with instant QR code receipts.
- **AI Product Recommendations**: Dynamic suggestions for complimentary snacks, beverages, and frequently bought together bakery items.
- **Product Catalog**: 18 product categories (Bread, Cookies, Pastries, Cupcakes, Birthday Cakes, Pizzas, Combos, etc.) with Veg/Eggless indicators, price filters, and instant search.
- **Live Order Tracking**: Visual timeline tracking from *Order Received → Preparing → Baking → Packing → Ready for Counter Pickup → Completed*.
- **Loyalty Rewards**: Earn VIP points on every purchase (10 points per ₹100 spent) & redeemable birthday coupons.

### 🛡️ Admin Management
- **Dashboard Analytics**: Gross revenue, order volume, monthly sales, customer metrics, and Recharts weekly sales line charts.
- **Order Pipeline**: Live status switcher (*Received, Baking, Packing, Ready for Pickup, Completed*).
- **Product & Category CRUD**: Manage inventory levels, prices, descriptions, and add new items with live image previews.

---

## 🏗️ Clean Architecture & Tech Stack

```text
c:\Ariharan\bakery\
├── backend/
│   ├── app/
│   │   ├── core/           # Config, JWT Security, Tokens
│   │   ├── database/       # SQLAlchemy Session & Base
│   │   ├── models/         # ORM Models (User, Product, Order, Cart, Review, etc.)
│   │   ├── schemas/        # Pydantic Schemas for Validation
│   │   ├── routers/        # FastAPI API Endpoints (Auth, Products, Cart, Orders, Admin)
│   │   └── utils/          # Seed data & QR Code generation
│   ├── main.py             # App Initialization & Global Error Handler
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/     # Navbar, Footer, ProductCard, CartDrawer, PickupModal
│   │   ├── context/        # AuthContext, CartContext, ThemeContext
│   │   ├── pages/          # Home, Shop, ProductDetail, Checkout, Track, Profile, Admin
│   │   ├── services/       # Axios client & JWT interceptors
│   │   └── types/          # TypeScript interface definitions
│   ├── index.css           # Design tokens & Glassmorphism styles
│   └── vite.config.ts
├── docker-compose.yml
├── ARCHITECTURE.md
└── ER_DIAGRAM.md
```

---

## 🚀 How to Run Locally

### 1. Run Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Interactive OpenAPI Swagger UI out of the box.

### 2. Run Frontend (React Vite)
```bash
cd frontend
npm install
npm run dev
```
- Frontend Application: `http://localhost:5173`

---

## 🔑 Demo Account Credentials

- **Admin Account**: `admin@sweetcrumbs.com` / `admin123`
- **Customer Account**: `sarah@example.com` / `customer123`
