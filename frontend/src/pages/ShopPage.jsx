import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Filter, SlidersHorizontal, ArrowUpDown, X, Check, RefreshCw } from 'lucide-react';
import { api } from '../services/api.js';
import ProductCard from '../components/ProductCard.jsx';

const ShopPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // URL-driven state
  const selectedCategory = searchParams.get('category') || 'all';
  const searchQuery = searchParams.get('search') || '';
  const [localSearch, setLocalSearch] = useState(searchQuery);

  // Filter state
  const [isVegOnly, setIsVegOnly] = useState(false);
  const [inStockOnly, setInStockOnly] = useState(false);
  const [maxPrice, setMaxPrice] = useState(2000);
  const [sortBy, setSortBy] = useState('popular');
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);

  // Keep local search input synced when URL search param changes
  useEffect(() => {
    setLocalSearch(searchQuery);
  }, [searchQuery]);

  // Debounced search update to URL (350ms)
  const debounceTimerRef = useRef(null);
  const handleSearchChange = (val) => {
    setLocalSearch(val);
    if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
    debounceTimerRef.current = setTimeout(() => {
      const params = new URLSearchParams(searchParams);
      if (val.trim()) {
        params.set('search', val.trim());
      } else {
        params.delete('search');
      }
      setSearchParams(params);
    }, 350);
  };

  const handleClearSearch = () => {
    setLocalSearch('');
    if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
    const params = new URLSearchParams(searchParams);
    params.delete('search');
    setSearchParams(params);
  };

  const fetchShopData = async () => {
    setLoading(true);
    setError(null);
    try {
      const queryParams = new URLSearchParams();
      if (selectedCategory && selectedCategory !== 'all') {
        queryParams.set('category_slug', selectedCategory);
      }
      if (searchQuery.trim()) {
        queryParams.set('search', searchQuery.trim());
      }
      if (sortBy) {
        queryParams.set('sort_by', sortBy);
      }
      if (inStockOnly) {
        queryParams.set('in_stock', 'true');
      }
      if (isVegOnly) {
        queryParams.set('is_veg', 'true');
      }
      if (maxPrice < 2000) {
        queryParams.set('max_price', maxPrice);
      }

      const [catRes, prodRes] = await Promise.all([
        api.get('/categories'),
        api.get(`/products?${queryParams.toString()}`)
      ]);
      setCategories(catRes.data);
      setProducts(prodRes.data);
    } catch (err) {
      console.error("Failed to load shop products", err);
      setError("Unable to load products. Please check your connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShopData();
  }, [selectedCategory, searchQuery, sortBy, inStockOnly, isVegOnly, maxPrice]);

  const handleCategoryChange = (slug) => {
    const params = new URLSearchParams(searchParams);
    if (slug === 'all') {
      params.delete('category');
    } else {
      params.set('category', slug);
    }
    setSearchParams(params);
    setIsMobileFilterOpen(false);
  };

  const handleResetFilters = () => {
    setSearchParams(new URLSearchParams());
    setLocalSearch('');
    setIsVegOnly(false);
    setInStockOnly(false);
    setMaxPrice(2000);
    setSortBy('popular');
    setIsMobileFilterOpen(false);
  };

  const activeCategoryName = categories.find(c => c.slug === selectedCategory)?.name;
  const hasActiveFilters = selectedCategory !== 'all' || searchQuery.trim() !== '' || isVegOnly || inStockOnly || maxPrice < 2000;

  // Filter content component reused between desktop sidebar and mobile drawer
  const FilterContent = () => (
    <div className="space-y-6">
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

      {/* In Stock Only Toggle (Step #8 Inventory Integration) */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          In Stock Only
        </span>
        <input
          type="checkbox"
          checked={inStockOnly}
          onChange={(e) => setInStockOnly(e.target.checked)}
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
        <div className="flex justify-between text-[10px] text-gray-400">
          <span>₹50</span>
          <span>₹2000</span>
        </div>
      </div>

      {/* Clear Filters Button */}
      {hasActiveFilters && (
        <button
          onClick={handleResetFilters}
          className="w-full py-2 px-3 border border-amber-900/20 text-xs font-semibold rounded-xl hover:bg-amber-100/50 dark:hover:bg-amber-950/40 text-gray-600 dark:text-amber-200 transition"
        >
          Reset All Filters
        </button>
      )}
    </div>
  );

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
            {hasActiveFilters && (
              <span className="w-2 h-2 rounded-full bg-bakery-orange"></span>
            )}
          </button>

          <div className="relative flex-1 md:w-64">
            <input
              type="text"
              placeholder="Search products..."
              value={localSearch}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="w-full pl-8 pr-8 py-2 text-xs rounded-2xl border border-amber-900/20 dark:border-amber-500/20 bg-white dark:bg-amber-950/40 focus:outline-none focus:border-bakery-orange"
            />
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
            {localSearch && (
              <button
                onClick={handleClearSearch}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
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
              <option value="name_asc">Name: A to Z</option>
              <option value="name_desc">Name: Z to A</option>
              <option value="rating">Highest Rated</option>
              <option value="newest">Newest Fresh Items</option>
            </select>
          </div>
        </div>
      </div>

      {/* Active Filter Chips */}
      {hasActiveFilters && (
        <div className="flex flex-wrap items-center gap-2 pt-1 pb-2">
          <span className="text-xs text-gray-500 font-medium mr-1">Active Filters:</span>
          {selectedCategory !== 'all' && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-100 dark:bg-amber-900/40 text-amber-900 dark:text-amber-200 text-xs rounded-full font-medium">
              Category: {activeCategoryName || selectedCategory}
              <button onClick={() => handleCategoryChange('all')} className="hover:opacity-75">
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          {searchQuery && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-100 dark:bg-amber-900/40 text-amber-900 dark:text-amber-200 text-xs rounded-full font-medium">
              Search: "{searchQuery}"
              <button onClick={handleClearSearch} className="hover:opacity-75">
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          {isVegOnly && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-100 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 text-xs rounded-full font-medium">
              100% Veg
              <button onClick={() => setIsVegOnly(false)} className="hover:opacity-75">
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          {inStockOnly && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-blue-100 dark:bg-blue-950/40 text-blue-800 dark:text-blue-300 text-xs rounded-full font-medium">
              In Stock
              <button onClick={() => setInStockOnly(false)} className="hover:opacity-75">
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          {maxPrice < 2000 && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-100 dark:bg-amber-900/40 text-amber-900 dark:text-amber-200 text-xs rounded-full font-medium">
              ≤ ₹{maxPrice}
              <button onClick={() => setMaxPrice(2000)} className="hover:opacity-75">
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          <button
            onClick={handleResetFilters}
            className="text-xs text-bakery-orange hover:underline font-semibold ml-2"
          >
            Clear all
          </button>
        </div>
      )}

      {/* Main Grid: Sidebar + Product Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        
        {/* Desktop Sidebar Filters */}
        <aside className="hidden md:block space-y-6 bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-sm h-fit">
          <div className="flex items-center justify-between border-b border-amber-900/10 pb-3">
            <h3 className="font-serif font-bold text-sm uppercase tracking-wider flex items-center gap-2">
              <SlidersHorizontal className="w-4 h-4 text-bakery-orange" /> Filters
            </h3>
          </div>
          <FilterContent />
        </aside>

        {/* Mobile Filter Drawer Modal */}
        {isMobileFilterOpen && (
          <div className="fixed inset-0 z-50 md:hidden flex justify-end bg-black/50 backdrop-blur-xs">
            <div className="w-4/5 max-w-sm h-full bg-white dark:bg-bakery-chocolate p-6 overflow-y-auto shadow-2xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between border-b border-amber-900/10 pb-4 mb-6">
                  <h3 className="font-serif font-bold text-base flex items-center gap-2">
                    <SlidersHorizontal className="w-4 h-4 text-bakery-orange" /> Filter Catalog
                  </h3>
                  <button
                    onClick={() => setIsMobileFilterOpen(false)}
                    className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-amber-950/60"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <FilterContent />
              </div>
              <button
                onClick={() => setIsMobileFilterOpen(false)}
                className="mt-8 w-full py-3 bg-bakery-orange text-white font-bold text-xs rounded-2xl shadow"
              >
                Apply & View Products ({products.length})
              </button>
            </div>
          </div>
        )}

        {/* Product Cards Grid */}
        <div className="md:col-span-3">
          {error ? (
            <div className="text-center py-16 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/40 rounded-3xl p-8">
              <p className="text-red-700 dark:text-red-300 font-semibold text-sm">{error}</p>
              <button
                onClick={fetchShopData}
                className="mt-4 inline-flex items-center gap-2 px-5 py-2.5 bg-bakery-orange text-white text-xs font-bold rounded-full shadow hover:opacity-90 transition"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Retry
              </button>
            </div>
          ) : loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-white dark:bg-bakery-chocolate h-80 rounded-3xl animate-pulse p-4 space-y-4">
                  <div className="w-full h-40 bg-gray-200 dark:bg-amber-950/60 rounded-2xl" />
                  <div className="h-4 bg-gray-200 dark:bg-amber-950/60 rounded w-3/4" />
                  <div className="h-4 bg-gray-200 dark:bg-amber-950/60 rounded w-1/2" />
                </div>
              ))}
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-16 bg-white dark:bg-bakery-chocolate/40 rounded-3xl border border-amber-900/10 p-8">
              <p className="font-serif text-2xl font-bold">No Bakery Delights Found</p>
              <p className="text-xs text-gray-500 mt-2">
                Try adjusting your search query, price range, or category filter.
              </p>
              <button
                onClick={handleResetFilters}
                className="mt-4 px-6 py-2.5 bg-bakery-orange text-white font-bold text-xs rounded-full shadow hover:opacity-90 transition"
              >
                Reset All Filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.map((p) => (
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

