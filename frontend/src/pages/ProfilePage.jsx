import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { ShoppingBag, Heart, Award, QrCode } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';
import { useCart } from '../context/CartContext.jsx';
import { api } from '../services/api.js';
import ProductCard from '../components/ProductCard.jsx';

const ProfilePage = () => {
  const { user } = useAuth();
  const { wishlist } = useCart();
  const [searchParams] = useSearchParams();

  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'orders');
  const [orders, setOrders] = useState([]);
  const [loadingOrders, setLoadingOrders] = useState(false);

  useEffect(() => {
    const fetchOrders = async () => {
      if (!user) return;
      setLoadingOrders(true);
      try {
        const res = await api.get('/orders/my-orders');
        setOrders(res.data);
      } catch (err) {
        console.error("Failed to load user orders", err);
      } finally {
        setLoadingOrders(false);
      }
    };
    fetchOrders();
  }, [user]);

  if (!user) {
    return (
      <div className="max-w-md mx-auto py-16 px-4 text-center space-y-4">
        <p className="font-serif text-2xl font-bold">Sign In Required</p>
        <p className="text-xs text-gray-500">Please sign in to view your profile, order history & loyalty points.</p>
        <Link to="/login" className="inline-block px-6 py-2.5 bg-bakery-orange text-white font-bold text-xs rounded-full">
          Sign In Now
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header Profile Card */}
      <div className="bg-gradient-to-r from-bakery-dark via-bakery-brown to-bakery-chocolate text-cream-100 rounded-3xl p-6 sm:p-8 shadow-xl flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-bakery-orange text-white flex items-center justify-center font-extrabold text-2xl border-2 border-amber-300 shadow">
            {user.full_name.charAt(0)}
          </div>
          <div>
            <h1 className="font-serif text-2xl font-bold">{user.full_name}</h1>
            <p className="text-xs text-amber-200/80">{user.email}</p>
            <span className="inline-block mt-2 text-[10px] font-bold uppercase bg-amber-500/20 border border-amber-400/40 text-amber-300 px-2.5 py-0.5 rounded-full">
              Role: {user.role}
            </span>
          </div>
        </div>

        {/* Loyalty Points Widget */}
        <div className="bg-white/10 backdrop-blur-md p-4 rounded-2xl border border-white/20 text-center sm:text-right min-w-44">
          <div className="flex items-center justify-center sm:justify-end gap-1.5 text-amber-300 font-bold text-xs">
            <Award className="w-4 h-4 text-bakery-orange" /> Sweet VIP Points
          </div>
          <span className="font-serif text-3xl font-extrabold text-white block mt-1">
            {user.loyalty_points}
          </span>
          <p className="text-[10px] text-amber-200/70">10 pts earned per ₹100 spent</p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-amber-900/10 gap-6">
        <button
          onClick={() => setActiveTab('orders')}
          className={`pb-3 text-xs font-bold uppercase tracking-wider flex items-center gap-2 border-b-2 transition ${
            activeTab === 'orders' ? 'border-bakery-orange text-bakery-orange' : 'border-transparent text-gray-500'
          }`}
        >
          <ShoppingBag className="w-4 h-4" /> Order History ({orders.length})
        </button>

        <button
          onClick={() => setActiveTab('wishlist')}
          className={`pb-3 text-xs font-bold uppercase tracking-wider flex items-center gap-2 border-b-2 transition ${
            activeTab === 'wishlist' ? 'border-bakery-orange text-bakery-orange' : 'border-transparent text-gray-500'
          }`}
        >
          <Heart className="w-4 h-4" /> Saved Wishlist ({wishlist.length})
        </button>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'orders' && (
          <div className="space-y-4">
            {loadingOrders ? (
              <p className="text-xs text-gray-500">Loading order history...</p>
            ) : orders.length === 0 ? (
              <div className="text-center py-12 bg-white dark:bg-bakery-chocolate/40 rounded-3xl p-6 border border-amber-900/10">
                <p className="font-serif font-bold text-lg">No Past Orders Found</p>
                <p className="text-xs text-gray-500 mt-1">Start your warm sourdough order today!</p>
                <Link to="/shop" className="inline-block mt-4 px-6 py-2.5 bg-bakery-orange text-white text-xs font-bold rounded-full">
                  Browse Menu
                </Link>
              </div>
            ) : (
              orders.map((order) => (
                <div key={order.id} className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <span className="font-serif font-bold text-base">Order #{order.order_number}</span>
                      <span className="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-bakery-orange/20 text-bakery-orange">
                        {order.status}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">
                      Placed on {new Date(order.created_at).toLocaleDateString()} • {order.items.length} items
                    </p>
                    <p className="text-xs text-amber-700 dark:text-amber-300 font-semibold">
                      {order.order_type === 'Delivery'
                        ? `🛵 Delivery: ${order.delivery_address || 'Home Delivery'}`
                        : `🥐 Pickup Slot: ${order.pickup_date} (${order.pickup_time_slot || 'Express Takeaway'})`}
                    </p>
                  </div>

                  <div className="flex items-center gap-4">
                    <span className="font-serif text-xl font-bold text-bakery-orange">₹{order.final_amount}</span>
                    <Link
                      to={`/track?orderId=${order.id}`}
                      className="px-4 py-2 bg-bakery-dark dark:bg-amber-900 text-white text-xs font-bold rounded-xl flex items-center gap-1 hover:bg-bakery-orange transition"
                    >
                      <QrCode className="w-4 h-4" /> Track & QR Code
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'wishlist' && (
          <div>
            {wishlist.length === 0 ? (
              <div className="text-center py-12 bg-white dark:bg-bakery-chocolate/40 rounded-3xl p-6 border border-amber-900/10">
                <p className="font-serif font-bold text-lg">Your Wishlist is Empty</p>
                <p className="text-xs text-gray-500 mt-1">Tap the heart icon on any product to save for later.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {wishlist.map((p) => (
                  <ProductCard key={p.id} product={p} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>

    </div>
  );
};

export default ProfilePage;
