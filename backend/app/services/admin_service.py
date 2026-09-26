from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.models.order import Order, OrderStatusEnum, PaymentStatusEnum
from app.models.user import User

class AdminService:
    def __init__(
        self,
        order_repo: OrderRepository,
        user_repo: UserRepository,
        product_repo: Optional[ProductRepository] = None,
        db: Optional[Session] = None
    ):
        self.order_repo = order_repo
        self.user_repo = user_repo
        if product_repo is not None:
            self.product_repo = product_repo
        elif db is not None:
            self.product_repo = ProductRepository(db)
        elif hasattr(order_repo, "db") and order_repo.db is not None:
            self.product_repo = ProductRepository(order_repo.db)
        else:
            self.product_repo = None

    def _resolve_period_dates(
        self,
        period: str = "7d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ):
        now = datetime.utcnow()
        start_of_today = datetime(now.year, now.month, now.day, 0, 0, 0)
        start_of_week = now - timedelta(days=7)
        start_of_month = datetime(now.year, now.month, 1, 0, 0, 0)

        p = (period or "7d").lower().strip()
        if p == "today":
            p_start = start_of_today
            p_end = now
        elif p in {"7d", "last_7_days", "week"}:
            p_start = start_of_week
            p_end = now
        elif p in {"30d", "last_30_days"}:
            p_start = now - timedelta(days=30)
            p_end = now
        elif p in {"this_month", "month"}:
            p_start = start_of_month
            p_end = now
        elif p in {"all", "all_time"}:
            p_start = None
            p_end = None
        elif p == "custom":
            if not start_date or not end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Both start_date and end_date (YYYY-MM-DD) are required for custom period."
                )
            try:
                p_start = datetime.strptime(start_date.strip(), "%Y-%m-%d")
                # Include end of day
                p_end = datetime.strptime(end_date.strip(), "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format for custom period. Expected YYYY-MM-DD."
                )
            if p_start > p_end:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="start_date must be before or equal to end_date."
                )
        else:
            # Default fallback to 7 days
            p = "7d"
            p_start = start_of_week
            p_end = now

        return p, p_start, p_end, now, start_of_today, start_of_week, start_of_month

    def get_analytics(
        self,
        period: str = "7d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        p, p_start, p_end, now, start_of_today, start_of_week, start_of_month = self._resolve_period_dates(
            period=period,
            start_date=start_date,
            end_date=end_date
        )

        # ---------------------------------------------------------
        # 1. Order Metrics
        # ---------------------------------------------------------
        total_orders = self.order_repo.count_total_orders()
        period_orders = self.order_repo.count_total_orders(start_date=p_start, end_date=p_end)
        today_orders = self.order_repo.count_total_orders(start_date=start_of_today)
        this_week_orders = self.order_repo.count_total_orders(start_date=start_of_week)
        this_month_orders = self.order_repo.count_total_orders(start_date=start_of_month)

        # Status breakdown
        status_counts = self.order_repo.get_status_counts(start_date=p_start, end_date=p_end)
        received_cnt = status_counts.get(OrderStatusEnum.RECEIVED.value, 0)
        preparing_cnt = status_counts.get(OrderStatusEnum.PREPARING.value, 0)
        baking_cnt = status_counts.get(OrderStatusEnum.BAKING.value, 0)
        packing_cnt = status_counts.get(OrderStatusEnum.PACKING.value, 0)
        ready_cnt = status_counts.get(OrderStatusEnum.READY_FOR_PICKUP.value, 0)
        completed_cnt = status_counts.get(OrderStatusEnum.COMPLETED.value, 0)
        cancelled_cnt = status_counts.get(OrderStatusEnum.CANCELLED.value, 0)

        pending_total = received_cnt + preparing_cnt + baking_cnt + packing_cnt

        order_metrics = {
            "total_orders": total_orders,
            "period_orders": period_orders,
            "today_orders": today_orders,
            "this_week_orders": this_week_orders,
            "this_month_orders": this_month_orders,
            "pending_orders": pending_total,
            "ready_orders": ready_cnt,
            "completed_orders": completed_cnt,
            "cancelled_orders": cancelled_cnt,
        }

        status_breakdown = {
            "received": received_cnt,
            "preparing": preparing_cnt,
            "baking": baking_cnt,
            "packing": packing_cnt,
            "ready_for_pickup": ready_cnt,
            "completed": completed_cnt,
            "cancelled": cancelled_cnt,
            "total": sum(status_counts.values()),
            "pending_total": pending_total,
        }

        # ---------------------------------------------------------
        # 2. Revenue Metrics (Strictly Realized Revenue: Paid & Non-Cancelled)
        # ---------------------------------------------------------
        total_revenue = self.order_repo.sum_revenue(paid_only=True)
        period_revenue = self.order_repo.sum_revenue(start_date=p_start, end_date=p_end, paid_only=True)
        today_revenue = self.order_repo.sum_revenue(start_date=start_of_today, paid_only=True)
        this_week_revenue = self.order_repo.sum_revenue(start_date=start_of_week, paid_only=True)
        this_month_revenue = self.order_repo.sum_revenue(start_date=start_of_month, paid_only=True)

        paid_orders_count = self.order_repo.count_total_orders(
            start_date=p_start,
            end_date=p_end,
            payment_status=PaymentStatusEnum.PAID.value,
            exclude_cancelled=True
        )

        average_order_value = round(period_revenue / paid_orders_count, 2) if paid_orders_count > 0 else 0.0

        revenue_metrics = {
            "total_revenue": total_revenue,
            "period_revenue": period_revenue,
            "today_revenue": today_revenue,
            "this_week_revenue": this_week_revenue,
            "this_month_revenue": this_month_revenue,
            "average_order_value": average_order_value,
        }

        # ---------------------------------------------------------
        # 3. Product & Inventory Analytics
        # ---------------------------------------------------------
        if self.product_repo:
            stock_summary = self.product_repo.count_by_stock_status()
            attention_raw = self.product_repo.get_low_stock_products(threshold=5, limit=10)
            items_requiring_attention = [
                {
                    "id": item.id,
                    "name": item.name,
                    "stock_quantity": item.stock_quantity,
                    "category": item.category.name if item.category else "Bakery",
                    "status": "Out of Stock" if item.stock_quantity == 0 else "Low Stock",
                    "price": item.price,
                }
                for item in attention_raw
            ]
        else:
            stock_summary = {"total": 0, "in_stock": 0, "low_stock": 0, "out_of_stock": 0}
            items_requiring_attention = []

        inventory_metrics = {
            "total_products": stock_summary["total"],
            "in_stock_products": stock_summary["in_stock"],
            "low_stock_products": stock_summary["low_stock"],
            "out_of_stock_products": stock_summary["out_of_stock"],
            "items_requiring_attention": items_requiring_attention,
        }

        # ---------------------------------------------------------
        # 4. Customer Analytics
        # ---------------------------------------------------------
        customer_count = self.user_repo.count_customers()
        new_customers = self.user_repo.count_new_customers(p_start) if p_start else customer_count
        ordering_customers = self.order_repo.count_ordering_customers(start_date=p_start, end_date=p_end)
        repeat_customers = self.order_repo.count_repeat_customers()
        top_customers = self.order_repo.get_top_customers(limit=5, start_date=p_start, end_date=p_end)

        customer_metrics = {
            "total_customers": customer_count,
            "new_customers": new_customers,
            "repeat_customers": repeat_customers,
            "ordering_customers": ordering_customers,
            "top_customers": top_customers,
        }

        # ---------------------------------------------------------
        # 5. Top Popular Products & Daily Sales Chart (Real Database Data)
        # ---------------------------------------------------------
        popular_products = self.order_repo.get_popular_products(limit=5, start_date=p_start, end_date=p_end)

        # Determine date bounds for chart
        if p_start and p_end:
            chart_start = p_start
            chart_end = p_end
        else:
            # All-time period shows last 30 days on daily chart
            chart_start = now - timedelta(days=30)
            chart_end = now

        sales_chart = self.order_repo.get_daily_sales(chart_start, chart_end)

        # ---------------------------------------------------------
        # 6. Assemble Full Response
        # ---------------------------------------------------------
        return {
            # Backward-compatible fields
            "total_revenue": total_revenue,
            "today_orders": today_orders,
            "monthly_sales": this_month_revenue,
            "customer_count": customer_count,
            "popular_products": popular_products,
            "sales_chart": sales_chart,
            # Enhanced Step #14 metrics
            "period": p,
            "start_date": p_start.strftime("%Y-%m-%d") if p_start else None,
            "end_date": p_end.strftime("%Y-%m-%d") if p_end else None,
            "order_metrics": order_metrics,
            "revenue_metrics": revenue_metrics,
            "inventory_metrics": inventory_metrics,
            "customer_metrics": customer_metrics,
            "status_breakdown": status_breakdown,
        }

    def list_orders(self) -> List[Order]:
        return self.order_repo.list_all_ordered()

    def list_users(self) -> List[User]:
        return self.user_repo.list_all()
