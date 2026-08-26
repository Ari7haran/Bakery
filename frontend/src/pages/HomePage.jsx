import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  Flame,
  Star,
  Award,
  Clock,
  ChevronRight,
  ShieldCheck,
  Instagram
} from 'lucide-react';
import { api } from '../services/api.js';
import ProductCard from '../components/ProductCard.jsx';

const mockBanners = [
  {
    title: "Freshly Baked Daily With Artisan Love",
    subtitle: "Handcrafted 48-hr sourdoughs, rich butter French croissants, and signature celebration cakes.",
    image: "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=1600&auto=format&fit=crop&q=80",
    cta: "Order Warm Bakery",
    link: "/shop"
  },
  {
    title: "Schedule Express Takeaway Pickup",
    subtitle: "Select your preferred slot & skip the line. Scan your instant QR code at our express counter!",
    image: "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=1600&auto=format&fit=crop&q=80",
    cta: "Schedule Pickup Slot",
    link: "/shop"
  }
];

const instagramPosts = [
  "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&auto=format&fit=crop&q=80",
  "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=400&auto=format&fit=crop&q=80",
  "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=400&auto=format&fit=crop&q=80",
  "https://images.unsplash.com/photo-1576618148400-f54bed99fcfd?w=400&auto=format&fit=crop&q=80",
  "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=400&auto=format&fit=crop&q=80",
  "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&auto=format&fit=crop&q=80"
];

const testimonials = [
  {
    name: "Emily Watson",
    role: "Regular Customer",
    comment: "The Sourdough Bread from Sweet Crumbs is genuinely the best in town. Getting the express QR pickup when running late for work is a total lifesaver!",
    rating: 5,
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80"
  },
  {
    name: "David Miller",
    role: "Pastry Enthusiast",
    comment: "Their Belgian Chocolate Truffle Cake made my daughter's birthday unforgettable. The texture and richness were 10/10!",
    rating: 5,
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"
  },
  {
    name: "Sophia Chen",
    role: "Coffee & Croissant Lover",
    comment: "The butter croissant combined with their Iced Hazelnut Latte is my ultimate daily morning fix. Absolutely 5-star quality!",
    rating: 5,
    avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
  }
];

const faqs = [
  { q: "How does Express Takeaway Pickup work?", a: "Simply add items to your cart, select your preferred date & time slot at checkout, and generate your instant QR receipt. Present the QR code at our Express Counter to grab your freshly packed warm order without waiting!" },
  { q: "Are your bakery items 100% fresh?", a: "Yes! Our master bakers bake twice daily at 6:00 AM and 3:30 PM. All unsold items are donated at the end of each day." },
  { q: "Do you offer Eggless / Pure Veg options?", a: "Absolutely! Most of our items are 100% vegetarian and clearly marked with green veg icons across the menu." },
  { q: "Can I customize birthday cakes?", a: "Yes, you can order custom flavor combinations and write custom messages during checkout notes or call our master chef directly." }
];

const HomePage = () => {
  const [categories, setCategories] = useState([]);
  const [todaysFresh, setTodaysFresh] = useState([]);
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [activeBanner, setActiveBanner] = useState(0);

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        const [catRes, prodRes] = await Promise.all([
          api.get('/categories'),
          api.get('/products')
        ]);
        setCategories(catRes.data);

        const prods = prodRes.data;
        setTodaysFresh(prods.filter(p => p.is_todays_fresh).slice(0, 4));
        setFeaturedProducts(prods.filter(p => p.is_featured).slice(0, 8));
      } catch (err) {
        console.error("Failed to load home data", err);
      }
    };
    fetchHomeData();
  }, []);

  return (
    <div className="space-y-16 pb-16">
      {/* Hero Banner Section */}
      <section className="relative rounded-3xl overflow-hidden shadow-2xl mx-4 sm:mx-6 lg:mx-8 mt-4 bg-bakery-dark">
        <div className="relative h-[480px] sm:h-[540px] w-full flex items-center">
          <img
            src={mockBanners[activeBanner].image}
            alt="Hero Bakery"
            className="absolute inset-0 w-full h-full object-cover opacity-40 transition-opacity duration-700"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-bakery-dark via-bakery-dark/80 to-transparent" />

          <div className="relative z-10 max-w-2xl px-6 sm:px-12 space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-bakery-orange/30 border border-bakery-orange/50 text-amber-300 text-xs font-bold uppercase tracking-wider backdrop-blur-md">
              <Sparkles className="w-4 h-4 text-bakery-orange animate-spin" />
              Artisanal Craft Bakery
            </div>

            <h1 className="font-serif text-4xl sm:text-6xl font-extrabold text-white leading-tight">
              {mockBanners[activeBanner].title}
            </h1>

            <p className="text-sm sm:text-base text-cream-100/90 leading-relaxed font-normal">
              {mockBanners[activeBanner].subtitle}
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <Link
                to={mockBanners[activeBanner].link}
                className="px-7 py-3.5 bg-gradient-to-r from-bakery-orange to-amber-500 text-white font-extrabold text-sm rounded-full shadow-lg hover:scale-105 transition transform flex items-center gap-2"
              >
                <span>{mockBanners[activeBanner].cta}</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to="/shop?category=combo-meals"
                className="px-6 py-3.5 bg-white/10 hover:bg-white/20 text-white font-bold text-sm rounded-full backdrop-blur transition border border-white/20"
              >
                View Combo Deals
              </Link>
            </div>
          </div>
        </div>

        {/* Carousel indicators */}
        <div className="absolute bottom-4 right-8 flex items-center gap-2 z-20">
          {mockBanners.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setActiveBanner(idx)}
              className={`h-2 rounded-full transition-all ${activeBanner === idx ? 'w-8 bg-bakery-orange' : 'w-2 bg-white/50'}`}
            />
          ))}
        </div>
      </section>

      {/* Feature Badges Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 bg-white dark:bg-bakery-chocolate/50 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-md">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-amber-100 dark:bg-amber-950 text-bakery-orange flex items-center justify-center font-bold">
              <Flame className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-xs">Freshly Baked</h4>
              <p className="text-[10px] text-gray-500">2 Batches Daily</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-amber-100 dark:bg-amber-950 text-bakery-orange flex items-center justify-center font-bold">
              <Clock className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-xs">Express Counter Pickup</h4>
              <p className="text-[10px] text-gray-500">QR Code Scanning</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-amber-100 dark:bg-amber-950 text-bakery-orange flex items-center justify-center font-bold">
              <Award className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-xs">100% Organic Wheat</h4>
              <p className="text-[10px] text-gray-500">No Preservatives</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-amber-100 dark:bg-amber-950 text-bakery-orange flex items-center justify-center font-bold">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-xs">Hygiene Certified</h4>
              <p className="text-[10px] text-gray-500">5-Star Standards</p>
            </div>
          </div>
        </div>
      </section>

      {/* Product Categories Slider */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-end justify-between">
          <div>
            <span className="text-bakery-orange font-extrabold text-xs uppercase tracking-widest">
              Explore Our Menu
            </span>
            <h2 className="font-serif text-2xl sm:text-3xl font-bold mt-1">
              Browse Bakery Categories
            </h2>
          </div>
          <Link
            to="/shop"
            className="text-xs font-bold text-bakery-orange hover:text-bakery-brown flex items-center gap-1"
          >
            <span>View All (18)</span>
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="flex gap-4 overflow-x-auto pb-4 pt-1 scrollbar-none">
          {categories.map((c) => (
            <Link
              key={c.id}
              to={`/shop?category=${c.slug}`}
              className="group shrink-0 w-32 p-4 bg-white dark:bg-bakery-chocolate/60 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 text-center hover:border-bakery-orange hover:shadow-lg transition duration-300"
            >
              <div className="w-14 h-14 mx-auto rounded-2xl bg-amber-100/60 dark:bg-amber-950/60 flex items-center justify-center text-2xl group-hover:scale-110 transition transform">
                {c.slug === 'bread' && '🍞'}
                {c.slug === 'cookies' && '🍪'}
                {c.slug === 'pastries' && '🥐'}
                {c.slug === 'cupcakes' && '🧁'}
                {c.slug === 'birthday-cakes' && '🎂'}
                {c.slug === 'brownies' && '🍫'}
                {c.slug === 'pizza' && '🍕'}
                {c.slug === 'burger' && '🍔'}
                {c.slug === 'puffs' && '🥟'}
                {c.slug === 'coffee' && '☕'}
                {c.slug === 'combo-meals' && '🎁'}
                {!['bread','cookies','pastries','cupcakes','birthday-cakes','brownies','pizza','burger','puffs','coffee','combo-meals'].includes(c.slug) && '🍰'}
              </div>
              <h3 className="font-bold text-xs mt-3 text-bakery-dark dark:text-cream-100 group-hover:text-bakery-orange transition">
                {c.name}
              </h3>
            </Link>
          ))}
        </div>
      </section>

      {/* Today's Freshly Baked Highlight Section */}
      <section className="bg-gradient-to-br from-amber-100/60 via-cream-100 to-amber-50 dark:from-bakery-chocolate dark:via-bakery-dark dark:to-amber-950/80 py-12 border-y border-amber-900/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-bakery-orange text-white flex items-center justify-center shadow">
                <Flame className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <h2 className="font-serif text-2xl sm:text-3xl font-bold">Today's Fresh Hot Items</h2>
                <p className="text-xs text-gray-500 dark:text-amber-200/60">Straight out of our morning 6:00 AM oven batch</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {todaysFresh.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="text-center max-w-xl mx-auto space-y-2">
          <span className="text-bakery-orange font-extrabold text-xs uppercase tracking-widest">
            Artisan Favorites
          </span>
          <h2 className="font-serif text-3xl font-bold">Chef's Signature Delights</h2>
          <p className="text-xs text-gray-500 dark:text-amber-200/70">
            Handcrafted with organic wheat, Normandy butter, and Belgian chocolate
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {featuredProducts.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </section>

      {/* Bakery Story & Artisanal Crafting */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-bakery-dark text-cream-100 rounded-3xl p-8 sm:p-12 relative overflow-hidden shadow-2xl flex flex-col lg:flex-row items-center gap-10">
          <div className="flex-1 space-y-6 z-10">
            <span className="text-amber-400 font-extrabold text-xs uppercase tracking-widest">
              Since 1998 • Handcrafted Tradition
            </span>
            <h2 className="font-serif text-3xl sm:text-5xl font-bold text-white leading-tight">
              Baking With Time-Honored European Passion
            </h2>
            <p className="text-xs sm:text-sm text-amber-100/80 leading-relaxed">
              At Sweet Crumbs, we believe great bread takes time. Our sourdough starter has been nurtured for over 28 years. We ferment our dough for 48 hours, yielding an incomparable depth of flavor, crispy caramelized crust, and airy lightness.
            </p>
            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-amber-900/50 text-center">
              <div>
                <span className="font-serif text-2xl sm:text-3xl font-bold text-bakery-orange">28+</span>
                <p className="text-[10px] text-amber-200/70">Years Experience</p>
              </div>
              <div>
                <span className="font-serif text-2xl sm:text-3xl font-bold text-bakery-orange">100%</span>
                <p className="text-[10px] text-amber-200/70">Natural Ingredients</p>
              </div>
              <div>
                <span className="font-serif text-2xl sm:text-3xl font-bold text-bakery-orange">50k+</span>
                <p className="text-[10px] text-amber-200/70">Happy Customers</p>
              </div>
            </div>
          </div>

          <div className="w-full lg:w-1/2 aspect-4/3 rounded-2xl overflow-hidden shadow-xl z-10 border-2 border-amber-500/20">
            <img
              src="https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&auto=format&fit=crop&q=80"
              alt="Baker crafting sourdough"
              className="w-full h-full object-cover hover:scale-105 transition duration-700"
            />
          </div>
        </div>
      </section>

      {/* Customer Reviews Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="text-center max-md mx-auto space-y-2">
          <span className="text-bakery-orange font-extrabold text-xs uppercase tracking-widest">
            Loved By Thousands
          </span>
          <h2 className="font-serif text-3xl font-bold">What Our Customers Say</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {testimonials.map((t, idx) => (
            <div key={idx} className="bg-white dark:bg-bakery-chocolate/60 p-6 rounded-3xl border border-amber-900/10 dark:border-amber-500/20 shadow-md space-y-4">
              <div className="flex items-center gap-1 text-amber-400">
                {[...Array(t.rating)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-current" />
                ))}
              </div>
              <p className="text-xs text-gray-600 dark:text-amber-100/80 italic leading-relaxed">
                "{t.comment}"
              </p>
              <div className="flex items-center gap-3 pt-2 border-t border-amber-900/10">
                <img src={t.avatar} alt={t.name} className="w-10 h-10 rounded-full object-cover" />
                <div>
                  <h4 className="font-bold text-xs">{t.name}</h4>
                  <span className="text-[10px] text-gray-400">{t.role}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Instagram Gallery */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Instagram className="w-5 h-5 text-bakery-orange" />
            <h2 className="font-serif text-xl font-bold">#SweetCrumbsBakery on Instagram</h2>
          </div>
          <a href="#" className="text-xs font-bold text-bakery-orange hover:underline">
            Follow @SweetCrumbsBakery
          </a>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {instagramPosts.map((src, i) => (
            <div key={i} className="group relative aspect-square rounded-2xl overflow-hidden bg-amber-900">
              <img src={src} alt="Instagram Post" className="w-full h-full object-cover group-hover:scale-110 transition duration-500" />
              <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center text-white">
                <Instagram className="w-6 h-6" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* FAQ Accordion */}
      <section className="max-w-3xl mx-auto px-4 space-y-6">
        <div className="text-center space-y-2">
          <h2 className="font-serif text-3xl font-bold">Frequently Asked Questions</h2>
          <p className="text-xs text-gray-500">Everything you need to know about express counter takeaway pickup & ordering.</p>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, idx) => (
            <div key={idx} className="bg-white dark:bg-bakery-chocolate/60 p-4 rounded-2xl border border-amber-900/10 dark:border-amber-500/20 shadow-xs">
              <h4 className="font-bold text-sm text-bakery-dark dark:text-cream-100 flex items-center gap-2">
                <span className="text-bakery-orange font-serif">Q.</span> {faq.q}
              </h4>
              <p className="text-xs text-gray-500 dark:text-amber-200/70 mt-1 pl-5 leading-relaxed">
                {faq.a}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default HomePage;
