from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional

class OrderStatusBreakdown(BaseModel):
    received: int = 0
    preparing: int = 0
    baking: int = 0
    packing: int = 0
    ready_for_pickup: int = 0
    completed: int = 0
    cancelled: int = 0
    total: int = 0
    pending_total: int = 0

    model_config = ConfigDict(from_attributes=True)

class OrderMetrics(BaseModel):
    total_orders: int
    period_orders: int
    today_orders: int
    this_week_orders: int
    this_month_orders: int
    pending_orders: int
    ready_orders: int
    completed_orders: int
    cancelled_orders: int

    model_config = ConfigDict(from_attributes=True)

class RevenueMetrics(BaseModel):
    total_revenue: float
    period_revenue: float
    today_revenue: float
    this_week_revenue: float
    this_month_revenue: float
    average_order_value: float

    model_config = ConfigDict(from_attributes=True)

class InventoryAttentionItem(BaseModel):
    id: int
    name: str
    stock_quantity: int
    category: str
    status: str  # "Out of Stock" or "Low Stock"
    price: float

    model_config = ConfigDict(from_attributes=True)

class InventoryMetrics(BaseModel):
    total_products: int
    in_stock_products: int
    low_stock_products: int
    out_of_stock_products: int
    items_requiring_attention: List[InventoryAttentionItem] = []

    model_config = ConfigDict(from_attributes=True)

class TopCustomerItem(BaseModel):
    id: int
    name: str
    email: str
    order_count: int
    total_spent: float

    model_config = ConfigDict(from_attributes=True)

class CustomerMetrics(BaseModel):
    total_customers: int
    new_customers: int
    repeat_customers: int
    ordering_customers: int
    top_customers: List[TopCustomerItem] = []

    model_config = ConfigDict(from_attributes=True)

class ChartDataPoint(BaseModel):
    date: str
    day: str
    sales: float
    orders: int

    model_config = ConfigDict(from_attributes=True)

class AnalyticsOut(BaseModel):
    # Backward compatible fields for legacy and Step #1-#13 dashboard consumers
    total_revenue: float
    today_orders: int
    monthly_sales: float
    customer_count: int
    popular_products: List[Dict[str, Any]]
    sales_chart: List[Dict[str, Any]]

    # Enhanced Step #14 metrics
    period: str = "7d"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    order_metrics: Optional[OrderMetrics] = None
    revenue_metrics: Optional[RevenueMetrics] = None
    inventory_metrics: Optional[InventoryMetrics] = None
    customer_metrics: Optional[CustomerMetrics] = None
    status_breakdown: Optional[OrderStatusBreakdown] = None

    model_config = ConfigDict(from_attributes=True)
