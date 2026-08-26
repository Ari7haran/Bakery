import React from 'react';
import { Link } from 'react-router-dom';
import { Star, Heart, Plus, Clock, Flame } from 'lucide-react';
import { useCart } from '../context/CartContext.jsx';

const ProductCard = ({ product }) => {
  const { addToCart, toggleWishlist, isInWishlist } = useCart();
  const inWishlist = isInWishlist(product.id);

  const displayPrice = product.discount_price || product.price;
  const hasDiscount = !!product.discount_price;

  return (
    <div className="group relative bg-white dark:bg-bakery-chocolate/80 rounded-3xl overflow-hidden border border-amber-900/10 dark:border-amber-500/20 shadow-md hover:shadow-2xl transition-all duration-300 flex flex-col justify-between">
      {/* Image Container */}
      <div className="relative aspect-4/3 overflow-hidden bg-amber-50 dark:bg-amber-950/30">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover group-hover:scale-108 transition-transform duration-500"
          loading="lazy"
        />

        {/* Badges Overlay */}
        <div className="absolute top-3 left-3 flex flex-col gap-1.5 z-10">
          {/* Veg / Non-Veg Indicator */}
          <span className="w-5 h-5 bg-white/90 dark:bg-slate-900/90 backdrop-blur rounded-sm border border-gray-300 p-0.5 flex items-center justify-center">
            <span className={`w-2.5 h-2.5 rounded-full ${product.is_veg ? 'bg-green-600' : 'bg-red-600'}`}></span>
          </span>

          {product.is_todays_fresh && (
            <span className="bg-gradient-to-r from-amber-500 to-orange-500 text-white text-[10px] font-extrabold px-2.5 py-0.5 rounded-full shadow flex items-center gap-1">
              <Flame className="w-3 h-3" /> Fresh Baked
            </span>
          )}

          {hasDiscount && (
            <span className="bg-red-500 text-white text-[10px] font-extrabold px-2.5 py-0.5 rounded-full shadow">
              SALE
            </span>
          )}
        </div>

        {/* Wishlist Button */}
        <button
          onClick={() => toggleWishlist(product)}
          className={`absolute top-3 right-3 w-8 h-8 rounded-full flex items-center justify-center transition shadow-md ${
            inWishlist
              ? 'bg-red-500 text-white'
              : 'bg-white/80 dark:bg-slate-900/80 backdrop-blur text-gray-700 dark:text-gray-200 hover:text-red-500'
          }`}
          title={inWishlist ? 'Remove from Wishlist' : 'Add to Wishlist'}
        >
          <Heart className={`w-4 h-4 ${inWishlist ? 'fill-current' : ''}`} />
        </button>

        {/* Prep Time Tag */}
        <div className="absolute bottom-2 left-3 bg-black/60 backdrop-blur text-white text-[10px] px-2 py-0.5 rounded-md flex items-center gap-1">
          <Clock className="w-3 h-3 text-amber-300" />
          <span>{product.prep_time}</span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between gap-1 mb-1">
            <div className="flex items-center gap-1 text-amber-500 font-bold text-xs">
              <Star className="w-3.5 h-3.5 fill-current" />
              <span>{product.rating}</span>
              <span className="text-gray-400 font-normal text-[10px]">({product.review_count})</span>
            </div>
            <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold bg-emerald-50 dark:bg-emerald-950/50 px-2 py-0.5 rounded-full">
              In Stock ({product.stock_quantity})
            </span>
          </div>

          <Link to={`/product/${product.id}`}>
            <h3 className="font-serif font-bold text-base text-bakery-dark dark:text-cream-100 group-hover:text-bakery-orange transition line-clamp-1">
              {product.name}
            </h3>
          </Link>

          <p className="text-xs text-gray-500 dark:text-amber-200/70 line-clamp-2 mt-1 mb-3">
            {product.description}
          </p>
        </div>

        {/* Pricing & Add Button */}
        <div className="flex items-center justify-between pt-2 border-t border-amber-900/10 dark:border-amber-500/10">
          <div className="flex items-baseline gap-1.5">
            <span className="font-extrabold text-base text-bakery-dark dark:text-cream-100">
              ₹{displayPrice}
            </span>
            {hasDiscount && (
              <span className="text-xs text-gray-400 line-through font-normal">
                ₹{product.price}
              </span>
            )}
          </div>

          <button
            onClick={() => addToCart(product, 1)}
            className="flex items-center gap-1.5 bg-bakery-orange hover:bg-bakery-brown text-white text-xs font-bold px-3 py-1.5 rounded-xl transition shadow-md group/btn"
          >
            <Plus className="w-3.5 h-3.5 group-hover/btn:rotate-90 transition transform" />
            <span>Add</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
