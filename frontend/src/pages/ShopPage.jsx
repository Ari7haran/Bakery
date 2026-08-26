import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Filter, SlidersHorizontal, ArrowUpDown } from 'lucide-react';
import { api } from '../services/api.js';
import ProductCard from '../components/ProductCard.jsx';

const ShopPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters state
  const selectedCategory = searchParams.get('category') || 'all';
  const searchQuery = searchParams.get('search') || '';
  const [isVegOnly, setIsVegOnly] = useState(false);
  const [maxPrice, setMaxPrice] = useState(1500);
  const [sortBy, setSortBy] = useState('popular');
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);

  useEffect(() => {
    const fetchShopData = async () => {
      setLoading(true);
      try {
        const [catRes, prodRes] = await Promise.all([
          api.get('/categories'),
          api.get(`/products?category_slug=${selectedCategory}&search=${encodeURIComponent(searchQuery)}&sort_by=${sortBy}`)
        ]);
        setCategories(catRes.data);
        setProducts(prodRes.data);
      } catch (err) {
        console.error("Failed to load shop products", err);
      } finally {
        setLoading(false);
      }
    };
    fetchShopData();
  }, [selectedCategory, searchQuery, sortBy]);

  const handleCategoryChange = (slug) => {
    const params = new URLSearchParams(searchParams);
    if (slug === 'all') {
      params.delete('category');
    } else {
      params.set('category', slug);
    }
    setSearchParams(params);
  };

  // Local filtering for quick responsive UI
  const filteredProducts = products.filter((p) => {
    if (isVegOnly && !p.is_veg) return false;
    const price = p.discount_price || p.price;
    if (price > maxPrice) return false;
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-amber-900/10 pb-6">
        <div>
          <h1 className="font-serif text-3xl font-bold">Artisanal Bakery Catalog</h1>
          <p className="text-xs text-gray-500 dark:text-amber-200/60 mt-1">
            Order fresh sourdoughs, pastries, celebration cakes & beverages for express takeaway pickup
          </p>
        </div>

        {/* Search & Sort Bar */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsMobileFilterOpen(true)}
            className="md:hidden flex items-center gap-2 px-4 py-2 bg-white dark:bg-bakery-chocolate border rounded-2xl text-xs font-bold shadow-sm"
          >
            <Filter className="w-4 h-4 text-bakery-orange" /> Filters
          </button>

          <div className="relative flex-1 md:w-64">
            <input
              type="text"
              placeholder="Filter products..."
              value={searchQuery}
              onChange={(e) => {
                const params = new URLSearchParams(searchParams);
                if (e.target.value) params.set('search', e.target.value);
                else params.delete('search');
                setSearchParams(params);
              }}
              className="w-full pl-8 pr-3 py-2 text-xs rounded-2xl border border-amber-900/20 dark:border-amber-500/20 bg-white dark:bg-amber-950/40"
            />
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
          </div>

          <div className="flex items-center gap-2">
            <ArrowUpDown className="w-4 h-4 text-bakery-orange hidden sm:inline" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 text-xs rounded-2xl border border-amber-900/20 dark:border-amber-500/20 bg-white dark:bg-amber-950/40 font-semibold focus:outline-none"
            >
              <option value="popular">Most Popular</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="rating">Highest Rated</option>
              <option value="newest">Newest Fresh Items</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Grid: Sidebar + Product Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        
        {/* Sidebar Filters */}
        <aside className="hidden md:block space-y-6 bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-sm h-fit">
          <div className="flex items-center justify-between border-b border-amber-900/10 pb-3">
            <h3 className="font-serif font-bold text-sm uppercase tracking-wider flex items-center gap-2">
              <SlidersHorizontal className="w-4 h-4 text-bakery-orange" /> Filters
            </h3>
          </div>

          {/* Veg Only Toggle */}
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold flex items-center gap-2">
              <span className="w-3 h-3 border border-green-600 rounded-xs flex items-center justify-center p-0.5">
                <span className="w-1.5 h-1.5 bg-green-600 rounded-full"></span>
              </span>
              100% Eggless / Pure Veg
            </span>
            <input
              type="checkbox"
              checked={isVegOnly}
              onChange={(e) => setIsVegOnly(e.target.checked)}
              className="w-4 h-4 accent-bakery-orange cursor-pointer"
            />
          </div>

          {/* Category List */}
          <div className="space-y-2">
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-500">Categories</label>
            <div className="space-y-1 max-h-64 overflow-y-auto pr-1">
              <button
                onClick={() => handleCategoryChange('all')}
                className={`w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition ${
                  selectedCategory === 'all'
                    ? 'bg-bakery-orange text-white font-bold shadow'
                    : 'hover:bg-amber-100/50 dark:hover:bg-amber-900/40 text-gray-700 dark:text-gray-200'
                }`}
              >
                All Bakery Categories
              </button>
              {categories.map((c) => (
                <button
                  key={c.id}
                  onClick={() => handleCategoryChange(c.slug)}
                  className={`w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition ${
                    selectedCategory === c.slug
                      ? 'bg-bakery-orange text-white font-bold shadow'
                      : 'hover:bg-amber-100/50 dark:hover:bg-amber-900/40 text-gray-700 dark:text-gray-200'
                  }`}
                >
                  {c.name}
                </button>
              ))}
            </div>
          </div>

          {/* Price Range */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-bold">
              <label>Max Price</label>
              <span className="text-bakery-orange">₹{maxPrice}</span>
            </div>
            <input
              type="range"
              min="50"
              max="2000"
              step="50"
              value={maxPrice}
              onChange={(e) => setMaxPrice(Number(e.target.value))}
              className="w-full accent-bakery-orange"
            />
          </div>
        </aside>

        {/* Product Cards Grid */}
        <div className="md:col-span-3">
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-white dark:bg-bakery-chocolate h-80 rounded-3xl animate-pulse p-4 space-y-4">
                  <div className="w-full h-40 bg-gray-200 dark:bg-amber-950/60 rounded-2xl" />
                  <div className="h-4 bg-gray-200 dark:bg-amber-950/60 rounded w-3/4" />
                  <div className="h-4 bg-gray-200 dark:bg-amber-950/60 rounded w-1/2" />
                </div>
              ))}
            </div>
          ) : filteredProducts.length === 0 ? (
            <div className="text-center py-16 bg-white dark:bg-bakery-chocolate/40 rounded-3xl border border-amber-900/10 p-8">
              <p className="font-serif text-2xl font-bold">No Bakery Delights Found</p>
              <p className="text-xs text-gray-500 mt-2">Try clearing search terms or selecting a different category.</p>
              <button
                onClick={() => {
                  setSearchParams(new URLSearchParams());
                  setIsVegOnly(false);
                  setMaxPrice(2000);
                }}
                className="mt-4 px-6 py-2.5 bg-bakery-orange text-white font-bold text-xs rounded-full shadow"
              >
                Reset All Filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProducts.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ShopPage;
