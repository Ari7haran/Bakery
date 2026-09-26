import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, CreditCard, QrCode, CheckCircle2 } from 'lucide-react';
import { useCart } from '../context/CartContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { useToast } from '../context/ToastContext.jsx';
import { api } from '../services/api.js';
import PickupModal from '../components/PickupModal.jsx';

const CheckoutPage = () => {
  const { cart, totalAmount, discountAmount, appliedCoupon, applyCoupon, removeCoupon, pickupSlot, clearCart } = useCart();
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const [orderType, setOrderType] = useState('Takeaway Pickup');
  const [paymentMethod, setPaymentMethod] = useState('Cash on Pickup');
  const [isPickupModalOpen, setIsPickupModalOpen] = useState(false);
  
  // Customer details form
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [phone, setPhone] = useState(user?.phone || '');
  const [address, setAddress] = useState('123 Main Street, Apt 4B, City');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [checkoutCouponCode, setCheckoutCouponCode] = useState('');
  const [checkoutCouponError, setCheckoutCouponError] = useState('');
  const [checkoutCouponSuccess, setCheckoutCouponSuccess] = useState('');
  const [isApplyingCoupon, setIsApplyingCoupon] = useState(false);

  const finalTotal = Math.max(0, totalAmount - discountAmount);

  const handleApplyCheckoutCoupon = async (codeToUse = null) => {
    const code = codeToUse || checkoutCouponCode;
    if (!code || !code.trim()) return;
    setCheckoutCouponError('');
    setCheckoutCouponSuccess('');
    setIsApplyingCoupon(true);
    const res = await applyCoupon(code.trim());
    setIsApplyingCoupon(false);
    if (res && res.success) {
      setCheckoutCouponSuccess(res.message);
      setCheckoutCouponCode('');
    } else {
      setCheckoutCouponError(res?.message || 'Invalid coupon code or order amount too low.');
    }
  };

  const handlePlaceOrder = async (e) => {
    e.preventDefault();
    if (cart.length === 0) return;

    setLoading(true);
    try {
      const payload = {
        order_type: orderType,
        pickup_date: orderType === 'Takeaway Pickup' ? (pickupSlot?.date || 'Today') : null,
        pickup_time_slot: orderType === 'Takeaway Pickup' ? (pickupSlot?.time || '04:00 PM - 04:30 PM') : null,
        delivery_address: orderType === 'Delivery' ? address : null,
        payment_method: orderType === 'Takeaway Pickup' ? 'Cash on Pickup' : 'Cash on Delivery',
        coupon_code: appliedCoupon ? appliedCoupon.code : null,
        notes: notes,
        items: cart.map((item) => ({
          product_id: item.product.id,
          quantity: item.quantity,
        })),
      };

      const res = await api.post('/orders/', payload);
      clearCart();
      toast.success("Order placed successfully! Check notifications for updates.");
      navigate(`/track?orderId=${res.data.id}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to place order. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (cart.length === 0) {
    return (
      <div className="max-w-xl mx-auto py-16 text-center space-y-4">
        <p className="font-serif text-2xl font-bold">Your Cart is Empty!</p>
        <p className="text-xs text-gray-500">Please add items to your cart before proceeding to checkout.</p>
        <button onClick={() => navigate('/shop')} className="px-6 py-2.5 bg-bakery-orange text-white font-bold text-xs rounded-full shadow">
          Explore Bakery Items
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="border-b border-amber-900/10 pb-4">
        <h1 className="font-serif text-3xl font-bold">Express Checkout</h1>
        <p className="text-xs text-gray-500 dark:text-amber-200/60 mt-1">
          Review items, schedule express takeaway pickup, and complete payment
        </p>
      </div>

      <form onSubmit={handlePlaceOrder} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Form Sections */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Order Type Toggle */}
          <div className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-sm space-y-4">
            <h3 className="font-serif font-bold text-base flex items-center gap-2">
              <Clock className="w-5 h-5 text-bakery-orange" /> Select Fulfillment Method
            </h3>

            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setOrderType('Takeaway Pickup')}
                className={`p-4 rounded-2xl border text-left transition flex flex-col justify-between ${
                  orderType === 'Takeaway Pickup'
                    ? 'border-bakery-orange bg-amber-50 dark:bg-amber-950/40 text-bakery-dark dark:text-cream-100 ring-2 ring-bakery-orange'
                    : 'border-amber-900/10 text-gray-600 dark:text-amber-200/60'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="font-bold text-sm">🥐 Express Counter Pickup</span>
                  {orderType === 'Takeaway Pickup' && <CheckCircle2 className="w-4 h-4 text-bakery-orange" />}
                </div>
                <p className="text-[11px] text-gray-500 mt-1">Zero wait time • Scan QR at pickup counter</p>
              </button>

              <button
                type="button"
                onClick={() => setOrderType('Delivery')}
                className={`p-4 rounded-2xl border text-left transition flex flex-col justify-between ${
                  orderType === 'Delivery'
                    ? 'border-bakery-orange bg-amber-50 dark:bg-amber-950/40 text-bakery-dark dark:text-cream-100 ring-2 ring-bakery-orange'
                    : 'border-amber-900/10 text-gray-600 dark:text-amber-200/60'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="font-bold text-sm">🛵 Doorstep Delivery</span>
                  {orderType === 'Delivery' && <CheckCircle2 className="w-4 h-4 text-bakery-orange" />}
                </div>
                <p className="text-[11px] text-gray-500 mt-1">Delivered warm within 30-45 mins</p>
              </button>
            </div>

            {/* If Takeaway Pickup */}
            {orderType === 'Takeaway Pickup' && (
              <div className="p-4 bg-amber-100/60 dark:bg-amber-950/60 rounded-2xl flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-amber-950 dark:text-amber-200 block">Scheduled Pickup Window:</span>
                  <span className="text-sm font-extrabold text-bakery-orange">
                    {pickupSlot ? `${pickupSlot.date} (${pickupSlot.time})` : 'Today (04:00 PM - 04:30 PM)'}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setIsPickupModalOpen(true)}
                  className="px-3 py-1.5 bg-bakery-brown text-white text-xs font-bold rounded-xl hover:bg-bakery-orange transition"
                >
                  Change Slot
                </button>
              </div>
            )}

            {/* If Delivery */}
            {orderType === 'Delivery' && (
              <div className="space-y-2">
                <label className="block text-xs font-bold">Delivery Street Address</label>
                <input
                  type="text"
                  required
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  className="w-full p-3 text-xs rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/30"
                />
              </div>
            )}
          </div>

          {/* Customer Details */}
          <div className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-sm space-y-4">
            <h3 className="font-serif font-bold text-base">Customer Details</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full p-3 text-xs rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/30"
                />
              </div>
              <div>
                <label className="block text-xs font-bold mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full p-3 text-xs rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/30"
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-xs font-bold mb-1">Phone Number (For Order SMS Updates)</label>
                <input
                  type="tel"
                  required
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+1 (555) 019-2834"
                  className="w-full p-3 text-xs rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/30"
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-xs font-bold mb-1">Order Notes / Birthday Cake Inscription</label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="E.g. Extra napkins please, or write 'Happy Birthday Sarah' on cake"
                  className="w-full p-3 text-xs rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/30"
                />
              </div>
            </div>
          </div>

          {/* Payment Method */}
          <div className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-serif font-bold text-base flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-bakery-orange" /> Payment Method
              </h3>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/50 text-bakery-orange">
                Cash Only Bakery
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {orderType === 'Takeaway Pickup' ? (
                <div className="p-4 rounded-2xl border border-bakery-orange bg-amber-50 dark:bg-amber-950/40 ring-2 ring-bakery-orange flex items-center gap-3">
                  <input
                    type="radio"
                    name="payment"
                    checked={true}
                    readOnly
                    className="accent-bakery-orange"
                  />
                  <div>
                    <span className="font-bold text-xs block">Cash on Pickup</span>
                    <span className="text-[10px] text-gray-500">Pay cash at bakery counter upon order collection</span>
                  </div>
                </div>
              ) : (
                <div className="p-4 rounded-2xl border border-bakery-orange bg-amber-50 dark:bg-amber-950/40 ring-2 ring-bakery-orange flex items-center gap-3">
                  <input
                    type="radio"
                    name="payment"
                    checked={true}
                    readOnly
                    className="accent-bakery-orange"
                  />
                  <div>
                    <span className="font-bold text-xs block">Cash on Delivery</span>
                    <span className="text-[10px] text-gray-500">Pay cash to our delivery executive at your doorstep</span>
                  </div>
                </div>
              )}

              <div className="p-4 rounded-2xl border border-dashed border-gray-300 dark:border-amber-900/30 bg-gray-50 dark:bg-amber-950/20 opacity-60 flex items-center gap-3 cursor-not-allowed">
                <input
                  type="radio"
                  name="payment_disabled"
                  disabled={true}
                  className="accent-gray-400"
                />
                <div>
                  <span className="font-bold text-xs block text-gray-400">Online Payment / UPI</span>
                  <span className="text-[10px] text-gray-400">Coming soon in future release</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Summary Card */}
        <div className="space-y-6">
          <div className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-md space-y-4 sticky top-24">
            <h3 className="font-serif font-bold text-lg border-b border-amber-900/10 pb-3">Order Summary</h3>

            {/* Cart Items List */}
            <div className="space-y-3 max-h-56 overflow-y-auto pr-1">
              {cart.map(({ product, quantity }) => {
                const itemPrice = product.discount_price || product.price;
                return (
                  <div key={product.id} className="flex justify-between items-center text-xs">
                    <div className="flex items-center gap-2">
                      <img src={product.image_url} alt={product.name} className="w-9 h-9 rounded-lg object-cover" />
                      <div>
                        <p className="font-bold line-clamp-1">{product.name}</p>
                        <p className="text-[10px] text-gray-500">Qty: {quantity}</p>
                      </div>
                    </div>
                    <span className="font-bold">₹{itemPrice * quantity}</span>
                  </div>
                );
              })}
            </div>

            {/* Coupon / Promo Code Section */}
            {appliedCoupon ? (
              <div className="space-y-1.5 pt-2 border-t border-amber-900/10">
                <div className="flex justify-between items-center text-xs text-emerald-600 dark:text-emerald-400 font-bold bg-emerald-50 dark:bg-emerald-950/50 p-2.5 rounded-xl border border-emerald-200">
                  <span>Coupon ({appliedCoupon.code})</span>
                  <div className="flex items-center gap-2">
                    <span>-₹{discountAmount}</span>
                    <button
                      type="button"
                      onClick={removeCoupon}
                      className="text-red-500 hover:underline text-[10px] font-bold"
                    >
                      Remove
                    </button>
                  </div>
                </div>
                {appliedCoupon.minOrderAmount && totalAmount < appliedCoupon.minOrderAmount && (
                  <p className="text-[10px] text-amber-600 font-medium">
                    Add ₹{(appliedCoupon.minOrderAmount - totalAmount).toFixed(0)} more to activate discount.
                  </p>
                )}
              </div>
            ) : (
              <div className="space-y-2 pt-2 border-t border-amber-900/10">
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Promo Code"
                    value={checkoutCouponCode}
                    onChange={(e) => setCheckoutCouponCode(e.target.value)}
                    className="flex-1 px-3 py-1.5 text-xs rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/20 uppercase focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => handleApplyCheckoutCoupon()}
                    disabled={isApplyingCoupon}
                    className="px-3.5 py-1.5 bg-bakery-brown text-white text-xs font-bold rounded-xl hover:bg-bakery-orange transition disabled:opacity-50"
                  >
                    {isApplyingCoupon ? 'Applying...' : 'Apply'}
                  </button>
                </div>
                {checkoutCouponError && <p className="text-[10px] text-red-500">{checkoutCouponError}</p>}
                {checkoutCouponSuccess && <p className="text-[10px] text-emerald-600 font-medium">{checkoutCouponSuccess}</p>}
                <div className="flex items-center gap-1.5 flex-wrap pt-0.5">
                  <span className="text-[10px] text-gray-400">Offers:</span>
                  {['WELCOME100', 'SWEET50', 'FESTIVE25'].map((code) => (
                    <button
                      key={code}
                      type="button"
                      onClick={() => handleApplyCheckoutCoupon(code)}
                      className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-50 dark:bg-amber-950/40 text-bakery-orange border border-amber-200 dark:border-amber-800 hover:bg-bakery-orange hover:text-white transition"
                    >
                      {code}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-2 text-xs pt-3 border-t border-amber-900/10">
              <div className="flex justify-between text-gray-500">
                <span>Items Total</span>
                <span>₹{totalAmount}</span>
              </div>
              <div className="flex justify-between text-gray-500">
                <span>Tax & Packaging</span>
                <span className="text-emerald-600 font-bold">FREE</span>
              </div>
              <div className="flex justify-between font-serif text-lg font-extrabold pt-2 border-t border-amber-900/10 text-bakery-dark dark:text-cream-100">
                <span>Total Amount</span>
                <span className="text-bakery-orange">₹{finalTotal}</span>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 bg-gradient-to-r from-bakery-brown via-bakery-orange to-amber-500 text-white font-extrabold text-sm rounded-2xl shadow-xl hover:opacity-95 transition flex items-center justify-center gap-2"
            >
              <QrCode className="w-5 h-5" />
              <span>{loading ? 'Processing Order...' : `Confirm Order & Get Pickup QR Code • ₹${finalTotal}`}</span>
            </button>
          </div>
        </div>

      </form>

      <PickupModal isOpen={isPickupModalOpen} onClose={() => setIsPickupModalOpen(false)} />
    </div>
  );
};

export default CheckoutPage;
