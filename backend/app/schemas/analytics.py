from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any

class AnalyticsOut(BaseModel):
    total_revenue: float
    today_orders: int
    monthly_sales: float
    customer_count: int
    popular_products: List[Dict[str, Any]]
    sales_chart: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)
