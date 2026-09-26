import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  DollarSign,
  ShoppingBag,
  Users,
  TrendingUp,
  Plus,
  Trash2,
  Pencil,
  ShieldCheck,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Filter,
  Search,
  RefreshCw,
  Package,
  Layers,
  ArrowRight
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from 'recharts';
import { api } from '../services/api.js';
import { useAuth } from '../context/AuthContext.jsx';
import { useToast } from '../context/ToastContext.jsx';

const STATUS_COLORS = {
  'Received': '#3B82F6',
  'Preparing': '#F59E0B',
  'Baking': '#D97706',
  'Packing': '#8B5CF6',
  'Ready for Pickup': '#10B981',
  'Completed': '#059669',
  'Cancelled': '#EF4444',
};

const CHART_PALETTE = ['#E07A5F', '#D4AF37', '#8B4513', '#2C1810', '#3D1C10', '#4A7C59', '#6B705C'];

const AdminDashboardPage = () => {
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const [analytics, setAnalytics] = useState(null);
  const [isAnalyticsLoading, setIsAnalyticsLoading] = useState(false);
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activeTab, setActiveTab] = useState('analytics');

  // Period / Date Filtering State
  const [period, setPeriod] = useState('7d');
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');

  // Orders Management Search & Filter
  const [orderSearch, setOrderSearch] = useState('');
  const [orderStatusFilter, setOrderStatusFilter] = useState('All');

  // Products Management Search & Filter
  const [productSearch, setProductSearch] = useState('');
  const [productCategoryFilter, setProductCategoryFilter] = useState('All');

  // New Product Modal Form State
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newProdName, setNewProdName] = useState('');
  const [newProdCategory, setNewProdCategory] = useState(1);
  const [newProdPrice, setNewProdPrice] = useState(200);
  const [newProdStock, setNewProdStock] = useState(25);
  const [newProdDesc, setNewProdDesc] = useState('');
  const [newProdImage, setNewProdImage] = useState('https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=800&auto=format&fit=crop&q=80');

  // Edit Product Modal Form State
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [editName, setEditName] = useState('');
  const [editCategory, setEditCategory] = useState(1);
  const [editPrice, setEditPrice] = useState(0);
  const [editStock, setEditStock] = useState(25);
  const [editDesc, setEditDesc] = useState('');
  const [editImage, setEditImage] = useState('');

  // Initial Data Fetch
  useEffect(() => {
    if (!user || user.role !== 'admin') {
      return;
    }

    const fetchAdminData = async () => {
      setIsAnalyticsLoading(true);
      try {
        const [anRes, ordRes, prodRes, catRes] = await Promise.all([
          api.get('/admin/analytics', { params: { period: '7d' } }),
          api.get('/admin/orders'),
          api.get('/products'),
          api.get('/categories')
        ]);
        setAnalytics(anRes.data);
        setOrders(ordRes.data);
        setProducts(prodRes.data);
        setCategories(catRes.data);
        if (catRes.data.length > 0) setNewProdCategory(catRes.data[0].id);
      } catch (err) {
        console.error("Failed to load admin dashboard data", err);
        toast.error("Failed to load admin dashboard data.");
      } finally {
        setIsAnalyticsLoading(false);
      }
    };
    fetchAdminData();
  }, [user]);

  // Handle Period Filter Changes
  const handlePeriodChange = async (newPeriod) => {
    setPeriod(newPeriod);
    if (newPeriod !== 'custom') {
      await fetchAnalyticsData(newPeriod);
    }
  };

  const handleApplyCustomDates = async (e) => {
    e.preventDefault();
    if (!customStartDate || !customEndDate) {
      toast.error("Please choose both start and end dates.");
      return;
    }
    if (customStartDate > customEndDate) {
      toast.error("Start date must be on or before end date.");
      return;
    }
    await fetchAnalyticsData('custom', customStartDate, customEndDate);
  };

  const fetchAnalyticsData = async (selectedPeriod, start = null, end = null) => {
    setIsAnalyticsLoading(true);
    try {
      const params = { period: selectedPeriod };
      if (selectedPeriod === 'custom') {
        params.start_date = start;
        params.end_date = end;
      }
      const res = await api.get('/admin/analytics', { params });
      setAnalytics(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update analytics.");
    } finally {
      setIsAnalyticsLoading(false);
    }
  };

  if (!user || user.role !== 'admin') {
    return (
      <div className="max-w-md mx-auto py-16 text-center space-y-4">
        <p className="font-serif text-2xl font-bold text-red-500">Access Denied</p>
        <p className="text-xs text-gray-500">Admin privileges required to view dashboard.</p>
        <button
          onClick={() => navigate('/')}
          className="px-6 py-2 bg-bakery-orange text-white text-xs font-bold rounded-full"
        >
          Return Home
        </button>
      </div>
    );
  }

  // Quick Restock Handler
  const handleQuickRestock = async (productId, currentStock, added = 10) => {
    const newStock = (currentStock || 0) + added;
    try {
      const res = await api.put(`/admin/products/${productId}/stock`, { stock_quantity: newStock });
      setProducts(products.map(p => p.id === productId ? res.data : p));
      toast.success(`Restocked! Stock updated to ${newStock} units.`);
      // Refresh analytics in background to keep inventory metrics fresh
      fetchAnalyticsData(period, customStartDate, customEndDate);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update stock.");
    }
  };

  // Orders Status Switcher
  const handleUpdateOrderStatus = async (orderId, status) => {
    try {
      const res = await api.put(`/admin/orders/${orderId}/status`, { status });
      setOrders(orders.map(o => o.id === orderId ? res.data : o));
      toast.success(`Order status updated to ${status}`);
      // Refresh analytics metrics
      fetchAnalyticsData(period, customStartDate, customEndDate);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update order status");
    }
  };

  // Orders Mark Paid
  const handleMarkPaymentPaid = async (orderId) => {
    try {
      const res = await api.put(`/admin/orders/${orderId}/payment`);
      setOrders(orders.map(o => o.id === orderId ? res.data : o));
      toast.success("Order payment marked as Paid");
      fetchAnalyticsData(period, customStartDate, customEndDate);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to mark order as paid");
    }
  };

  // Product Creation
  const handleCreateProduct = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        name: newProdName,
        slug: newProdName.toLowerCase().replace(/\s+/g, '-'),
        category_id: Number(newProdCategory),
        description: newProdDesc,
        price: Number(newProdPrice),
        is_veg: true,
        is_featured: true,
        is_todays_fresh: true,
        is_popular: true,
        prep_time: "15-20 mins",
        stock_quantity: Number(newProdStock),
        image_url: newProdImage
      };
      const res = await api.post('/admin/products', payload);
      setProducts([res.data, ...products]);
      setIsAddModalOpen(false);
      setNewProdName('');
      setNewProdDesc('');
      setNewProdStock(25);
      toast.success("Product created successfully!");
      fetchAnalyticsData(period, customStartDate, customEndDate);
    } catch {
      toast.error("Failed to create product.");
    }
  };

  // Product Editing
  const openEditModal = (product) => {
    setEditingProduct(product);
    setEditName(product.name || '');
    setEditCategory(product.category_id || (product.category?.id || 1));
    setEditPrice(product.price || 0);
    setEditStock(product.stock_quantity ?? 25);
    setEditDesc(product.description || '');
    setEditImage(product.image_url || '');
    setIsEditModalOpen(true);
  };

  const handleEditProduct = async (e) => {
    e.preventDefault();
    if (!editingProduct) return;
    try {
      const payload = {
        name: editName,
        slug: editName.toLowerCase().replace(/\s+/g, '-'),
        category_id: Number(editCategory),
        description: editDesc,
        price: Number(editPrice),
        is_veg: editingProduct.is_veg ?? true,
        is_featured: editingProduct.is_featured ?? true,
        is_todays_fresh: editingProduct.is_todays_fresh ?? true,
        is_popular: editingProduct.is_popular ?? true,
        prep_time: editingProduct.prep_time || "15-20 mins",
        stock_quantity: Number(editStock),
        image_url: editImage
      };
      const res = await api.put(`/admin/products/${editingProduct.id}`, payload);
      setProducts(products.map(p => p.id === editingProduct.id ? res.data : p));
      setIsEditModalOpen(false);
      setEditingProduct(null);
      toast.success("Product updated successfully!");
      fetchAnalyticsData(period, customStartDate, customEndDate);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update product.");
    }
  };

  const handleDeleteProduct = async (prodId) => {
    if (!confirm("Are you sure you want to delete this product?")) return;
    try {
      await api.delete(`/admin/products/${prodId}`);
      setProducts(products.filter(p => p.id !== prodId));
      toast.success("Product deleted successfully");
      fetchAnalyticsData(period, customStartDate, customEndDate);
    } catch {
      toast.error("Failed to delete product.");
    }
  };

  // Filtered Orders
  const filteredOrders = orders.filter(o => {
    const matchesStatus = orderStatusFilter === 'All' || o.status === orderStatusFilter;
    const q = orderSearch.toLowerCase().trim();
    const matchesSearch = !q ||
      o.order_number?.toLowerCase().includes(q) ||
      o.user?.full_name?.toLowerCase().includes(q) ||
      o.delivery_address?.toLowerCase().includes(q);
    return matchesStatus && matchesSearch;
  });

  // Filtered Products
  const filteredProducts = products.filter(p => {
    const matchesCat = productCategoryFilter === 'All' ||
      String(p.category_id) === String(productCategoryFilter) ||
      String(p.category?.id) === String(productCategoryFilter);
    const q = productSearch.toLowerCase().trim();
    const matchesSearch = !q ||
      p.name?.toLowerCase().includes(q) ||
      p.description?.toLowerCase().includes(q);
    return matchesCat && matchesSearch;
  });

  // Status Breakdown Pie Chart Data
  const statusPieData = analytics?.status_breakdown ? [
    { name: 'Received', value: analytics.status_breakdown.received, color: STATUS_COLORS['Received'] },
    { name: 'Preparing', value: analytics.status_breakdown.preparing, color: STATUS_COLORS['Preparing'] },
    { name: 'Baking', value: analytics.status_breakdown.baking, color: STATUS_COLORS['Baking'] },
    { name: 'Packing', value: analytics.status_breakdown.packing, color: STATUS_COLORS['Packing'] },
    { name: 'Ready for Pickup', value: analytics.status_breakdown.ready_for_pickup, color: STATUS_COLORS['Ready for Pickup'] },
    { name: 'Completed', value: analytics.status_breakdown.completed, color: STATUS_COLORS['Completed'] },
    { name: 'Cancelled', value: analytics.status_breakdown.cancelled, color: STATUS_COLORS['Cancelled'] },
  ].filter(d => d.value > 0) : [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

      {/* Admin Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-amber-900/10 pb-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-500/10 text-amber-600 dark:text-amber-300 text-[10px] font-extrabold uppercase rounded-full">
            <ShieldCheck className="w-3.5 h-3.5" /> Bakery Control Center
          </div>
          <h1 className="font-serif text-3xl font-bold mt-1">Admin Dashboard & Analytics</h1>
          <p className="text-xs text-gray-500 mt-0.5">Real-time business performance, order pipeline, and catalog control.</p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-bakery-brown to-bakery-orange text-white text-xs font-bold rounded-2xl shadow hover:opacity-95 transition"
          >
            <Plus className="w-4 h-4" /> Add Product
          </button>
        </div>
      </div>

      {/* Period Filter Toolbar */}
      <div className="bg-white dark:bg-bakery-chocolate/60 p-4 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs font-bold text-gray-500">
            <Calendar className="w-4 h-4 text-bakery-orange" />
            <span>Time Range:</span>
          </div>

          {/* Quick Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5">
            {[
              { id: 'today', label: 'Today' },
              { id: '7d', label: 'Last 7 Days' },
              { id: '30d', label: 'Last 30 Days' },
              { id: 'this_month', label: 'This Month' },
              { id: 'all', label: 'All Time' },
              { id: 'custom', label: 'Custom Range' },
            ].map((btn) => (
              <button
                key={btn.id}
                onClick={() => handlePeriodChange(btn.id)}
                className={`px-3 py-1.5 text-xs font-bold rounded-xl transition ${
                  period === btn.id
                    ? 'bg-bakery-orange text-white shadow-xs'
                    : 'bg-amber-50/60 dark:bg-amber-950/40 text-gray-600 dark:text-gray-300 hover:bg-amber-100'
                }`}
              >
                {btn.label}
              </button>
            ))}
          </div>
        </div>

        {/* Custom Range Picker */}
        {period === 'custom' && (
          <form onSubmit={handleApplyCustomDates} className="pt-3 border-t border-amber-900/10 flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2">
              <label className="text-xs font-bold text-gray-500">Start:</label>
              <input
                type="date"
                required
                value={customStartDate}
                onChange={(e) => setCustomStartDate(e.target.value)}
                className="px-3 py-1.5 text-xs rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/30"
              />
            </div>
            <div className="flex items-center gap-2">
              <label className="text-xs font-bold text-gray-500">End:</label>
              <input
                type="date"
                required
                value={customEndDate}
                onChange={(e) => setCustomEndDate(e.target.value)}
                className="px-3 py-1.5 text-xs rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/30"
              />
            </div>
            <button
              type="submit"
              className="px-4 py-1.5 bg-bakery-brown text-white text-xs font-bold rounded-xl shadow-xs hover:opacity-90 transition"
            >
              Apply Filter
            </button>
          </form>
        )}
      </div>

      {/* KPI Cards Grid (6 Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {/* Card 1: Revenue */}
        <div className="bg-white dark:bg-bakery-chocolate/60 p-5 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs space-y-1.5">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-[11px] font-bold uppercase tracking-wider">Revenue</span>
            <DollarSign className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="font-serif text-2xl font-extrabold text-emerald-600 dark:text-emerald-400">
            ₹{analytics?.revenue_metrics?.period_revenue ?? analytics?.total_revenue ?? 0}
          </div>
          <p className="text-[10px] text-gray-400">
            Avg Order: ₹{analytics?.revenue_metrics?.average_order_value || 0}
          </p>
        </div>

        {/* Card 2: Orders Count */}
        <div className="bg-white dark:bg-bakery-chocolate/60 p-5 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs space-y-1.5">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-[11px] font-bold uppercase tracking-wider">Orders</span>
            <ShoppingBag className="w-4 h-4 text-bakery-orange" />
          </div>
          <div className="font-serif text-2xl font-extrabold text-bakery-dark dark:text-cream-100">
            {analytics?.order_metrics?.period_orders ?? analytics?.today_orders ?? 0}
          </div>
          <p className="text-[10px] text-gray-400">
            {analytics?.order_metrics?.today_orders || 0} placed today
          </p>
        </div>

        {/* Card 3: Monthly Volume */}
        <div className="bg-white dark:bg-bakery-chocolate/60 p-5 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs space-y-1.5">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-[11px] font-bold uppercase tracking-wider">This Month</span>
            <TrendingUp className="w-4 h-4 text-amber-500" />
          </div>
          <div className="font-serif text-2xl font-extrabold text-bakery-orange">
            ₹{analytics?.revenue_metrics?.this_month_revenue ?? analytics?.monthly_sales ?? 0}
          </div>
          <p className="text-[10px] text-gray-400">
            {analytics?.order_metrics?.this_month_orders || 0} orders this month
          </p>
        </div>

        {/* Card 4: Customers */}
        <div className="bg-white dark:bg-bakery-chocolate/60 p-5 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs space-y-1.5">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-[11px] font-bold uppercase tracking-wider">Customers</span>
            <Users className="w-4 h-4 text-blue-500" />
          </div>
          <div className="font-serif text-2xl font-extrabold text-bakery-dark dark:text-cream-100">
            {analytics?.customer_metrics?.total_customers ?? analytics?.customer_count ?? 1}
          </div>
          <p className="text-[10px] text-gray-400">
            {analytics?.customer_metrics?.new_customers || 0} new in period
          </p>
        </div>

        {/* Card 5: Kitchen Pipeline */}
        <div className="bg-white dark:bg-bakery-chocolate/60 p-5 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs space-y-1.5">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-[11px] font-bold uppercase tracking-wider">Fulfillment</span>
            <Clock className="w-4 h-4 text-amber-600" />
          </div>
          <div className="font-serif text-2xl font-extrabold text-amber-600">
            {analytics?.order_metrics?.pending_orders || 0}
          </div>
          <p className="text-[10px] text-gray-400">
            {analytics?.order_metrics?.ready_orders || 0} ready for pickup
          </p>
        </div>

        {/* Card 6: Inventory Status */}
        <div className="bg-white dark:bg-bakery-chocolate/60 p-5 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs space-y-1.5">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-[11px] font-bold uppercase tracking-wider">Inventory Alerts</span>
            <AlertTriangle className="w-4 h-4 text-red-500" />
          </div>
          <div className="font-serif text-2xl font-extrabold text-red-600">
            {(analytics?.inventory_metrics?.low_stock_products || 0) + (analytics?.inventory_metrics?.out_of_stock_products || 0)}
          </div>
          <p className="text-[10px] text-gray-400">
            {analytics?.inventory_metrics?.out_of_stock_products || 0} out of stock
          </p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-amber-900/10 gap-6">
        <button
          onClick={() => setActiveTab('analytics')}
          className={`pb-3 text-xs font-bold uppercase tracking-wider transition border-b-2 ${
            activeTab === 'analytics' ? 'border-bakery-orange text-bakery-orange' : 'border-transparent text-gray-500'
          }`}
        >
          Analytics & Reports
        </button>
        <button
          onClick={() => setActiveTab('orders')}
          className={`pb-3 text-xs font-bold uppercase tracking-wider transition border-b-2 ${
            activeTab === 'orders' ? 'border-bakery-orange text-bakery-orange' : 'border-transparent text-gray-500'
          }`}
        >
          Manage Orders ({orders.length})
        </button>
        <button
          onClick={() => setActiveTab('products')}
          className={`pb-3 text-xs font-bold uppercase tracking-wider transition border-b-2 ${
            activeTab === 'products' ? 'border-bakery-orange text-bakery-orange' : 'border-transparent text-gray-500'
          }`}
        >
          Manage Products ({products.length})
        </button>
      </div>

      {/* Tab 1: Analytics & Reports */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">

          {/* Top Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* Sales & Orders Trend Line Chart */}
            <div className="lg:col-span-2 bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-serif font-bold text-base">Sales Trend (₹)</h3>
                  <p className="text-[11px] text-gray-400">Daily realized sales for selected window</p>
                </div>
                <div className="flex items-center gap-3 text-xs font-semibold">
                  <span className="flex items-center gap-1.5 text-bakery-orange">
                    <span className="w-2.5 h-2.5 rounded-full bg-bakery-orange inline-block" /> Sales (₹)
                  </span>
                  <span className="flex items-center gap-1.5 text-amber-700">
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-700 inline-block" /> Orders
                  </span>
                </div>
              </div>

              <div className="h-64 w-full">
                {analytics?.sales_chart && analytics.sales_chart.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={analytics.sales_chart}>
                      <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                      <XAxis dataKey="day" stroke="#8B4513" fontSize={11} />
                      <YAxis yAxisId="left" stroke="#E07A5F" fontSize={11} />
                      <YAxis yAxisId="right" orientation="right" stroke="#8B4513" fontSize={11} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#2C1810',
                          borderRadius: '12px',
                          border: 'none',
                          color: '#FFF',
                          fontSize: '11px'
                        }}
                      />
                      <Line yAxisId="left" type="monotone" dataKey="sales" name="Sales (₹)" stroke="#E07A5F" strokeWidth={3} dot={{ r: 4 }} />
                      <Line yAxisId="right" type="monotone" dataKey="orders" name="Orders Count" stroke="#8B4513" strokeWidth={2} strokeDasharray="4 4" dot={{ r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-xs text-gray-400">
                    No sales data recorded in this period.
                  </div>
                )}
              </div>
            </div>

            {/* Order Status Distribution Pie Chart */}
            <div className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs space-y-4">
              <div>
                <h3 className="font-serif font-bold text-base">Fulfillment Pipeline</h3>
                <p className="text-[11px] text-gray-400">Orders grouped by live status</p>
              </div>

              <div className="h-48 w-full">
                {statusPieData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={statusPieData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        innerRadius={45}
                        outerRadius={70}
                        paddingAngle={3}
                      >
                        {statusPieData.map((entry, idx) => (
                          <Cell key={`cell-${idx}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#2C1810',
                          borderRadius: '12px',
                          border: 'none',
                          color: '#FFF',
                          fontSize: '11px'
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-xs text-gray-400">
                    No orders in selected period.
                  </div>
                )}
              </div>

              {/* Status Legend Badges */}
              <div className="flex flex-wrap gap-1.5 pt-2 border-t border-amber-900/10">
                {statusPieData.map((s) => (
                  <span
                    key={s.name}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold"
                    style={{ backgroundColor: `${s.color}20`, color: s.color }}
                  >
                    <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: s.color }} />
                    {s.name}: {s.value}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom Grid: Popular Products & Inventory Attention */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* Popular Products */}
            <div className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-serif font-bold text-base">Top Selling Products</h3>
                  <p className="text-[11px] text-gray-400">Ranked by units sold</p>
                </div>
                <ShoppingBag className="w-4 h-4 text-bakery-orange" />
              </div>

              {analytics?.popular_products && analytics.popular_products.length > 0 ? (
                <div className="divide-y divide-amber-900/10">
                  {analytics.popular_products.map((item, idx) => (
                    <div key={item.id || idx} className="py-2.5 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2.5">
                        <span className="w-5 h-5 rounded-full bg-amber-500/10 text-bakery-orange font-bold text-[10px] flex items-center justify-center">
                          #{idx + 1}
                        </span>
                        <span className="font-bold">{item.name}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="font-bold text-bakery-orange">{item.sales} sold</span>
                        {item.revenue !== undefined && (
                          <span className="text-gray-400">₹{item.revenue}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-400 py-6 text-center">No sales registered for this period yet.</p>
              )}
            </div>

            {/* Inventory Requiring Attention */}
            <div className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-serif font-bold text-base">Inventory Attention</h3>
                  <p className="text-[11px] text-gray-400">Out of stock & low stock (&le; 5 units)</p>
                </div>
                <AlertTriangle className="w-4 h-4 text-red-500" />
              </div>

              {analytics?.inventory_metrics?.items_requiring_attention && analytics.inventory_metrics.items_requiring_attention.length > 0 ? (
                <div className="divide-y divide-amber-900/10">
                  {analytics.inventory_metrics.items_requiring_attention.map((item) => (
                    <div key={item.id} className="py-2 flex items-center justify-between text-xs">
                      <div>
                        <p className="font-bold">{item.name}</p>
                        <p className="text-[10px] text-gray-400">{item.category} • ₹{item.price}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          item.stock_quantity === 0
                            ? 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300'
                            : 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                        }`}>
                          {item.stock_quantity} left
                        </span>
                        <button
                          type="button"
                          onClick={() => handleQuickRestock(item.id, item.stock_quantity, 10)}
                          className="px-2 py-0.5 bg-amber-500/10 text-bakery-orange hover:bg-bakery-orange hover:text-white rounded-lg text-[10px] font-bold transition"
                          title="Add 10 units"
                        >
                          +10 Stock
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-6 text-center text-xs text-emerald-600 font-semibold flex items-center justify-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" /> All products adequately stocked.
                </div>
              )}
            </div>

          </div>

          {/* Top Customers Insights */}
          {analytics?.customer_metrics?.top_customers && analytics.customer_metrics.top_customers.length > 0 && (
            <div className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-serif font-bold text-base">Top Loyal Customers</h3>
                  <p className="text-[11px] text-gray-400">Highest grossing customer accounts</p>
                </div>
                <Users className="w-4 h-4 text-blue-500" />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                {analytics.customer_metrics.top_customers.map((c, i) => (
                  <div key={c.id} className="p-3 bg-cream-50 dark:bg-amber-950/30 rounded-2xl border border-amber-900/10 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-bakery-orange">#{i + 1} VIP</span>
                      <span className="text-[10px] text-gray-400">{c.order_count} orders</span>
                    </div>
                    <p className="font-bold text-xs truncate">{c.name}</p>
                    <p className="text-[10px] text-gray-400 truncate">{c.email}</p>
                    <p className="font-bold text-emerald-600 text-xs pt-1">₹{c.total_spent}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      )}

      {/* Tab 2: Orders Management Table */}
      {activeTab === 'orders' && (
        <div className="bg-white dark:bg-bakery-chocolate/60 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 overflow-hidden shadow-xs space-y-4 p-4">
          
          {/* Order Search & Status Filter Controls */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-amber-900/10">
            <div className="relative flex-1 max-w-sm">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
              <input
                type="text"
                value={orderSearch}
                onChange={(e) => setOrderSearch(e.target.value)}
                placeholder="Search by order #, customer, address..."
                className="w-full pl-9 pr-3 py-1.5 text-xs rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/30"
              />
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-gray-500">Status:</span>
              <select
                value={orderStatusFilter}
                onChange={(e) => setOrderStatusFilter(e.target.value)}
                className="px-3 py-1.5 text-xs font-bold rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/40 text-bakery-orange"
              >
                <option value="All">All Statuses ({orders.length})</option>
                <option value="Received">Received</option>
                <option value="Preparing">Preparing</option>
                <option value="Baking">Baking</option>
                <option value="Packing">Packing</option>
                <option value="Ready for Pickup">Ready for Pickup</option>
                <option value="Completed">Completed</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-amber-100/60 dark:bg-amber-950/60 font-bold uppercase tracking-wider border-b border-amber-900/10">
                <tr>
                  <th className="p-4">Order #</th>
                  <th className="p-4">Customer</th>
                  <th className="p-4">Fulfillment Details</th>
                  <th className="p-4">Amount</th>
                  <th className="p-4">Payment</th>
                  <th className="p-4">Status & Switcher</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-amber-900/10">
                {filteredOrders.length > 0 ? (
                  filteredOrders.map((o) => (
                    <tr key={o.id} className="hover:bg-amber-50/50 dark:hover:bg-amber-900/20 transition">
                      <td className="p-4 font-bold">{o.order_number}</td>
                      <td className="p-4">{o.user?.full_name || 'Guest'}</td>
                      <td className="p-4 text-amber-700 dark:text-amber-300">
                        {o.order_type === 'Delivery' ? (
                          <span className="font-semibold text-emerald-700 dark:text-emerald-300">
                            🛵 Delivery: {o.delivery_address}
                          </span>
                        ) : (
                          <span>
                            🥐 Pickup: {o.pickup_date} ({o.pickup_time_slot || 'Express'})
                          </span>
                        )}
                      </td>
                      <td className="p-4 font-bold text-bakery-orange">₹{o.final_amount}</td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 text-[11px] font-bold rounded-full ${o.payment_status === 'Paid' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'}`}>
                            {o.payment_status}
                          </span>
                          {o.payment_status !== 'Paid' && (
                            <button
                              type="button"
                              onClick={() => handleMarkPaymentPaid(o.id)}
                              className="px-2 py-0.5 text-[10px] font-bold bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg shadow-xs transition"
                            >
                              Mark Paid
                            </button>
                          )}
                        </div>
                      </td>
                      <td className="p-4">
                        <select
                          value={o.status}
                          onChange={(e) => handleUpdateOrderStatus(o.id, e.target.value)}
                          className="px-2.5 py-1 text-xs font-bold rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/40 text-bakery-orange"
                        >
                          <option value="Received">Received</option>
                          <option value="Preparing">Preparing</option>
                          <option value="Baking">Baking</option>
                          <option value="Packing">Packing</option>
                          <option value="Ready for Pickup">Ready for Pickup</option>
                          <option value="Completed">Completed</option>
                          <option value="Cancelled">Cancelled</option>
                        </select>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-gray-400">
                      No matching orders found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Products CRUD Table */}
      {activeTab === 'products' && (
        <div className="bg-white dark:bg-bakery-chocolate/60 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 overflow-hidden shadow-xs space-y-4 p-4">
          
          {/* Product Search & Filter Controls */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-amber-900/10">
            <div className="relative flex-1 max-w-sm">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
              <input
                type="text"
                value={productSearch}
                onChange={(e) => setProductSearch(e.target.value)}
                placeholder="Search products by name..."
                className="w-full pl-9 pr-3 py-1.5 text-xs rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/30"
              />
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-gray-500">Category:</span>
              <select
                value={productCategoryFilter}
                onChange={(e) => setProductCategoryFilter(e.target.value)}
                className="px-3 py-1.5 text-xs font-bold rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/40 text-bakery-orange"
              >
                <option value="All">All Categories</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-amber-100/60 dark:bg-amber-950/60 font-bold uppercase tracking-wider border-b border-amber-900/10">
                <tr>
                  <th className="p-4">Product</th>
                  <th className="p-4">Category</th>
                  <th className="p-4">Price</th>
                  <th className="p-4">Stock</th>
                  <th className="p-4">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-amber-900/10">
                {filteredProducts.length > 0 ? (
                  filteredProducts.map((p) => (
                    <tr key={p.id} className="hover:bg-amber-50/50 dark:hover:bg-amber-900/20 transition">
                      <td className="p-4 flex items-center gap-2">
                        <img src={p.image_url} alt={p.name} className="w-8 h-8 rounded-lg object-cover" />
                        <span className="font-bold">{p.name}</span>
                      </td>
                      <td className="p-4">{p.category?.name || 'Bakery'}</td>
                      <td className="p-4 font-bold text-bakery-orange">₹{p.price}</td>
                      <td className="p-4">
                        <span className={`font-semibold ${
                          p.stock_quantity === 0
                            ? 'text-red-500 font-bold'
                            : p.stock_quantity <= 5
                            ? 'text-amber-600 font-bold'
                            : 'text-emerald-600'
                        }`}>
                          {p.stock_quantity} pcs
                        </span>
                      </td>
                      <td className="p-4 flex items-center gap-1.5">
                        <button
                          onClick={() => openEditModal(p)}
                          className="p-1.5 text-amber-600 hover:bg-amber-100 dark:hover:bg-amber-900/50 rounded-lg transition"
                          title="Edit Product"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteProduct(p.id)}
                          className="p-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-950/50 rounded-lg transition"
                          title="Delete Product"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-gray-400">
                      No matching products found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modal to Add New Product */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="bg-white dark:bg-bakery-chocolate w-full max-w-lg rounded-3xl p-6 shadow-2xl border space-y-4">
            <h3 className="font-serif text-xl font-bold">Add New Bakery Product</h3>
            <form onSubmit={handleCreateProduct} className="space-y-3">
              <div>
                <label className="block text-xs font-bold mb-1">Product Name</label>
                <input
                  type="text"
                  required
                  value={newProdName}
                  onChange={(e) => setNewProdName(e.target.value)}
                  placeholder="E.g. Cinnamon Swirl Roll"
                  className="w-full p-2.5 text-xs rounded-xl border"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold mb-1">Category</label>
                  <select
                    value={newProdCategory}
                    onChange={(e) => setNewProdCategory(Number(e.target.value))}
                    className="w-full p-2.5 text-xs rounded-xl border bg-white dark:bg-amber-900"
                  >
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold mb-1">Price (₹)</label>
                  <input
                    type="number"
                    required
                    value={newProdPrice}
                    onChange={(e) => setNewProdPrice(Number(e.target.value))}
                    className="w-full p-2.5 text-xs rounded-xl border"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold mb-1">Stock (pcs)</label>
                  <input
                    type="number"
                    required
                    min="0"
                    value={newProdStock}
                    onChange={(e) => setNewProdStock(Number(e.target.value))}
                    className="w-full p-2.5 text-xs rounded-xl border"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold mb-1">Description</label>
                <textarea
                  required
                  rows={2}
                  value={newProdDesc}
                  onChange={(e) => setNewProdDesc(e.target.value)}
                  className="w-full p-2.5 text-xs rounded-xl border"
                />
              </div>

              <div>
                <label className="block text-xs font-bold mb-1">Image URL</label>
                <input
                  type="url"
                  required
                  value={newProdImage}
                  onChange={(e) => setNewProdImage(e.target.value)}
                  className="w-full p-2.5 text-xs rounded-xl border"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="flex-1 py-2.5 bg-gray-200 dark:bg-amber-900 text-xs font-bold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-bakery-orange text-white text-xs font-bold rounded-xl shadow-xs"
                >
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal to Edit Existing Product */}
      {isEditModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="bg-white dark:bg-bakery-chocolate w-full max-w-lg rounded-3xl p-6 shadow-2xl border space-y-4">
            <div className="flex items-center justify-between border-b border-amber-900/10 pb-3">
              <h3 className="font-serif text-xl font-bold flex items-center gap-2">
                <Pencil className="w-5 h-5 text-bakery-orange" /> Edit Bakery Product
              </h3>
              <button
                onClick={() => { setIsEditModalOpen(false); setEditingProduct(null); }}
                className="text-gray-400 hover:text-gray-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>
            <form onSubmit={handleEditProduct} className="space-y-3">
              <div>
                <label className="block text-xs font-bold mb-1">Product Name</label>
                <input
                  type="text"
                  required
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="w-full p-2.5 text-xs rounded-xl border bg-cream-50 dark:bg-amber-900/40"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold mb-1">Category</label>
                  <select
                    value={editCategory}
                    onChange={(e) => setEditCategory(Number(e.target.value))}
                    className="w-full p-2.5 text-xs rounded-xl border bg-white dark:bg-amber-900"
                  >
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold mb-1">Price (₹)</label>
                  <input
                    type="number"
                    required
                    min="0"
                    value={editPrice}
                    onChange={(e) => setEditPrice(Number(e.target.value))}
                    className="w-full p-2.5 text-xs rounded-xl border bg-cream-50 dark:bg-amber-900/40"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold mb-1">Stock (pcs)</label>
                  <input
                    type="number"
                    required
                    min="0"
                    value={editStock}
                    onChange={(e) => setEditStock(Number(e.target.value))}
                    className="w-full p-2.5 text-xs rounded-xl border bg-cream-50 dark:bg-amber-900/40"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold mb-1">Description</label>
                <textarea
                  required
                  rows={2}
                  value={editDesc}
                  onChange={(e) => setEditDesc(e.target.value)}
                  className="w-full p-2.5 text-xs rounded-xl border bg-cream-50 dark:bg-amber-900/40"
                />
              </div>

              <div>
                <label className="block text-xs font-bold mb-1">Image URL</label>
                <input
                  type="url"
                  required
                  value={editImage}
                  onChange={(e) => setEditImage(e.target.value)}
                  className="w-full p-2.5 text-xs rounded-xl border bg-cream-50 dark:bg-amber-900/40"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => { setIsEditModalOpen(false); setEditingProduct(null); }}
                  className="flex-1 py-2.5 bg-gray-200 dark:bg-amber-900 text-xs font-bold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-bakery-orange text-white text-xs font-bold rounded-xl shadow-xs hover:opacity-90 transition"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};

export default AdminDashboardPage;
