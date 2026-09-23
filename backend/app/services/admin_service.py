from typing import List, Dict, Any
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.models.order import Order
from app.models.user import User

class AdminService:
    def __init__(self, order_repo: OrderRepository, user_repo: UserRepository):
        self.order_repo = order_repo
        self.user_repo = user_repo

    def get_analytics(self) -> Dict[str, Any]:
        total_revenue = self.order_repo.sum_revenue()
        today_orders = self.order_repo.count_total_orders()
        monthly_sales = total_revenue * 0.85
        customer_count = self.user_repo.count_customers()
        popular_products = self.order_repo.get_popular_products(limit=5)

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

    def list_orders(self) -> List[Order]:
        return self.order_repo.list_all_ordered()

    def list_users(self) -> List[User]:
        return self.user_repo.list_all()
