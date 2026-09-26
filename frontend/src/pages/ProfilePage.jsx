import React, { useEffect, useState } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { ShoppingBag, Heart, Award, QrCode, Bell, CheckCheck, Trash2, ExternalLink } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';
import { useCart } from '../context/CartContext.jsx';
import { useToast } from '../context/ToastContext.jsx';
import { api } from '../services/api.js';
import { notificationService } from '../services/notificationService.js';
import ProductCard from '../components/ProductCard.jsx';

const ProfilePage = () => {
  const { user } = useAuth();
  const { wishlist } = useCart();
  const [searchParams] = useSearchParams();

  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'orders');
  const [orders, setOrders] = useState([]);
  const [loadingOrders, setLoadingOrders] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [loadingNotifications, setLoadingNotifications] = useState(false);
  const [notifFilter, setNotifFilter] = useState('all');
  const toast = useToast();
  const navigate = useNavigate();

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

  const fetchProfileNotifications = async () => {
    if (!user) return;
    setLoadingNotifications(true);
    try {
      const data = await notificationService.getNotifications({
        limit: 50,
        is_read: notifFilter === 'unread' ? false : notifFilter === 'read' ? true : undefined
      });
      setNotifications(data.items || []);
    } catch (err) {
      console.error("Failed to load notifications", err);
    } finally {
      setLoadingNotifications(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'notifications') {
      fetchProfileNotifications();
    }
  }, [user, activeTab, notifFilter]);

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

        <button
          onClick={() => setActiveTab('notifications')}
          className={`pb-3 text-xs font-bold uppercase tracking-wider flex items-center gap-2 border-b-2 transition ${
            activeTab === 'notifications' ? 'border-bakery-orange text-bakery-orange' : 'border-transparent text-gray-500'
          }`}
        >
          <Bell className="w-4 h-4" /> Notifications
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

        {activeTab === 'notifications' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white dark:bg-bakery-chocolate/60 p-4 rounded-2xl border border-amber-900/10">
              <div className="flex gap-2 text-xs">
                {['all', 'unread', 'read'].map((f) => (
                  <button
                    key={f}
                    onClick={() => setNotifFilter(f)}
                    className={`px-3 py-1 rounded-full font-bold capitalize transition ${
                      notifFilter === f ? 'bg-bakery-orange text-white' : 'bg-gray-100 dark:bg-amber-950 text-gray-600 dark:text-gray-300'
                    }`}
                  >
                    {f}
                  </button>
                ))}
              </div>

              <button
                onClick={async () => {
                  try {
                    await notificationService.markAllAsRead();
                    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
                    toast.success("All notifications marked as read");
                  } catch (err) {
                    toast.error("Failed to mark all as read");
                  }
                }}
                className="text-xs font-bold text-amber-700 dark:text-amber-300 hover:text-bakery-orange flex items-center gap-1 self-start sm:self-auto"
              >
                <CheckCheck className="w-4 h-4" /> Mark All as Read
              </button>
            </div>

            {loadingNotifications ? (
              <p className="text-xs text-gray-500">Loading notifications...</p>
            ) : notifications.length === 0 ? (
              <div className="text-center py-12 bg-white dark:bg-bakery-chocolate/40 rounded-3xl p-6 border border-amber-900/10">
                <span className="text-3xl block mb-2">🥐</span>
                <p className="font-serif font-bold text-lg">No Notifications Found</p>
                <p className="text-xs text-gray-500 mt-1">You are all caught up on baking updates and orders.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {notifications.map((n) => (
                  <div
                    key={n.id}
                    className={`bg-white dark:bg-bakery-chocolate/60 p-4 rounded-2xl border transition shadow-sm flex items-start justify-between gap-4 ${
                      !n.is_read ? 'border-amber-400 bg-amber-50/40 dark:bg-amber-950/30' : 'border-amber-900/10 opacity-90'
                    }`}
                  >
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-serif font-bold text-sm text-bakery-dark dark:text-cream-100">{n.title}</span>
                        {!n.is_read && (
                          <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-bakery-orange/20 text-bakery-orange">
                            New
                          </span>
                        )}
                        <span className="text-[10px] text-gray-400">
                          {new Date(n.created_at).toLocaleDateString()} {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-300">{n.message}</p>
                      {n.link_url && (
                        <button
                          onClick={async () => {
                            if (!n.is_read) {
                              await notificationService.markAsRead(n.id);
                            }
                            navigate(n.link_url);
                          }}
                          className="mt-2 inline-flex items-center gap-1 text-xs font-bold text-bakery-orange hover:underline"
                        >
                          View Details <ExternalLink className="w-3 h-3" />
                        </button>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {!n.is_read && (
                        <button
                          onClick={async () => {
                            await notificationService.markAsRead(n.id);
                            setNotifications(prev => prev.map(item => item.id === n.id ? { ...item, is_read: true } : item));
                            toast.success("Notification marked as read");
                          }}
                          className="p-1.5 text-xs text-amber-700 dark:text-amber-300 hover:text-bakery-orange rounded-lg"
                          title="Mark read"
                        >
                          <CheckCheck className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={async () => {
                          await notificationService.deleteNotification(n.id);
                          setNotifications(prev => prev.filter(item => item.id !== n.id));
                          toast.success("Notification dismissed");
                        }}
                        className="p-1.5 text-gray-400 hover:text-red-500 rounded-lg"
                        title="Dismiss notification"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
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
