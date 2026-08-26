import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  DollarSign,
  ShoppingBag,
  Users,
  TrendingUp,
  Plus,
  Trash2,
  Edit,
  CheckCircle2,
  Clock,
  Package,
  LayoutDashboard,
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, PieChart, Pie, Cell } from 'recharts';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { AnalyticsData, Order, Product, Category } from '../types';

const COLORS = ['#8B4513', '#E07A5F', '#D4AF37', '#2C1810', '#3D1C10'];

const AdminDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [activeTab, setActiveTab] = useState<'analytics' | 'orders' | 'products'>('analytics');
  const [loading, setLoading] = useState(true);

  // New Product Modal Form State
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newProdName, setNewProdName] = useState('');
  const [newProdCategory, setNewProdCategory] = useState<number>(1);
  const [newProdPrice, setNewProdPrice] = useState<number>(200);
  const [newProdDesc, setNewProdDesc] = useState('');
  const [newProdImage, setNewProdImage] = useState('https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=800&auto=format&fit=crop&q=80');

  useEffect(() => {
    if (!user || user.role !== 'admin') {
      return;
    }

    const fetchAdminData = async () => {
      setLoading(true);
      try {
        const [anRes, ordRes, prodRes, catRes] = await Promise.all([
          api.get('/admin/analytics'),
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
        console.error("Failed to load admin analytics", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAdminData();
  }, [user]);

  if (!user || user.role !== 'admin') {
    return (
      <div className="max-w-md mx-auto py-16 text-center space-y-4">
        <p className="font-serif text-2xl font-bold text-red-500">Access Denied</p>
        <p className="text-xs text-gray-500">Admin privileges required to view dashboard.</p>
        <button onClick={() => navigate('/')} className="px-6 py-2 bg-bakery-orange text-white text-xs font-bold rounded-full">
          Return Home
        </button>
      </div>
    );
  }

  const handleUpdateOrderStatus = async (orderId: number, status: string) => {
    try {
      const res = await api.put(`/admin/orders/${orderId}/status`, { status });
      setOrders(orders.map(o => o.id === orderId ? res.data : o));
    } catch {
      alert("Failed to update order status");
    }
  };

  const handleCreateProduct = async (e: React.FormEvent) => {
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
        stock_quantity: 25,
        image_url: newProdImage
      };
      const res = await api.post('/admin/products', payload);
      setProducts([res.data, ...products]);
      setIsAddModalOpen(false);
      setNewProdName('');
      setNewProdDesc('');
      alert("Product created successfully!");
    } catch {
      alert("Failed to create product.");
    }
  };

  const handleDeleteProduct = async (prodId: number) => {
    if (!confirm("Are you sure you want to delete this product?")) return;
    try {
      await api.delete(`/admin/products/${prodId}`);
      setProducts(products.filter(p => p.id !== prodId));
    } catch {
      alert("Failed to delete product.");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Admin Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-amber-900/10 pb-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-500/10 text-amber-600 dark:text-amber-300 text-[10px] font-extrabold uppercase rounded-full">
            <ShieldCheck className="w-3.5 h-3.5" /> Bakery Control Center
          </div>
          <h1 className="font-serif text-3xl font-bold mt-1">Admin Dashboard</h1>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-bakery-brown to-bakery-orange text-white text-xs font-bold rounded-2xl shadow hover:opacity-95 transition"
          >
            <Plus className="w-4 h-4" /> Add Product
          </button>
        </div>
      </div>

      {/* Analytics Widgets Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-xs font-bold">Total Revenue</span>
            <DollarSign className="w-5 h-5 text-emerald-500" />
          </div>
          <span className="font-serif text-2xl font-extrabold text-emerald-600 dark:text-emerald-400">
            ₹{analytics?.total_revenue || 0}
          </span>
          <p className="text-[10px] text-gray-400">Lifetime gross sales</p>
        </div>

        <div className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-xs font-bold">Today's Orders</span>
            <ShoppingBag className="w-5 h-5 text-bakery-orange" />
          </div>
          <span className="font-serif text-2xl font-extrabold text-bakery-dark dark:text-cream-100">
            {analytics?.today_orders || orders.length}
          </span>
          <p className="text-[10px] text-gray-400">Completed & pending counter orders</p>
        </div>

        <div className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-xs font-bold">Monthly Sales</span>
            <TrendingUp className="w-5 h-5 text-amber-500" />
          </div>
          <span className="font-serif text-2xl font-extrabold text-bakery-orange">
            ₹{analytics?.monthly_sales || 0}
          </span>
          <p className="text-[10px] text-gray-400">Current month volume</p>
        </div>

        <div className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-xs font-bold">Customers</span>
            <Users className="w-5 h-5 text-blue-500" />
          </div>
          <span className="font-serif text-2xl font-extrabold text-bakery-dark dark:text-cream-100">
            {analytics?.customer_count || 1}
          </span>
          <p className="text-[10px] text-gray-400">Registered accounts</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-amber-900/10 gap-6">
        <button
          onClick={() => setActiveTab('analytics')}
          className={`pb-3 text-xs font-bold uppercase tracking-wider transition border-b-2 ${
            activeTab === 'analytics' ? 'border-bakery-orange text-bakery-orange' : 'border-transparent text-gray-500'
          }`}
        >
          Recharts Analytics
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

      {/* Tab 1: Recharts Analytics Charts */}
      {activeTab === 'analytics' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Revenue Line Chart */}
          <div className="lg:col-span-2 bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-sm space-y-4">
            <h3 className="font-serif font-bold text-sm">Weekly Sales Trend (₹)</h3>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={analytics?.sales_chart || []}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="day" stroke="#8B4513" fontSize={11} />
                  <YAxis stroke="#8B4513" fontSize={11} />
                  <Tooltip />
                  <Line type="monotone" dataKey="sales" stroke="#E07A5F" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Popular Items Pie Chart */}
          <div className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-sm space-y-4">
            <h3 className="font-serif font-bold text-sm">Top Bakery Items</h3>
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={analytics?.popular_products || []} dataKey="sales" nameKey="name" cx="50%" cy="50%" outerRadius={70} fill="#E07A5F">
                    {(analytics?.popular_products || []).map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Orders Management Table */}
      {activeTab === 'orders' && (
        <div className="bg-white dark:bg-bakery-chocolate/60 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-amber-100/60 dark:bg-amber-950/60 font-bold uppercase tracking-wider border-b border-amber-900/10">
                <tr>
                  <th className="p-4">Order #</th>
                  <th className="p-4">Customer</th>
                  <th className="p-4">Slot</th>
                  <th className="p-4">Amount</th>
                  <th className="p-4">Payment</th>
                  <th className="p-4">Status & Switcher</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-amber-900/10">
                {orders.map((o) => (
                  <tr key={o.id} className="hover:bg-amber-50/50 dark:hover:bg-amber-900/20 transition">
                    <td className="p-4 font-bold">{o.order_number}</td>
                    <td className="p-4">{o.user?.full_name || 'Guest'}</td>
                    <td className="p-4 text-amber-700 dark:text-amber-300">{o.pickup_date} ({o.pickup_time_slot || 'Express'})</td>
                    <td className="p-4 font-bold text-bakery-orange">₹{o.final_amount}</td>
                    <td className="p-4 font-semibold">{o.payment_status}</td>
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
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Products CRUD Table */}
      {activeTab === 'products' && (
        <div className="bg-white dark:bg-bakery-chocolate/60 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 overflow-hidden shadow-sm">
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
                {products.map((p) => (
                  <tr key={p.id} className="hover:bg-amber-50/50 dark:hover:bg-amber-900/20 transition">
                    <td className="p-4 flex items-center gap-2">
                      <img src={p.image_url} alt={p.name} className="w-8 h-8 rounded-lg object-cover" />
                      <span className="font-bold">{p.name}</span>
                    </td>
                    <td className="p-4">{p.category?.name || 'Bakery'}</td>
                    <td className="p-4 font-bold text-bakery-orange">₹{p.price}</td>
                    <td className="p-4 font-semibold text-emerald-600">{p.stock_quantity} pcs</td>
                    <td className="p-4">
                      <button onClick={() => handleDeleteProduct(p.id)} className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg" title="Delete Product">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
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

              <div className="grid grid-cols-2 gap-3">
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
                  className="flex-1 py-2.5 bg-bakery-orange text-white text-xs font-bold rounded-xl shadow"
                >
                  Save Product
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
