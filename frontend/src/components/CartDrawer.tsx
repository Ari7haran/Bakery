import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { X, Trash2, Plus, Minus, Tag, Clock, ArrowRight, ShoppingBag, Sparkles } from 'lucide-react';
import { useCart } from '../context/CartContext';

const CartDrawer: React.FC = () => {
  const {
    cart,
    updateQuantity,
    removeFromCart,
    isCartOpen,
    setIsCartOpen,
    totalAmount,
    discountAmount,
    appliedCoupon,
    applyCoupon,
    removeCoupon,
    pickupSlot
  } = useCart();

  const [couponCode, setCouponCode] = useState('');
  const [couponError, setCouponError] = useState('');

  if (!isCartOpen) return null;

  const finalTotal = Math.max(0, totalAmount - discountAmount);

  const handleApplyCoupon = async (e: React.FormEvent) => {
    e.preventDefault();
    setCouponError('');
    if (!couponCode.trim()) return;

    const success = await applyCoupon(couponCode);
    if (!success) {
      setCouponError('Invalid coupon code or order amount too low.');
    } else {
      setCouponCode('');
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        onClick={() => setIsCartOpen(false)}
        className="absolute inset-0 bg-black/60 backdrop-blur-xs transition-opacity animate-in fade-in"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-cream-50 dark:bg-bakery-chocolate text-bakery-dark dark:text-cream-100 shadow-2xl border-l border-amber-900/10 dark:border-amber-500/20 flex flex-col justify-between">
          
          {/* Header */}
          <div className="p-4 sm:p-6 border-b border-amber-900/10 dark:border-amber-500/10 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShoppingBag className="w-5 h-5 text-bakery-orange" />
              <h2 className="font-serif text-xl font-bold">Your Fresh Order</h2>
              <span className="bg-bakery-orange/20 text-bakery-orange text-xs font-extrabold px-2.5 py-0.5 rounded-full">
                {cart.length} Items
              </span>
            </div>
            <button
              onClick={() => setIsCartOpen(false)}
              className="p-2 rounded-full hover:bg-amber-900/10 dark:hover:bg-cream-100/10 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Pickup Slot Notice */}
          <div className="bg-amber-100/60 dark:bg-amber-950/40 px-4 py-2.5 border-b border-amber-900/10 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-bakery-brown dark:text-amber-300" />
              <div>
                <span className="font-bold">Takeaway Pickup: </span>
                <span>{pickupSlot ? `${pickupSlot.date} (${pickupSlot.time})` : 'Default Slot'}</span>
              </div>
            </div>
          </div>

          {/* Items List */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
            {cart.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center text-gray-500 py-12">
                <div className="w-16 h-16 rounded-full bg-amber-100 dark:bg-amber-950/50 flex items-center justify-center text-3xl mb-3">
                  🥐
                </div>
                <p className="font-serif font-bold text-lg text-bakery-dark dark:text-cream-100">Your cart is empty!</p>
                <p className="text-xs max-w-xs mt-1">Explore our artisanal oven fresh breads, croissants & pastries.</p>
                <button
                  onClick={() => setIsCartOpen(false)}
                  className="mt-4 px-5 py-2 bg-bakery-orange text-white text-xs font-bold rounded-xl shadow"
                >
                  Explore Menu
                </button>
              </div>
            ) : (
              cart.map(({ product, quantity }) => {
                const itemPrice = product.discount_price || product.price;
                return (
                  <div
                    key={product.id}
                    className="flex gap-3 bg-white dark:bg-amber-950/30 p-3 rounded-2xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs"
                  >
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-16 h-16 rounded-xl object-cover"
                    />
                    <div className="flex-1 flex flex-col justify-between">
                      <div>
                        <div className="flex justify-between items-start">
                          <h4 className="font-bold text-xs line-clamp-1">{product.name}</h4>
                          <button
                            onClick={() => removeFromCart(product.id)}
                            className="text-gray-400 hover:text-red-500 transition"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                        <p className="text-[11px] text-amber-700 dark:text-amber-300 font-bold mt-0.5">
                          ₹{itemPrice} x {quantity} = ₹{itemPrice * quantity}
                        </p>
                      </div>

                      {/* Quantity Buttons */}
                      <div className="flex items-center gap-2 mt-2">
                        <div className="flex items-center border border-amber-900/20 dark:border-amber-500/20 rounded-lg overflow-hidden bg-cream-50 dark:bg-amber-900/20">
                          <button
                            onClick={() => updateQuantity(product.id, quantity - 1)}
                            className="p-1 hover:bg-amber-200 dark:hover:bg-amber-800 transition"
                          >
                            <Minus className="w-3 h-3" />
                          </button>
                          <span className="px-2 text-xs font-bold">{quantity}</span>
                          <button
                            onClick={() => updateQuantity(product.id, quantity + 1)}
                            className="p-1 hover:bg-amber-200 dark:hover:bg-amber-800 transition"
                          >
                            <Plus className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Footer & Checkout */}
          {cart.length > 0 && (
            <div className="p-4 sm:p-6 border-t border-amber-900/10 dark:border-amber-500/10 bg-white dark:bg-amber-950/50 space-y-3">
              {/* Coupon Form */}
              {appliedCoupon ? (
                <div className="flex items-center justify-between bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 p-2.5 rounded-xl border border-emerald-200 text-xs font-semibold">
                  <div className="flex items-center gap-1.5">
                    <Tag className="w-4 h-4" />
                    <span>Coupon <strong>{appliedCoupon.code}</strong> Applied (-₹{appliedCoupon.discountAmount})</span>
                  </div>
                  <button onClick={removeCoupon} className="text-red-500 hover:underline text-[10px]">Remove</button>
                </div>
              ) : (
                <form onSubmit={handleApplyCoupon} className="space-y-1">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Coupon Code (e.g. WELCOME100)"
                      value={couponCode}
                      onChange={(e) => setCouponCode(e.target.value)}
                      className="flex-1 px-3 py-1.5 text-xs rounded-xl border border-amber-900/20 dark:border-amber-500/20 bg-cream-50 dark:bg-amber-900/20 uppercase"
                    />
                    <button
                      type="submit"
                      className="px-3 py-1.5 bg-bakery-brown text-white text-xs font-bold rounded-xl hover:bg-bakery-orange transition"
                    >
                      Apply
                    </button>
                  </div>
                  {couponError && <p className="text-[10px] text-red-500">{couponError}</p>}
                </form>
              )}

              {/* Price Calculation */}
              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between text-gray-600 dark:text-amber-200/70">
                  <span>Subtotal</span>
                  <span>₹{totalAmount}</span>
                </div>
                {discountAmount > 0 && (
                  <div className="flex justify-between text-emerald-600 dark:text-emerald-400 font-semibold">
                    <span>Discount</span>
                    <span>-₹{discountAmount}</span>
                  </div>
                )}
                <div className="flex justify-between text-gray-600 dark:text-amber-200/70">
                  <span>Estimated Taxes & Packaging</span>
                  <span className="text-emerald-600 font-semibold">FREE</span>
                </div>
                <div className="flex justify-between font-serif text-base font-extrabold text-bakery-dark dark:text-cream-100 pt-2 border-t border-amber-900/10">
                  <span>Total Amount</span>
                  <span className="text-bakery-orange">₹{finalTotal}</span>
                </div>
              </div>

              {/* Checkout CTA */}
              <Link
                to="/checkout"
                onClick={() => setIsCartOpen(false)}
                className="w-full py-3 bg-gradient-to-r from-bakery-brown via-bakery-orange to-amber-500 text-white font-bold text-sm rounded-2xl shadow-xl hover:opacity-95 transition flex items-center justify-center gap-2 group"
              >
                <span>Proceed to Express Checkout</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition" />
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CartDrawer;
