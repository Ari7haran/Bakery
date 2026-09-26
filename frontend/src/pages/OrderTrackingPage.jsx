import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { QrCode, ArrowLeft, RefreshCw } from 'lucide-react';
import { api } from '../services/api.js';
import { useToast } from '../context/ToastContext.jsx';

const statusSteps = [
  { status: 'Received', label: 'Order Received', icon: '📝' },
  { status: 'Preparing', label: 'Dough Prep', icon: '🥣' },
  { status: 'Baking', label: 'In Stone Oven', icon: '🔥' },
  { status: 'Packing', label: 'Warm Packing', icon: '🛍️' },
  { status: 'Ready for Pickup', label: 'Ready at Counter', icon: '✨' },
  { status: 'Completed', label: 'Collected', icon: '🎉' },
];

const OrderTrackingPage = () => {
  const [searchParams] = useSearchParams();
  const orderId = searchParams.get('orderId');
  const toast = useToast();
  const previousStatusRef = useRef(null);

  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchOrder = async () => {
    if (!orderId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const res = await api.get(`/orders/${orderId}`);
      const updatedOrder = res.data;

      // Detect status change and display toast without duplicate alerts
      if (previousStatusRef.current && previousStatusRef.current !== updatedOrder.status) {
        if (updatedOrder.status === 'Ready for Pickup') {
          toast.success(
            `Order #${updatedOrder.order_number} is hot & ready at the counter! ✨`,
            'Ready for Pickup'
          );
        } else {
          toast.info(
            `Order #${updatedOrder.order_number} is now ${updatedOrder.status}!`,
            'Baking Timeline Update 🥐'
          );
        }
      }
      previousStatusRef.current = updatedOrder.status;

      setOrder(updatedOrder);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || "Order not found");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrder();
    const interval = setInterval(() => {
      fetchOrder();
    }, 10000); // Auto refresh every 10s
    return () => clearInterval(interval);
  }, [orderId]);

  if (!orderId) {
    return (
      <div className="max-w-xl mx-auto py-16 px-4 text-center space-y-4">
        <h2 className="font-serif text-2xl font-bold">Track Your Bakery Order</h2>
        <p className="text-xs text-gray-500">Please enter your order ID or check your profile order history.</p>
        <Link to="/profile" className="inline-block px-6 py-2.5 bg-bakery-orange text-white font-bold text-xs rounded-full shadow">
          View My Orders
        </Link>
      </div>
    );
  }

  if (loading && !order) {
    return (
      <div className="max-w-xl mx-auto py-16 text-center space-y-2">
        <RefreshCw className="w-8 h-8 text-bakery-orange animate-spin mx-auto" />
        <p className="text-xs text-gray-500">Fetching live oven status...</p>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="max-w-xl mx-auto py-16 text-center space-y-4">
        <p className="text-red-500 font-bold">{error || "Order not found"}</p>
        <Link to="/" className="inline-block px-6 py-2.5 bg-bakery-orange text-white font-bold text-xs rounded-full">
          Back to Home
        </Link>
      </div>
    );
  }

  const currentStepIndex = statusSteps.findIndex(s => s.status === order.status);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-amber-900/10 pb-4">
        <div>
          <span className="bg-bakery-orange/20 text-bakery-orange text-[10px] font-extrabold px-3 py-1 rounded-full uppercase tracking-wider">
            Live Bakery Tracker
          </span>
          <h1 className="font-serif text-3xl font-bold mt-1">Order #{order.order_number}</h1>
        </div>
        <button onClick={fetchOrder} className="p-2 rounded-full hover:bg-amber-100 dark:hover:bg-amber-900 text-bakery-orange" title="Refresh Status">
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {/* Main Order Status Card */}
      <div className="bg-white dark:bg-bakery-chocolate/80 rounded-3xl p-6 sm:p-8 border border-amber-900/10 dark:border-amber-500/20 shadow-xl space-y-8">
        
        {/* Top Info Banner */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 bg-amber-50 dark:bg-amber-950/40 rounded-2xl border border-amber-900/10">
          <div>
            <p className="text-xs text-gray-500">{order.order_type === 'Delivery' ? 'Fulfillment Type' : 'Pickup Number'}</p>
            <p className="font-serif text-2xl font-extrabold text-bakery-orange">
              {order.order_type === 'Delivery' ? '🛵 Delivery' : (order.pickup_number || 'N/A')}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">{order.order_type === 'Delivery' ? 'Delivery Destination' : 'Scheduled Time Slot'}</p>
            <p className="text-sm font-bold text-bakery-dark dark:text-cream-100">
              {order.order_type === 'Delivery'
                ? order.delivery_address
                : `${order.pickup_date} • ${order.pickup_time_slot || 'Express Pickup'}`}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Payment Status</p>
            <span className="text-xs font-extrabold text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-950 px-2.5 py-1 rounded-full">
              {order.payment_status} ({order.payment_method})
            </span>
          </div>
        </div>

        {/* Status Timeline */}
        <div className="space-y-4">
          <h3 className="font-serif font-bold text-base text-gray-700 dark:text-amber-200">Live Kitchen & Oven Timeline</h3>
          
          <div className="grid grid-cols-2 sm:grid-cols-6 gap-2 text-center relative">
            {statusSteps.map((step, idx) => {
              const isDone = idx <= currentStepIndex;
              const isCurrent = idx === currentStepIndex;

              return (
                <div
                  key={step.status}
                  className={`p-3 rounded-2xl border transition-all ${
                    isCurrent
                      ? 'bg-gradient-to-b from-bakery-orange to-amber-500 text-white border-bakery-orange ring-4 ring-amber-500/20 scale-105 shadow-lg'
                      : isDone
                      ? 'bg-amber-100/70 dark:bg-amber-950/70 text-bakery-dark dark:text-cream-100 border-amber-300'
                      : 'bg-gray-50 dark:bg-amber-950/20 text-gray-400 border-gray-200 dark:border-amber-900/20'
                  }`}
                >
                  <span className="text-2xl block mb-1">{step.icon}</span>
                  <span className="text-[11px] font-bold block">{step.label}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Express Pickup / Delivery QR Code Display */}
        {order.qr_code_data && (
          <div className="bg-cream-100 dark:bg-amber-950/60 p-6 rounded-3xl text-center space-y-4 border border-amber-900/10">
            <div className="inline-flex items-center gap-2 text-xs font-extrabold text-bakery-orange bg-amber-200/60 dark:bg-amber-900/60 px-3 py-1 rounded-full">
              <QrCode className="w-4 h-4" /> {order.order_type === 'Delivery' ? 'Digital Delivery Receipt' : 'Scan Code at Express Counter'}
            </div>
            
            <div className="w-48 h-48 mx-auto bg-white p-3 rounded-2xl shadow-md border">
              <img src={order.qr_code_data} alt="Order QR Code" className="w-full h-full object-contain" />
            </div>

            <p className="text-xs text-gray-600 dark:text-amber-200/70 max-w-sm mx-auto">
              {order.order_type === 'Delivery'
                ? 'Keep this digital QR receipt handy for our delivery rider upon doorstep arrival!'
                : 'Show this QR receipt to our bakery express counter staff to pick up your freshly packed warm order instantly!'}
            </p>
          </div>
        )}

        {/* Ordered Items Breakdown */}
        <div className="space-y-3 pt-4 border-t border-amber-900/10">
          <h4 className="font-bold text-sm">Ordered Items ({order.items.length})</h4>
          <div className="space-y-2">
            {order.items.map((item) => (
              <div key={item.id} className="flex justify-between items-center text-xs p-2 bg-gray-50 dark:bg-amber-950/30 rounded-xl">
                <div className="flex items-center gap-2">
                  <img src={item.product?.image_url} alt={item.product?.name} className="w-8 h-8 rounded-lg object-cover" />
                  <span className="font-semibold">{item.product?.name} x {item.quantity}</span>
                </div>
                <span className="font-bold">₹{item.price * item.quantity}</span>
              </div>
            ))}
          </div>

          <div className="flex justify-between font-serif text-lg font-bold pt-3 border-t border-amber-900/10">
            <span>Total Amount Paid</span>
            <span className="text-bakery-orange">₹{order.final_amount}</span>
          </div>
        </div>

      </div>

      <div className="text-center pt-4">
        <Link to="/shop" className="inline-flex items-center gap-2 text-xs font-bold text-bakery-orange hover:underline">
          <ArrowLeft className="w-4 h-4" /> Order More Warm Bakery Delights
        </Link>
      </div>
    </div>
  );
};

export default OrderTrackingPage;
