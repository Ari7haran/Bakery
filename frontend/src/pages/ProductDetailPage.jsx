import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Star,
  Heart,
  Plus,
  Minus,
  Clock,
  ShieldCheck,
  ShoppingBag,
  Sparkles,
  ChevronRight,
  Award,
  Edit3,
  Trash2,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  MessageSquare
} from 'lucide-react';
import { api } from '../services/api.js';
import { useCart } from '../context/CartContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import ProductCard from '../components/ProductCard.jsx';

const StarPicker = ({ rating, setRating, editable = true, size = "w-5 h-5" }) => {
  const [hoverRating, setHoverRating] = useState(0);

  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => {
        const isFilled = (hoverRating || rating) >= star;
        return (
          <button
            key={star}
            type="button"
            disabled={!editable}
            onClick={() => editable && setRating(star)}
            onMouseEnter={() => editable && setHoverRating(star)}
            onMouseLeave={() => editable && setHoverRating(0)}
            className={`${editable ? 'cursor-pointer transition hover:scale-110' : 'cursor-default'} focus:outline-none`}
            aria-label={`${star} star`}
          >
            <Star
              className={`${size} ${
                isFilled
                  ? 'text-amber-400 fill-amber-400'
                  : 'text-gray-300 dark:text-gray-600'
              }`}
            />
          </button>
        );
      })}
    </div>
  );
};

const ProductDetailPage = () => {
  const { id } = useParams();
  const { addToCart, toggleWishlist, isInWishlist } = useCart();
  const { user } = useAuth();

  const [product, setProduct] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loadingRecommendations, setLoadingRecommendations] = useState(true);
  const [reviews, setReviews] = useState([]);
  const [reviewsLoading, setReviewsLoading] = useState(true);
  const [reviewsError, setReviewsError] = useState(null);
  const [reviewSort, setReviewSort] = useState('newest');

  const [quantity, setQuantity] = useState(1);
  const [activeTab, setActiveTab] = useState('description');

  // Review submission state
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(null);

  // Review editing state
  const [editingReviewId, setEditingReviewId] = useState(null);
  const [editRating, setEditRating] = useState(5);
  const [editComment, setEditComment] = useState('');
  const [savingEdit, setSavingEdit] = useState(false);
  const [editError, setEditError] = useState(null);

  // Deletion state
  const [deletingId, setDeletingId] = useState(null);

  const fetchProduct = useCallback(async () => {
    try {
      const prodRes = await api.get(`/products/${id}`);
      setProduct(prodRes.data);
    } catch (err) {
      console.error("Failed to load product details", err);
    }
  }, [id]);

  const fetchReviews = useCallback(async (sort = reviewSort) => {
    setReviewsLoading(true);
    setReviewsError(null);
    try {
      const revRes = await api.get(`/products/${id}/reviews?sort_by=${sort}`);
      setReviews(revRes.data || []);
    } catch (err) {
      console.error("Failed to load reviews", err);
      setReviewsError("Unable to load reviews right now. Please try again.");
    } finally {
      setReviewsLoading(false);
    }
  }, [id, reviewSort]);

  useEffect(() => {
    if (!id) return;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    fetchProduct();

    setLoadingRecommendations(true);
    api.get(`/products/recommendations/${id}`)
      .then(res => setRecommendations(res.data || []))
      .catch(err => {
        console.error("Failed to load recommendations", err);
        setRecommendations([]);
      })
      .finally(() => setLoadingRecommendations(false));

    fetchReviews(reviewSort);
  }, [id, fetchProduct, fetchReviews, reviewSort]);

  if (!product) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <p className="animate-pulse text-amber-700 dark:text-amber-300">Loading warm bakery details...</p>
      </div>
    );
  }

  const inWishlist = isInWishlist(product.id);
  const displayPrice = product.discount_price || product.price;

  // Check if current user already submitted a review
  const userExistingReview = user ? reviews.find(r => r.user_id === user.id) : null;

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    setSubmitError(null);
    setSubmitSuccess(null);

    if (newRating < 1 || newRating > 5) {
      setSubmitError("Please select a valid rating between 1 and 5 stars.");
      return;
    }

    setSubmittingReview(true);
    try {
      await api.post(`/products/${product.id}/reviews`, {
        rating: newRating,
        comment: newComment
      });
      setNewComment('');
      setNewRating(5);
      setSubmitSuccess("Thank you! Your review has been published.");
      await fetchReviews(reviewSort);
      await fetchProduct();
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to submit your review. Please try again.";
      setSubmitError(msg);
    } finally {
      setSubmittingReview(false);
    }
  };

  const startEditReview = (r) => {
    setEditingReviewId(r.id);
    setEditRating(r.rating);
    setEditComment(r.comment || '');
    setEditError(null);
  };

  const cancelEditReview = () => {
    setEditingReviewId(null);
    setEditRating(5);
    setEditComment('');
    setEditError(null);
  };

  const handleSaveEdit = async (reviewId) => {
    setEditError(null);
    setSavingEdit(true);
    try {
      await api.put(`/reviews/${reviewId}`, {
        rating: editRating,
        comment: editComment
      });
      setEditingReviewId(null);
      await fetchReviews(reviewSort);
      await fetchProduct();
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to update review.";
      setEditError(msg);
    } finally {
      setSavingEdit(false);
    }
  };

  const handleDeleteReview = async (reviewId) => {
    if (!window.confirm("Are you sure you want to delete this review?")) return;
    setDeletingId(reviewId);
    try {
      await api.delete(`/reviews/${reviewId}`);
      await fetchReviews(reviewSort);
      await fetchProduct();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to delete review.");
    } finally {
      setDeletingId(null);
    }
  };

  // Rating breakdown calculation
  const totalReviewsCount = reviews.length;
  const starCounts = [5, 4, 3, 2, 1].map(stars => ({
    stars,
    count: reviews.filter(r => r.rating === stars).length,
    percentage: totalReviewsCount > 0 ? (reviews.filter(r => r.rating === stars).length / totalReviewsCount) * 100 : 0
  }));

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
          <div className="aspect-square bg-amber-50 dark:bg-amber-950/20 rounded-3xl overflow-hidden border border-amber-900/10 dark:border-amber-500/20 relative shadow-sm">
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full h-full object-cover"
            />
            {product.is_popular && (
              <span className="absolute top-4 left-4 bg-amber-500 text-white text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow">
                Customer Favorite
              </span>
            )}
            <button
              onClick={() => toggleWishlist(product)}
              className="absolute top-4 right-4 p-2.5 rounded-full bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm border border-white/20 shadow hover:scale-110 transition"
              aria-label="Wishlist"
            >
              <Heart className={`w-4 h-4 ${inWishlist ? 'text-red-500 fill-red-500' : 'text-gray-600 dark:text-gray-300'}`} />
            </button>
          </div>
        </div>

        {/* Product Details Header */}
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
              <button
                onClick={() => setActiveTab('reviews')}
                className="flex items-center gap-1.5 text-amber-500 font-extrabold text-sm hover:underline cursor-pointer"
              >
                <Star className="w-4 h-4 fill-current text-amber-400" />
                <span>{Number(product.rating || 0).toFixed(1)}</span>
                <span className="text-gray-400 text-xs font-normal">
                  ({product.review_count} {product.review_count === 1 ? 'Review' : 'Customer Reviews'})
                </span>
              </button>
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

          {/* Quantity and Add to Cart */}
          <div className="space-y-4 pt-2">
            <div className="flex items-center gap-4">
              <div className="flex items-center border border-amber-900/20 dark:border-amber-500/30 rounded-2xl p-1 bg-white dark:bg-amber-950/20">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="p-2 text-gray-500 hover:text-bakery-orange transition"
                  aria-label="Decrease quantity"
                >
                  <Minus className="w-3.5 h-3.5" />
                </button>
                <span className="w-8 text-center font-bold text-sm">{quantity}</span>
                <button
                  onClick={() => setQuantity(Math.min(product.stock_quantity, quantity + 1))}
                  className="p-2 text-gray-500 hover:text-bakery-orange transition"
                  aria-label="Increase quantity"
                >
                  <Plus className="w-3.5 h-3.5" />
                </button>
              </div>

              <button
                onClick={() => addToCart(product, quantity)}
                disabled={product.stock_quantity === 0}
                className="flex-1 py-3 px-6 bg-bakery-orange hover:bg-bakery-brown text-white font-bold rounded-2xl flex items-center justify-center gap-2 shadow-lg shadow-bakery-orange/20 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ShoppingBag className="w-4 h-4" />
                <span>{product.stock_quantity > 0 ? 'Add to Cart' : 'Out of Stock'}</span>
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 pt-2 text-xs text-gray-500">
              <div className="flex items-center gap-2 p-2.5 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-900/5">
                <Award className="w-4 h-4 text-bakery-orange" />
                <span>100% Artisan Handmade</span>
              </div>
              <div className="flex items-center gap-2 p-2.5 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-900/5">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>Freshness Guaranteed</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs: Description, Ingredients, Nutrition, Reviews */}
      <div className="bg-white dark:bg-bakery-chocolate/60 rounded-3xl p-6 sm:p-8 border border-amber-900/10 dark:border-amber-500/20 shadow-md">
        <div className="flex border-b border-amber-900/10 gap-6 overflow-x-auto">
          {['description', 'ingredients', 'nutrition', 'reviews'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 text-xs font-bold uppercase tracking-wider transition border-b-2 whitespace-nowrap ${
                activeTab === tab
                  ? 'border-bakery-orange text-bakery-orange font-extrabold'
                  : 'border-transparent text-gray-500 hover:text-bakery-dark dark:hover:text-cream-100'
              }`}
            >
              {tab === 'reviews' ? `Reviews (${product.review_count || reviews.length})` : tab}
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
            <div className="space-y-8">
              {/* Rating Summary Card */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 rounded-2xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-900/10">
                <div className="flex flex-col items-center justify-center text-center p-4 border-b md:border-b-0 md:border-r border-amber-900/10">
                  <div className="font-serif text-5xl font-extrabold text-bakery-dark dark:text-cream-100">
                    {Number(product.rating || 0).toFixed(1)}
                  </div>
                  <div className="my-2">
                    <StarPicker rating={Math.round(product.rating || 5)} editable={false} size="w-4 h-4" />
                  </div>
                  <p className="text-xs text-gray-500">
                    Based on {product.review_count} {product.review_count === 1 ? 'review' : 'reviews'}
                  </p>
                </div>

                <div className="md:col-span-2 flex flex-col justify-center space-y-1.5 px-2">
                  {starCounts.map(({ stars, count, percentage }) => (
                    <div key={stars} className="flex items-center gap-2 text-xs">
                      <span className="w-12 text-gray-600 dark:text-gray-300 font-medium">{stars} stars</span>
                      <div className="flex-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
                        <div
                          className="h-full bg-amber-400 rounded-full transition-all duration-500"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <span className="w-8 text-right text-gray-400 text-[11px]">{count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Review Submission Section */}
              <div className="bg-white dark:bg-bakery-chocolate/40 p-6 rounded-2xl border border-amber-900/10 space-y-4">
                {user ? (
                  userExistingReview && editingReviewId !== userExistingReview.id ? (
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800">
                      <div>
                        <h4 className="font-bold text-sm text-bakery-dark dark:text-cream-100">You reviewed this product</h4>
                        <p className="text-xs text-gray-500">You rated it {userExistingReview.rating} stars. You can update or remove your review anytime.</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => startEditReview(userExistingReview)}
                          className="px-3 py-1.5 bg-amber-100 hover:bg-amber-200 text-amber-800 text-xs font-bold rounded-lg transition flex items-center gap-1.5"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                          <span>Edit Review</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDeleteReview(userExistingReview.id)}
                          disabled={deletingId === userExistingReview.id}
                          className="px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-600 text-xs font-bold rounded-lg transition flex items-center gap-1.5"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                          <span>Delete</span>
                        </button>
                      </div>
                    </div>
                  ) : (
                    <form onSubmit={handleReviewSubmit} className="space-y-4">
                      <div className="flex items-center justify-between">
                        <h4 className="font-bold text-sm uppercase tracking-wider text-bakery-dark dark:text-cream-100">
                          Leave a Customer Review
                        </h4>
                        <span className="text-xs text-gray-400">Signed in as {user.full_name}</span>
                      </div>

                      {submitError && (
                        <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
                          <AlertCircle className="w-4 h-4 flex-shrink-0" />
                          <span>{submitError}</span>
                        </div>
                      )}

                      {submitSuccess && (
                        <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center gap-2">
                          <CheckCircle className="w-4 h-4 flex-shrink-0" />
                          <span>{submitSuccess}</span>
                        </div>
                      )}

                      <div className="flex items-center gap-3">
                        <label className="text-xs font-bold text-gray-700 dark:text-gray-300">Your Rating:</label>
                        <StarPicker rating={newRating} setRating={setNewRating} size="w-6 h-6" />
                        <span className="text-xs text-amber-600 font-semibold">
                          {newRating === 5 && 'Excellent'}
                          {newRating === 4 && 'Very Good'}
                          {newRating === 3 && 'Average'}
                          {newRating === 2 && 'Poor'}
                          {newRating === 1 && 'Terrible'}
                        </span>
                      </div>

                      <div className="space-y-1">
                        <textarea
                          rows={3}
                          maxLength={2000}
                          placeholder="Share your taste experience, texture, aroma, or pairings..."
                          value={newComment}
                          onChange={(e) => setNewComment(e.target.value)}
                          className="w-full p-3.5 text-xs rounded-xl border border-amber-900/20 bg-white dark:bg-amber-950/30 focus:ring-2 focus:ring-bakery-orange focus:outline-none"
                        />
                        <div className="text-right text-[10px] text-gray-400">
                          {newComment.length}/2000 characters
                        </div>
                      </div>

                      <button
                        type="submit"
                        disabled={submittingReview}
                        className="px-5 py-2.5 bg-bakery-orange hover:bg-bakery-brown text-white text-xs font-bold rounded-xl transition shadow-md disabled:opacity-50 flex items-center gap-2"
                      >
                        {submittingReview ? (
                          <>
                            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                            <span>Publishing...</span>
                          </>
                        ) : (
                          <span>Submit Review</span>
                        )}
                      </button>
                    </form>
                  )
                ) : (
                  <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-900/10 text-center space-y-2">
                    <p className="text-xs text-gray-600 dark:text-amber-100/80">
                      Want to review this product? Please sign in to share your taste experience.
                    </p>
                    <Link
                      to="/login"
                      className="inline-block px-4 py-2 bg-bakery-orange hover:bg-bakery-brown text-white text-xs font-bold rounded-xl transition"
                    >
                      Sign In to Review
                    </Link>
                  </div>
                )}
              </div>

              {/* Review Controls Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-amber-900/10 pb-3">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-bakery-orange" />
                  <h3 className="font-bold text-sm">Customer Feedback</h3>
                  <span className="text-xs text-gray-400">({reviews.length})</span>
                </div>

                <div className="flex items-center gap-2">
                  <label className="text-xs text-gray-500">Sort by:</label>
                  <select
                    value={reviewSort}
                    onChange={(e) => setReviewSort(e.target.value)}
                    className="px-3 py-1.5 text-xs rounded-xl border border-amber-900/20 bg-white dark:bg-amber-950/50 focus:outline-none"
                  >
                    <option value="newest">Newest First</option>
                    <option value="oldest">Oldest First</option>
                    <option value="highest_rating">Highest Rated</option>
                    <option value="lowest_rating">Lowest Rated</option>
                  </select>
                </div>
              </div>

              {/* Review List & States */}
              {reviewsLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((n) => (
                    <div key={n} className="p-5 rounded-2xl border border-amber-900/10 bg-amber-50/20 animate-pulse space-y-3">
                      <div className="flex justify-between">
                        <div className="w-28 h-4 bg-gray-200 dark:bg-gray-700 rounded" />
                        <div className="w-20 h-4 bg-gray-200 dark:bg-gray-700 rounded" />
                      </div>
                      <div className="w-full h-10 bg-gray-200 dark:bg-gray-700 rounded" />
                    </div>
                  ))}
                </div>
              ) : reviewsError ? (
                <div className="p-6 text-center space-y-3 rounded-2xl bg-red-50/50 border border-red-200">
                  <p className="text-xs text-red-600">{reviewsError}</p>
                  <button
                    onClick={() => fetchReviews(reviewSort)}
                    className="px-4 py-2 bg-bakery-orange text-white text-xs font-bold rounded-xl hover:bg-bakery-brown transition"
                  >
                    Try Again
                  </button>
                </div>
              ) : reviews.length === 0 ? (
                <div className="p-8 text-center space-y-2 rounded-2xl bg-amber-50/30 border border-dashed border-amber-900/20">
                  <p className="text-sm font-semibold text-gray-600 dark:text-gray-300">No customer reviews yet.</p>
                  <p className="text-xs text-gray-400">Be the first to review this freshly baked treat!</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {reviews.map((r) => {
                    const isAuthor = user && user.id === r.user_id;
                    const isAdmin = user && user.role === 'admin';
                    const canModify = isAuthor || isAdmin;
                    const isEditing = editingReviewId === r.id;

                    return (
                      <div
                        key={r.id}
                        className="p-5 rounded-2xl border border-amber-900/10 bg-white dark:bg-bakery-chocolate/30 space-y-3 shadow-sm transition hover:border-amber-900/20"
                      >
                        {isEditing ? (
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-xs uppercase text-bakery-orange">Editing Review</span>
                              <StarPicker rating={editRating} setRating={setEditRating} size="w-5 h-5" />
                            </div>

                            {editError && (
                              <p className="text-xs text-red-600">{editError}</p>
                            )}

                            <textarea
                              rows={3}
                              maxLength={2000}
                              value={editComment}
                              onChange={(e) => setEditComment(e.target.value)}
                              className="w-full p-3 text-xs rounded-xl border border-amber-900/20 bg-white dark:bg-amber-950/40 focus:ring-2 focus:ring-bakery-orange focus:outline-none"
                            />

                            <div className="flex items-center gap-2">
                              <button
                                type="button"
                                onClick={() => handleSaveEdit(r.id)}
                                disabled={savingEdit}
                                className="px-3 py-1.5 bg-bakery-orange text-white text-xs font-bold rounded-lg hover:bg-bakery-brown transition disabled:opacity-50"
                              >
                                {savingEdit ? 'Saving...' : 'Save Changes'}
                              </button>
                              <button
                                type="button"
                                onClick={cancelEditReview}
                                className="px-3 py-1.5 bg-gray-200 dark:bg-gray-700 text-xs font-bold rounded-lg transition"
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <div className="flex flex-wrap items-center justify-between gap-2">
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-xs text-bakery-dark dark:text-cream-100">
                                  {r.user?.full_name || 'Anonymous Customer'}
                                </span>
                                {r.is_verified_purchase && (
                                  <span className="inline-flex items-center gap-1 text-[10px] text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800 px-2 py-0.5 rounded-full font-semibold">
                                    <ShieldCheck className="w-3 h-3 text-emerald-600" />
                                    <span>Verified Purchase</span>
                                  </span>
                                )}
                              </div>

                              <div className="flex items-center gap-3">
                                <StarPicker rating={r.rating} editable={false} size="w-3.5 h-3.5" />
                                <span className="text-[11px] text-gray-400">
                                  {new Date(r.created_at).toLocaleDateString(undefined, {
                                    year: 'numeric',
                                    month: 'short',
                                    day: 'numeric'
                                  })}
                                </span>
                              </div>
                            </div>

                            {r.comment && (
                              <p className="text-xs text-gray-600 dark:text-amber-100/80 leading-relaxed">
                                {r.comment}
                              </p>
                            )}

                            {canModify && (
                              <div className="flex items-center gap-3 pt-2 border-t border-amber-900/5 text-xs text-gray-400">
                                {isAuthor && (
                                  <button
                                    onClick={() => startEditReview(r)}
                                    className="hover:text-bakery-orange transition flex items-center gap-1"
                                  >
                                    <Edit3 className="w-3 h-3" />
                                    <span>Edit</span>
                                  </button>
                                )}
                                <button
                                  onClick={() => handleDeleteReview(r.id)}
                                  disabled={deletingId === r.id}
                                  className="hover:text-red-500 transition flex items-center gap-1"
                                >
                                  <Trash2 className="w-3 h-3" />
                                  <span>{deletingId === r.id ? 'Deleting...' : 'Delete'}</span>
                                </button>
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* AI Frequently Bought Together Recommendations */}
      <section className="space-y-6 pt-6 border-t border-amber-900/10">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-bakery-orange" />
          <h2 className="font-serif text-2xl font-bold">Frequently Bought Together</h2>
        </div>

        {loadingRecommendations ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((n) => (
              <div key={n} className="h-72 rounded-3xl bg-amber-50/50 dark:bg-amber-950/20 animate-pulse border border-amber-900/5" />
            ))}
          </div>
        ) : recommendations.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {recommendations.map((rec) => (
              <ProductCard key={rec.id} product={rec} />
            ))}
          </div>
        ) : (
          <p className="text-xs text-gray-400 italic">No recommendations available at this time.</p>
        )}
      </section>
    </div>
  );
};

export default ProductDetailPage;
