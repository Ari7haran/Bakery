import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  ShoppingBag,
  Heart,
  Search,
  User,
  Sun,
  Moon,
  Clock,
  ChevronDown,
  Menu as MenuIcon,
  X,
  LogOut,
  Sparkles,
  LayoutDashboard,
  Bell
} from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';
import { useCart } from '../context/CartContext.jsx';
import { useTheme } from '../context/ThemeContext.jsx';
import PickupModal from './PickupModal.jsx';
import NotificationDropdown from './NotificationDropdown.jsx';
import { notificationService } from '../services/notificationService.js';

const Navbar = () => {
  const { user, logout } = useAuth();
  const { cartCount, wishlist, setIsCartOpen, pickupSlot } = useCart();
  const { isDarkMode, toggleTheme } = useTheme();
  const [searchQuery, setSearchQuery] = useState('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isPickupModalOpen, setIsPickupModalOpen] = useState(false);
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!user) {
      setUnreadCount(0);
      return;
    }

    const fetchUnread = async () => {
      try {
        const data = await notificationService.getUnreadCount();
        setUnreadCount(data.unread_count || 0);
      } catch (err) {
        // Silent fail for polling
      }
    };

    fetchUnread();
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, [user]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/shop?search=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <>
      <header className="sticky top-0 z-40 w-full glass-card border-b border-amber-900/10 dark:border-amber-500/10 transition-colors">
        {/* Top Info Bar */}
        <div className="bg-bakery-dark text-cream-100 text-xs py-1.5 px-4 flex flex-wrap justify-between items-center text-amber-200">
          <div className="flex items-center gap-2">
            <span className="bg-bakery-orange/80 text-white text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">
              Hot Takeaway
            </span>
            <span>🥐 Order Online for Express Counter Pickup within 15 mins!</span>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <button
              onClick={() => setIsPickupModalOpen(true)}
              className="flex items-center gap-1.5 hover:text-white transition font-medium bg-bakery-brown/50 px-2.5 py-0.5 rounded"
            >
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span>Pickup: {pickupSlot ? `${pickupSlot.date} (${pickupSlot.time})` : 'Select Slot'}</span>
              <ChevronDown className="w-3 h-3" />
            </button>
            <span className="hidden md:inline text-amber-400/60">|</span>
            <span className="hidden md:inline">📞 +1 (800) 555-BAKE</span>
          </div>
        </div>

        {/* Main Navigation Bar */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex items-center justify-between gap-4">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-bakery-brown to-bakery-orange flex items-center justify-center text-white shadow-md shadow-amber-900/20 group-hover:scale-105 transition transform">
              <span className="text-xl">🥐</span>
            </div>
            <div>
              <span className="font-serif text-2xl font-bold tracking-tight text-bakery-dark dark:text-cream-100">
                Sweet<span className="text-bakery-orange">Crumbs</span>
              </span>
              <p className="text-[10px] tracking-widest text-bakery-brown/70 dark:text-amber-300/70 font-semibold uppercase -mt-1">
                Artisanal Bakery & Cafe
              </p>
            </div>
          </Link>

          {/* Desktop Search Bar */}
          <form onSubmit={handleSearch} className="hidden lg:flex flex-1 max-w-md relative mx-4">
            <input
              type="text"
              placeholder="Search sourdough, fresh cupcakes, croissants..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-4 pr-10 py-2 rounded-full border border-amber-900/20 dark:border-amber-500/20 bg-cream-100/80 dark:bg-amber-950/30 text-sm focus:outline-none focus:ring-2 focus:ring-bakery-orange dark:text-cream-100 placeholder-amber-900/40 dark:placeholder-amber-200/40 transition"
            />
            <button
              type="submit"
              className="absolute right-1 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-bakery-orange text-white flex items-center justify-center hover:bg-bakery-brown transition shadow-sm"
            >
              <Search className="w-4 h-4" />
            </button>
          </form>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-6 font-medium text-sm">
            <Link
              to="/"
              className={`hover:text-bakery-orange transition ${location.pathname === '/' ? 'text-bakery-orange font-bold' : ''}`}
            >
              Home
            </Link>
            <Link
              to="/shop"
              className={`hover:text-bakery-orange transition ${location.pathname === '/shop' ? 'text-bakery-orange font-bold' : ''}`}
            >
              Menu & Shop
            </Link>
            <Link
              to="/shop?category=combo-meals"
              className="hover:text-bakery-orange transition flex items-center gap-1 text-bakery-brown dark:text-amber-300 font-semibold"
            >
              <Sparkles className="w-3.5 h-3.5 text-bakery-orange animate-bounce" />
              Combos
            </Link>
            <Link
              to="/track"
              className={`hover:text-bakery-orange transition ${location.pathname === '/track' ? 'text-bakery-orange font-bold' : ''}`}
            >
              Track Order
            </Link>
          </nav>

          {/* Action Icons */}
          <div className="flex items-center gap-3">
            {/* Theme Switcher */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-full hover:bg-amber-950/10 dark:hover:bg-cream-100/10 text-bakery-dark dark:text-cream-100 transition"
              title="Toggle Dark/Light Mode"
            >
              {isDarkMode ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-bakery-brown" />}
            </button>

            {/* Wishlist */}
            <Link
              to="/profile?tab=wishlist"
              className="relative p-2 rounded-full hover:bg-amber-950/10 dark:hover:bg-cream-100/10 text-bakery-dark dark:text-cream-100 transition"
              title="Wishlist"
            >
              <Heart className="w-5 h-5" />
              {wishlist.length > 0 && (
                <span className="absolute top-0 right-0 w-4 h-4 bg-red-500 text-white rounded-full text-[10px] font-bold flex items-center justify-center">
                  {wishlist.length}
                </span>
              )}
            </Link>

            {/* Notifications Bell & Dropdown */}
            {user && (
              <div className="relative">
                <button
                  onClick={() => {
                    setIsNotificationOpen(!isNotificationOpen);
                    setIsUserMenuOpen(false);
                  }}
                  className={`relative p-2 rounded-full transition ${
                    isNotificationOpen
                      ? 'bg-amber-100 dark:bg-amber-900/60 text-bakery-orange'
                      : 'hover:bg-amber-950/10 dark:hover:bg-cream-100/10 text-bakery-dark dark:text-cream-100'
                  }`}
                  title="Notifications"
                  aria-label="View Notifications"
                >
                  <Bell className="w-5 h-5" />
                  {unreadCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 min-w-4 h-4 px-1 bg-bakery-orange text-white rounded-full text-[10px] font-extrabold flex items-center justify-center shadow-sm animate-pulse">
                      {unreadCount > 99 ? '99+' : unreadCount}
                    </span>
                  )}
                </button>

                <NotificationDropdown
                  isOpen={isNotificationOpen}
                  onClose={() => setIsNotificationOpen(false)}
                  user={user}
                  onUnreadCountChange={(newCount) => setUnreadCount(newCount)}
                />
              </div>
            )}

            {/* Cart Drawer Trigger */}
            <button
              onClick={() => setIsCartOpen(true)}
              className="relative p-2.5 rounded-full bg-gradient-to-r from-bakery-brown to-bakery-orange text-white hover:opacity-95 transition shadow-md flex items-center justify-center"
              title="Shopping Cart"
            >
              <ShoppingBag className="w-5 h-5" />
              {cartCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-amber-400 text-bakery-dark font-extrabold rounded-full text-xs flex items-center justify-center shadow">
                  {cartCount}
                </span>
              )}
            </button>

            {/* User Account / Profile */}
            <div className="relative">
              {user ? (
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center gap-2 pl-2 py-1 pr-1.5 rounded-full border border-amber-900/20 dark:border-amber-500/20 hover:bg-amber-100/50 dark:hover:bg-amber-950/50 transition"
                >
                  <div className="w-7 h-7 rounded-full bg-bakery-orange text-white flex items-center justify-center font-bold text-xs">
                    {user.full_name.charAt(0)}
                  </div>
                  <span className="text-xs font-semibold hidden sm:inline">{user.full_name.split(' ')[0]}</span>
                  <ChevronDown className="w-3.5 h-3.5" />
                </button>
              ) : (
                <Link
                  to="/login"
                  className="hidden sm:flex items-center gap-1.5 bg-bakery-dark dark:bg-amber-900 text-white text-xs font-semibold px-4 py-2 rounded-full hover:bg-bakery-orange transition shadow-sm"
                >
                  <User className="w-3.5 h-3.5" />
                  Sign In
                </Link>
              )}

              {/* User Dropdown */}
              {isUserMenuOpen && user && (
                <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-bakery-chocolate rounded-2xl shadow-xl border border-amber-900/10 dark:border-amber-500/20 py-2 z-50 animate-in fade-in slide-in-from-top-2">
                  <div className="px-4 py-2 border-b border-amber-900/10 dark:border-amber-500/10">
                    <p className="text-xs font-bold truncate">{user.full_name}</p>
                    <p className="text-[10px] text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
                    <p className="text-[10px] text-amber-600 dark:text-amber-300 mt-1 font-semibold">
                      ⭐ {user.loyalty_points} Loyalty Points
                    </p>
                  </div>

                  <Link
                    to="/profile"
                    onClick={() => setIsUserMenuOpen(false)}
                    className="flex items-center gap-2 px-4 py-2 text-xs hover:bg-cream-100 dark:hover:bg-amber-900/50 transition"
                  >
                    <User className="w-4 h-4 text-bakery-orange" />
                    My Profile & Orders
                  </Link>

                  {user.role === 'admin' && (
                    <Link
                      to="/admin"
                      onClick={() => setIsUserMenuOpen(false)}
                      className="flex items-center gap-2 px-4 py-2 text-xs text-amber-600 dark:text-amber-300 font-bold hover:bg-cream-100 dark:hover:bg-amber-900/50 transition"
                    >
                      <LayoutDashboard className="w-4 h-4" />
                      Admin Dashboard
                    </Link>
                  )}

                  <button
                    onClick={() => {
                      logout();
                      setIsUserMenuOpen(false);
                    }}
                    className="w-full flex items-center gap-2 px-4 py-2 text-xs text-red-600 dark:text-red-400 hover:bg-cream-100 dark:hover:bg-amber-900/50 transition text-left"
                  >
                    <LogOut className="w-4 h-4" />
                    Sign Out
                  </button>
                </div>
              )}
            </div>

            {/* Mobile Hamburger Toggle */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 text-bakery-dark dark:text-cream-100"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <MenuIcon className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu Dropdown */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-amber-900/10 px-4 py-4 space-y-3 bg-cream-50 dark:bg-bakery-dark">
            <form onSubmit={handleSearch} className="relative mb-3">
              <input
                type="text"
                placeholder="Search bakery items..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-4 pr-10 py-2 rounded-full border text-xs"
              />
            </form>

            <Link
              to="/"
              onClick={() => setIsMobileMenuOpen(false)}
              className="block font-medium hover:text-bakery-orange"
            >
              Home
            </Link>
            <Link
              to="/shop"
              onClick={() => setIsMobileMenuOpen(false)}
              className="block font-medium hover:text-bakery-orange"
            >
              Menu & Shop
            </Link>
            <Link
              to="/track"
              onClick={() => setIsMobileMenuOpen(false)}
              className="block font-medium hover:text-bakery-orange"
            >
              Track Order
            </Link>
            {user && (
              <Link
                to="/profile?tab=notifications"
                onClick={() => setIsMobileMenuOpen(false)}
                className="flex items-center justify-between font-medium hover:text-bakery-orange"
              >
                <span className="flex items-center gap-2">
                  <Bell className="w-4 h-4 text-bakery-orange" />
                  Notifications
                </span>
                {unreadCount > 0 && (
                  <span className="bg-bakery-orange text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                    {unreadCount}
                  </span>
                )}
              </Link>
            )}
            {!user && (
              <Link
                to="/login"
                onClick={() => setIsMobileMenuOpen(false)}
                className="block text-bakery-orange font-bold text-sm pt-2"
              >
                Sign In / Register
              </Link>
            )}
          </div>
        )}
      </header>

      {/* Pickup Slot Modal */}
      <PickupModal isOpen={isPickupModalOpen} onClose={() => setIsPickupModalOpen(false)} />
    </>
  );
};

export default Navbar;
