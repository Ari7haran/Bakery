import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext.jsx';
import { api } from '../services/api.js';

const CartContext = createContext(undefined);

export const CartProvider = ({ children }) => {
  const { user } = useAuth();
  const [cart, setCart] = useState(() => {
    const saved = localStorage.getItem('sweet_crumbs_cart');
    return saved ? JSON.parse(saved) : [];
  });

  const [wishlist, setWishlist] = useState(() => {
    const saved = localStorage.getItem('sweet_crumbs_wishlist');
    return saved ? JSON.parse(saved) : [];
  });

  const [appliedCoupon, setAppliedCoupon] = useState(null);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [pickupSlot, setPickupSlot] = useState({
    date: 'Today',
    time: '04:00 PM - 04:30 PM'
  });

  useEffect(() => {
    localStorage.setItem('sweet_crumbs_cart', JSON.stringify(cart));
  }, [cart]);

  useEffect(() => {
    localStorage.setItem('sweet_crumbs_wishlist', JSON.stringify(wishlist));
  }, [wishlist]);

  const addToCart = (product, quantity = 1) => {
    setCart((prev) => {
      const existingIndex = prev.findIndex((item) => item.product.id === product.id);
      if (existingIndex > -1) {
        const updated = [...prev];
        updated[existingIndex].quantity += quantity;
        return updated;
      }
      return [...prev, { product, quantity }];
    });
    setIsCartOpen(true);
  };

  const updateQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }
    setCart((prev) =>
      prev.map((item) =>
        item.product.id === productId ? { ...item, quantity } : item
      )
    );
  };

  const removeFromCart = (productId) => {
    setCart((prev) => prev.filter((item) => item.product.id !== productId));
  };

  const clearCart = () => {
    setCart([]);
    setAppliedCoupon(null);
  };

  const toggleWishlist = (product) => {
    setWishlist((prev) => {
      const exists = prev.some((p) => p.id === product.id);
      if (exists) {
        return prev.filter((p) => p.id !== product.id);
      }
      return [...prev, product];
    });
  };

  const isInWishlist = (productId) => {
    return wishlist.some((p) => p.id === productId);
  };

  const cartCount = cart.reduce((acc, item) => acc + item.quantity, 0);

  const totalAmount = cart.reduce((acc, item) => {
    const itemPrice = item.product.discount_price || item.product.price;
    return acc + itemPrice * item.quantity;
  }, 0);

  const applyCoupon = async (code) => {
    try {
      const res = await api.post('/user/coupon/validate', {
        code,
        order_amount: totalAmount
      });
      if (res.data.valid) {
        setAppliedCoupon({
          code: res.data.code,
          discountPercent: res.data.discount_percent,
          discountAmount: res.data.discount_amount
        });
        return true;
      }
      return false;
    } catch {
      // Fallback offline validation for demo
      if (code.toUpperCase() === 'WELCOME100' && totalAmount >= 300) {
        const discount = Math.min((totalAmount * 20) / 100, 100);
        setAppliedCoupon({ code: 'WELCOME100', discountPercent: 20, discountAmount: discount });
        return true;
      }
      return false;
    }
  };

  const removeCoupon = () => {
    setAppliedCoupon(null);
  };

  const discountAmount = appliedCoupon ? appliedCoupon.discountAmount : 0;

  return (
    <CartContext.Provider
      value={{
        cart,
        wishlist,
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
        toggleWishlist,
        isInWishlist,
        cartCount,
        totalAmount,
        discountAmount,
        appliedCoupon,
        applyCoupon,
        removeCoupon,
        isCartOpen,
        setIsCartOpen,
        pickupSlot,
        setPickupSlot
      }}
    >
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) throw new Error('useCart must be used within CartProvider');
  return context;
};
