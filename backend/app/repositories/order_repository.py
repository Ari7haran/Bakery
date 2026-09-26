from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, distinct
from app.repositories.base_repository import BaseRepository
from app.models.order import Order, OrderItem, OrderStatusEnum, PaymentStatusEnum
from app.models.product import Product
from app.models.user import User

class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        super().__init__(Order, db)

    def get_by_id(self, id: int) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.id == id)
            .first()
        )

    def get_by_order_number(self, order_number: str) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.order_number == order_number)
            .first()
        )

    def list_by_user(self, user_id: int) -> List[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .all()
        )

    def list_all_ordered(self) -> List[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .order_by(Order.created_at.desc())
            .all()
        )

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

    def sum_revenue(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        paid_only: bool = True
    ) -> float:
        query = self.db.query(func.sum(Order.final_amount))
        if paid_only:
            query = query.filter(
                Order.payment_status == PaymentStatusEnum.PAID.value,
                Order.status != OrderStatusEnum.CANCELLED.value
            )
        else:
            query = query.filter(Order.status != OrderStatusEnum.CANCELLED.value)

        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)

        val = query.scalar()
        return round(float(val), 2) if val is not None else 0.0

    def count_total_orders(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        exclude_cancelled: bool = False
    ) -> int:
        query = self.db.query(func.count(Order.id))
        if status:
            query = query.filter(Order.status == status)
        elif exclude_cancelled:
            query = query.filter(Order.status != OrderStatusEnum.CANCELLED.value)

        if payment_status:
            query = query.filter(Order.payment_status == payment_status)

        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)

        return query.scalar() or 0

    def get_status_counts(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        query = self.db.query(Order.status, func.count(Order.id))
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        results = query.group_by(Order.status).all()
        return {status: count for status, count in results}

    def get_popular_products(
        self,
        limit: int = 5,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        query = (
            self.db.query(
                Product.id.label("id"),
                Product.name.label("name"),
                func.sum(OrderItem.quantity).label("units_sold"),
                func.sum(OrderItem.quantity * OrderItem.price).label("total_revenue")
            )
            .join(OrderItem, Product.id == OrderItem.product_id)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(Order.status != OrderStatusEnum.CANCELLED.value)
        )
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)

        results = (
            query.group_by(Product.id, Product.name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "name": r.name,
                "sales": int(r.units_sold) if r.units_sold else 0,
                "revenue": round(float(r.total_revenue), 2) if r.total_revenue else 0.0
            }
            for r in results
        ]

    def get_daily_sales(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        orders = (
            self.db.query(Order.created_at, Order.final_amount, Order.payment_status, Order.status)
            .filter(Order.created_at >= start_date, Order.created_at <= end_date)
            .all()
        )

        current = start_date.date()
        target_end = end_date.date()
        daily_map = {}
        while current <= target_end:
            day_str = current.strftime("%Y-%m-%d")
            day_abbr = current.strftime("%a")
            daily_map[day_str] = {"date": day_str, "day": day_abbr, "sales": 0.0, "orders": 0}
            current += timedelta(days=1)

        for o in orders:
            d_str = o.created_at.date().strftime("%Y-%m-%d") if o.created_at else None
            if d_str and d_str in daily_map:
                daily_map[d_str]["orders"] += 1
                if o.payment_status == PaymentStatusEnum.PAID.value and o.status != OrderStatusEnum.CANCELLED.value:
                    daily_map[d_str]["sales"] += float(o.final_amount or 0.0)

        result = list(daily_map.values())
        for item in result:
            item["sales"] = round(item["sales"], 2)
        return result

    def get_top_customers(
        self,
        limit: int = 5,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        query = (
            self.db.query(
                User.id.label("id"),
                User.full_name.label("name"),
                User.email.label("email"),
                func.count(Order.id).label("order_count"),
                func.sum(Order.final_amount).label("total_spent")
            )
            .join(Order, User.id == Order.user_id)
            .filter(Order.status != OrderStatusEnum.CANCELLED.value)
        )
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)

        results = (
            query.group_by(User.id, User.full_name, User.email)
            .order_by(func.sum(Order.final_amount).desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "name": r.name,
                "email": r.email,
                "order_count": int(r.order_count) if r.order_count else 0,
                "total_spent": round(float(r.total_spent), 2) if r.total_spent else 0.0
            }
            for r in results
        ]

    def count_ordering_customers(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        query = self.db.query(func.count(distinct(Order.user_id))).filter(
            Order.user_id.isnot(None),
            Order.status != OrderStatusEnum.CANCELLED.value
        )
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        return query.scalar() or 0

    def count_repeat_customers(self) -> int:
        subq = (
            self.db.query(Order.user_id)
            .filter(Order.user_id.isnot(None), Order.status != OrderStatusEnum.CANCELLED.value)
            .group_by(Order.user_id)
            .having(func.count(Order.id) > 1)
            .subquery()
        )
        return self.db.query(func.count()).select_from(subq).scalar() or 0
