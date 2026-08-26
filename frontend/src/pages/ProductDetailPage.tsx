import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Star, Heart, Plus, Minus, Clock, ShieldCheck, ShoppingBag, Sparkles, ChevronRight, Award } from 'lucide-react';
import { api } from '../services/api';
import { Product, Review } from '../types';
import { useCart } from '../context/CartContext';
import ProductCard from '../components/ProductCard';

const ProductDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { addToCart, toggleWishlist, isInWishlist } = useCart();

  const [product, setProduct] = useState<Product | null>(null);
  const [recommendations, setRecommendations] = useState<Product[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [quantity, setQuantity] = useState(1);
  const [activeTab, setActiveTab] = useState<'description' | 'ingredients' | 'nutrition' | 'reviews'>('description');
  
  // Review submission
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);

  useEffect(() => {
    if (!id) return;
    const fetchDetails = async () => {
      try {
        const [prodRes, recRes, revRes] = await Promise.all([
          api.get(`/products/${id}`),
          api.get(`/products/recommendations/${id}`),
          api.get(`/products/${id}/reviews`)
        ]);
        setProduct(prodRes.data);
        setRecommendations(recRes.data);
        setReviews(revRes.data);
      } catch (err) {
        console.error("Failed to load product details", err);
      }
    };
    fetchDetails();
  }, [id]);

  if (!product) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <p className="animate-pulse">Loading warm bakery details...</p>
      </div>
    );
  }

  const inWishlist = isInWishlist(product.id);
  const displayPrice = product.discount_price || product.price;

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    setSubmittingReview(true);
    try {
      const res = await api.post('/reviews', {
        product_id: product.id,
        rating: newRating,
        comment: newComment
      });
      setReviews([res.data, ...reviews]);
      setNewComment('');
      alert("Thank you! Your review has been added.");
    } catch {
      alert("Please sign in to submit a review.");
    } finally {
      setSubmittingReview(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-xs text-gray-500 dark:text-amber-200/60">
        <Link to="/" className="hover:text-bakery-orange">Home</Link>
        <ChevronRight className="w-3 h-3" />
        <Link to="/shop" className="hover:text-bakery-orange">Shop</Link>
        <ChevronRight className="w-3 h-3" />
        <span className="font-bold text-bakery-dark dark:text-cream-100">{product.name}</span>
      </nav>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        {/* Product Image Gallery */}
        <div className="space-y-4">
          <div className="relative aspect-4/3 rounded-3xl overflow-hidden shadow-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-900/10">
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full h-full object-cover hover:scale-105 transition duration-500"
            />
            <button
              onClick={() => toggleWishlist(product)}
              className={`absolute top-4 right-4 p-3 rounded-full shadow-lg backdrop-blur ${
                inWishlist ? 'bg-red-500 text-white' : 'bg-white/80 dark:bg-slate-900/80 text-gray-700 hover:text-red-500'
              }`}
            >
              <Heart className={`w-5 h-5 ${inWishlist ? 'fill-current' : ''}`} />
            </button>
          </div>
        </div>

        {/* Product Info */}
        <div className="space-y-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="w-5 h-5 bg-white dark:bg-slate-900 border border-gray-300 rounded p-0.5 flex items-center justify-center">
                <span className={`w-2.5 h-2.5 rounded-full ${product.is_veg ? 'bg-green-600' : 'bg-red-600'}`} />
              </span>
              <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-3 py-1 rounded-full">
                {product.stock_quantity > 0 ? `In Stock (${product.stock_quantity} available)` : 'Out of Stock'}
              </span>
            </div>

            <h1 className="font-serif text-3xl sm:text-4xl font-extrabold">{product.name}</h1>

            <div className="flex items-center gap-4 mt-3">
              <div className="flex items-center gap-1 text-amber-500 font-extrabold text-sm">
                <Star className="w-4 h-4 fill-current" />
                <span>{product.rating}</span>
                <span className="text-gray-400 text-xs font-normal">({product.review_count} Customer Reviews)</span>
              </div>
              <span className="text-gray-300">|</span>
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Clock className="w-4 h-4 text-bakery-orange" />
                <span>Bake Prep: {product.prep_time}</span>
              </div>
            </div>
          </div>

          {/* Pricing */}
          <div className="p-4 bg-amber-100/50 dark:bg-amber-950/40 rounded-2xl flex items-baseline gap-3">
            <span className="font-serif text-3xl font-extrabold text-bakery-orange">
              ₹{displayPrice}
            </span>
            {product.discount_price && (
              <span className="text-base text-gray-400 line-through">
                ₹{product.price}
              </span>
            )}
            <span className="text-xs text-amber-700 dark:text-amber-300 font-semibold ml-auto">
              (Includes All Taxes)
            </span>
          </div>

          <p className="text-sm text-gray-600 dark:text-amber-100/80 leading-relaxed">
            {product.description}
          </p>

          {/* Quantity and Add to Cart */}
          <div className="flex flex-col sm:flex-row items-center gap-4 pt-4 border-t border-amber-900/10">
            <div className="flex items-center border border-amber-900/20 dark:border-amber-500/20 rounded-2xl overflow-hidden bg-white dark:bg-amber-950/40 p-1">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="p-2 hover:bg-amber-100 dark:hover:bg-amber-900 rounded-xl transition"
              >
                <Minus className="w-4 h-4" />
              </button>
              <span className="px-4 font-bold text-sm">{quantity}</span>
              <button
                onClick={() => setQuantity(quantity + 1)}
                className="p-2 hover:bg-amber-100 dark:hover:bg-amber-900 rounded-xl transition"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>

            <button
              onClick={() => addToCart(product, quantity)}
              className="flex-1 w-full sm:w-auto py-3.5 px-6 bg-gradient-to-r from-bakery-brown to-bakery-orange text-white font-extrabold text-sm rounded-2xl shadow-xl hover:opacity-95 transition flex items-center justify-center gap-2"
            >
              <ShoppingBag className="w-5 h-5" />
              <span>Add {quantity} to Cart • ₹{displayPrice * quantity}</span>
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs text-gray-500 pt-4">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>Takeaway Pickup Ready</span>
            </div>
            <div className="flex items-center gap-2">
              <Award className="w-4 h-4 text-amber-500" />
              <span>100% Organic Wheat</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs: Description, Ingredients, Nutrition, Reviews */}
      <div className="bg-white dark:bg-bakery-chocolate/60 rounded-3xl p-6 border border-amber-900/10 dark:border-amber-500/20 shadow-md">
        <div className="flex border-b border-amber-900/10 gap-6 overflow-x-auto">
          {(['description', 'ingredients', 'nutrition', 'reviews'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 text-xs font-bold uppercase tracking-wider transition border-b-2 ${
                activeTab === tab
                  ? 'border-bakery-orange text-bakery-orange font-extrabold'
                  : 'border-transparent text-gray-500 hover:text-bakery-dark dark:hover:text-cream-100'
              }`}
            >
              {tab} {tab === 'reviews' && `(${reviews.length})`}
            </button>
          ))}
        </div>

        <div className="pt-6 text-sm">
          {activeTab === 'description' && (
            <div className="space-y-3 leading-relaxed text-gray-600 dark:text-amber-100/80">
              <p>{product.description}</p>
              <p>Baked in authentic stone ovens with controlled humidity for maximum puff expansion and rich caramelization.</p>
            </div>
          )}

          {activeTab === 'ingredients' && (
            <div className="space-y-2">
              <h4 className="font-bold text-xs uppercase text-amber-600">Pure Organic Ingredients</h4>
              <p className="text-gray-600 dark:text-amber-100/80">{product.ingredients || 'Organic Wheat Flour, Normandy Butter, Water, Cane Sugar, Yeast, Sea Salt.'}</p>
            </div>
          )}

          {activeTab === 'nutrition' && (
            <div className="space-y-2">
              <h4 className="font-bold text-xs uppercase text-amber-600">Nutritional Profile (Per Serving)</h4>
              <p className="text-gray-600 dark:text-amber-100/80">{product.nutrition_info || 'Calories: 240kcal | Protein: 5g | Carbs: 34g | Fat: 10g'}</p>
            </div>
          )}

          {activeTab === 'reviews' && (
            <div className="space-y-6">
              {/* Review Submission Form */}
              <form onSubmit={handleReviewSubmit} className="bg-amber-50 dark:bg-amber-950/30 p-4 rounded-2xl space-y-3 border border-amber-900/10">
                <h4 className="font-bold text-xs uppercase">Leave a Verified Review</h4>
                <div className="flex items-center gap-2">
                  <label className="text-xs">Rating:</label>
                  <select
                    value={newRating}
                    onChange={(e) => setNewRating(Number(e.target.value))}
                    className="px-2 py-1 text-xs rounded border bg-white dark:bg-amber-900"
                  >
                    <option value={5}>⭐⭐⭐⭐⭐ (5/5 Excellent)</option>
                    <option value={4}>⭐⭐⭐⭐ (4/5 Very Good)</option>
                    <option value={3}>⭐⭐⭐ (3/5 Average)</option>
                  </select>
                </div>
                <textarea
                  required
                  rows={2}
                  placeholder="Share your taste experience..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  className="w-full p-3 text-xs rounded-xl border border-amber-900/20 bg-white dark:bg-amber-900/30 focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={submittingReview}
                  className="px-4 py-2 bg-bakery-orange text-white text-xs font-bold rounded-xl hover:bg-bakery-brown transition"
                >
                  Submit Review
                </button>
              </form>

              {/* Review list */}
              <div className="space-y-4">
                {reviews.length === 0 ? (
                  <p className="text-xs text-gray-500">No customer reviews yet. Be the first to review!</p>
                ) : (
                  reviews.map((r) => (
                    <div key={r.id} className="p-4 rounded-2xl border border-amber-900/10 space-y-1">
                      <div className="flex justify-between items-center">
                        <span className="font-bold text-xs">{r.user?.full_name || 'Anonymous Customer'}</span>
                        <span className="text-amber-500 font-bold text-xs">{"★".repeat(r.rating)}</span>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-amber-100/80">{r.comment}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* AI Frequently Bought Together Recommendations */}
      <section className="space-y-6">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-bakery-orange" />
          <h2 className="font-serif text-2xl font-bold">Frequently Bought Together</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {recommendations.map((rec) => (
            <ProductCard key={rec.id} product={rec} />
          ))}
        </div>
      </section>
    </div>
  );
};

export default ProductDetailPage;
