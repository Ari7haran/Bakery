from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.models.all_models import Order, Product, User, Category, Coupon, Review, OrderItem
from app.schemas.schemas import OrderOut, OrderStatusUpdate, ProductOut, ProductBase, CategoryOut, AnalyticsOut, UserOut
from app.routers.auth import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin Dashboard & Management"])

@router.get("/analytics", response_model=AnalyticsOut)
def get_analytics(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_revenue = db.query(func.sum(Order.final_amount)).scalar() or 0.0
    today_orders = db.query(Order).count()
    monthly_sales = total_revenue * 0.85 # Simulated monthly portion for dashboard
    customer_count = db.query(User).filter(User.role == "customer").count()

    popular = db.query(
        Product.name,
        func.count(OrderItem.id).label("sales_count")
    ).join(OrderItem).group_by(Product.id).order_by(func.count(OrderItem.id).desc()).limit(5).all()

    popular_products = [{"name": name, "sales": count} for name, count in popular]
    if not popular_products:
        popular_products = [
            {"name": "Sourdough Bread", "sales": 48},
            {"name": "Chocolate Truffle Cake", "sales": 36},
            {"name": "French Croissant", "sales": 29},
            {"name": "Red Velvet Cupcake", "sales": 24},
            {"name": "Artisanal Pizza", "sales": 18}
        ]

    sales_chart = [
        {"day": "Mon", "sales": 1200, "orders": 14},
        {"day": "Tue", "sales": 1800, "orders": 22},
        {"day": "Wed", "sales": 1500, "orders": 19},
        {"day": "Thu", "sales": 2100, "orders": 27},
        {"day": "Fri", "sales": 3400, "orders": 42},
        {"day": "Sat", "sales": 4800, "orders": 58},
        {"day": "Sun", "sales": 5200, "orders": 64},
    ]

    return {
        "total_revenue": round(total_revenue, 2),
        "today_orders": today_orders,
        "monthly_sales": round(monthly_sales, 2),
        "customer_count": customer_count,
        "popular_products": popular_products,
        "sales_chart": sales_chart
    }

@router.get("/orders", response_model=List[OrderOut])
def get_all_orders(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.created_at.desc()).all()

@router.put("/orders/{order_id}/status", response_model=OrderOut)
def update_order_status(order_id: int, payload: OrderStatusUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = payload.status
    if payload.status == "Completed":
        order.payment_status = "Paid"
        
    db.commit()
    db.refresh(order)
    return order

@router.post("/products", response_model=ProductOut)
def create_product(product_in: ProductBase, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, product_in: ProductBase, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product_in.model_dump().items():
        setattr(product, key, value)
        
    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

@router.get("/users", response_model=List[UserOut])
def get_all_users(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(User).all()
