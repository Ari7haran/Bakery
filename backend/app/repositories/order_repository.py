from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.base_repository import BaseRepository
from app.models.order import Order, OrderItem
from app.models.product import Product

class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        super().__init__(Order, db)

    def get_by_order_number(self, order_number: str) -> Optional[Order]:
        return self.db.query(Order).filter(Order.order_number == order_number).first()

    def list_by_user(self, user_id: int) -> List[Order]:
        return self.db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()

    def list_all_ordered(self) -> List[Order]:
        return self.db.query(Order).order_by(Order.created_at.desc()).all()

    def create_order_with_items(self, order: Order, items: List[OrderItem]) -> Order:
        self.db.add(order)
        self.db.flush()
        for item in items:
            item.order_id = order.id
            self.db.add(item)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update_status(self, order: Order, status: str) -> Order:
        order.status = status
        self.db.commit()
        self.db.refresh(order)
        return order

    def update_payment_status(self, order: Order, payment_status: str) -> Order:
        order.payment_status = payment_status
        self.db.commit()
        self.db.refresh(order)
        return order

    def sum_revenue(self) -> float:
        return self.db.query(func.sum(Order.final_amount)).scalar() or 0.0

    def count_total_orders(self) -> int:
        return self.db.query(Order).count()

    def get_popular_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        results = (
            self.db.query(Product.name, func.count(OrderItem.id).label("sales_count"))
            .join(OrderItem, Product.id == OrderItem.product_id)
            .group_by(Product.id)
            .order_by(func.count(OrderItem.id).desc())
            .limit(limit)
            .all()
        )
        return [{"name": name, "sales": count} for name, count in results]
