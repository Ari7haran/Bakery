export interface User {
  id: number;
  full_name: string;
  email: string;
  phone?: string;
  role: 'customer' | 'admin';
  loyalty_points: number;
  is_active: boolean;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  icon?: string;
  description?: string;
  image_url?: string;
}

export interface ProductImage {
  id: number;
  image_url: string;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  category_id: number;
  description: string;
  price: number;
  discount_price?: number;
  is_veg: boolean;
  is_featured: boolean;
  is_todays_fresh: boolean;
  is_popular: boolean;
  ingredients?: string;
  nutrition_info?: string;
  prep_time: string;
  rating: number;
  review_count: number;
  stock_quantity: number;
  image_url: string;
  category?: Category;
  images?: ProductImage[];
}

export interface CartItem {
  id: number;
  product_id: number;
  quantity: number;
  product: Product;
}

export interface OrderItem {
  id: number;
  product_id: number;
  quantity: number;
  price: number;
  product: Product;
}

export interface Order {
  id: number;
  order_number: string;
  total_amount: number;
  discount_amount: number;
  final_amount: number;
  order_type: 'Delivery' | 'Takeaway Pickup';
  pickup_date?: string;
  pickup_time_slot?: string;
  pickup_number?: string;
  qr_code_data?: string;
  status: 'Received' | 'Preparing' | 'Baking' | 'Packing' | 'Ready for Pickup' | 'Completed' | 'Cancelled';
  payment_method: string;
  payment_status: string;
  delivery_address?: string;
  notes?: string;
  created_at: string;
  items: OrderItem[];
}

export interface Review {
  id: number;
  product_id: number;
  user_id: number;
  rating: number;
  comment: string;
  created_at: string;
  user: User;
}

export interface Coupon {
  id: number;
  code: string;
  discount_percent: number;
  max_discount_amount: number;
  min_order_amount: number;
  is_active: bool;
}

export interface AnalyticsData {
  total_revenue: number;
  today_orders: number;
  monthly_sales: number;
  customer_count: number;
  popular_products: { name: string; sales: number }[];
  sales_chart: { day: string; sales: number; orders: number }[];
}
