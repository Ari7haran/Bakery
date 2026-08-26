import React from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Phone, Clock, Instagram, Facebook, Twitter, Send, Award, ShieldCheck } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-bakery-dark text-cream-100 border-t border-amber-900/30 pt-16 pb-8 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10 pb-12 border-b border-amber-900/40">
          
          {/* Col 1: Brand Info */}
          <div className="space-y-4">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-bakery-orange flex items-center justify-center text-white text-lg">
                🥐
              </div>
              <span className="font-serif text-2xl font-bold tracking-tight text-white">
                Sweet<span className="text-bakery-orange">Crumbs</span>
              </span>
            </div>
            <p className="text-xs text-amber-200/70 leading-relaxed">
              Crafting premium European sourdoughs, artisanal pastries, custom celebration cakes, and warm savory snacks daily since 1998.
            </p>
            <div className="flex items-center gap-3 pt-2">
              <a href="#" className="w-8 h-8 rounded-full bg-amber-950 flex items-center justify-center hover:bg-bakery-orange transition text-amber-200 hover:text-white">
                <Instagram className="w-4 h-4" />
              </a>
              <a href="#" className="w-8 h-8 rounded-full bg-amber-950 flex items-center justify-center hover:bg-bakery-orange transition text-amber-200 hover:text-white">
                <Facebook className="w-4 h-4" />
              </a>
              <a href="#" className="w-8 h-8 rounded-full bg-amber-950 flex items-center justify-center hover:bg-bakery-orange transition text-amber-200 hover:text-white">
                <Twitter className="w-4 h-4" />
              </a>
            </div>
          </div>

          {/* Col 2: Quick Links */}
          <div>
            <h4 className="font-serif text-base font-bold text-amber-300 mb-4 uppercase tracking-wider">
              Popular Categories
            </h4>
            <ul className="space-y-2 text-xs text-amber-100/70">
              <li><Link to="/shop?category=bread" className="hover:text-bakery-orange transition">Artisanal Breads & Sourdough</Link></li>
              <li><Link to="/shop?category=pastries" className="hover:text-bakery-orange transition">Butter French Croissants</Link></li>
              <li><Link to="/shop?category=birthday-cakes" className="hover:text-bakery-orange transition">Custom Birthday Cakes</Link></li>
              <li><Link to="/shop?category=cupcakes" className="hover:text-bakery-orange transition">Gourmet Frosted Cupcakes</Link></li>
              <li><Link to="/shop?category=pizza" className="hover:text-bakery-orange transition">Wood-Fired Bakery Pizzas</Link></li>
              <li><Link to="/shop?category=combo-meals" className="hover:text-bakery-orange transition">High-Tea Combo Bundles</Link></li>
            </ul>
          </div>

          {/* Col 3: Operating Hours & Contact */}
          <div>
            <h4 className="font-serif text-base font-bold text-amber-300 mb-4 uppercase tracking-wider">
              Hours & Takeaway
            </h4>
            <ul className="space-y-3 text-xs text-amber-100/70">
              <li className="flex items-start gap-2">
                <Clock className="w-4 h-4 text-bakery-orange shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-white">Mon - Sun: 7:00 AM - 10:00 PM</p>
                  <p className="text-[10px] text-amber-400/80">Fresh Batch Times: 7:30 AM & 4:00 PM</p>
                </div>
              </li>
              <li className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-bakery-orange shrink-0" />
                <span>428 Baker Street, Gourmet Quarter</span>
              </li>
              <li className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-bakery-orange shrink-0" />
                <span>+1 (800) 555-BAKE</span>
              </li>
            </ul>
          </div>

          {/* Col 4: Newsletter */}
          <div>
            <h4 className="font-serif text-base font-bold text-amber-300 mb-4 uppercase tracking-wider">
              Sweet VIP Newsletter
            </h4>
            <p className="text-xs text-amber-200/70 mb-3">
              Subscribe to get secret weekend discount codes & birthday cake offers!
            </p>
            <form onSubmit={(e) => { e.preventDefault(); alert("Thank you for subscribing to Sweet Crumbs!"); }} className="space-y-2">
              <div className="relative">
                <input
                  type="email"
                  required
                  placeholder="Enter your email address"
                  className="w-full pl-3 pr-10 py-2 rounded-xl bg-amber-950/80 border border-amber-900/60 text-xs text-white placeholder-amber-400/40 focus:outline-none focus:ring-1 focus:ring-bakery-orange"
                />
                <button
                  type="submit"
                  className="absolute right-1 top-1/2 -translate-y-1/2 p-1.5 bg-bakery-orange text-white rounded-lg hover:bg-bakery-brown transition"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </form>
          </div>

        </div>

        {/* Bottom copyright */}
        <div className="pt-6 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-amber-200/60">
          <p>© 2026 Sweet Crumbs Bakery Ltd. All Rights Reserved.</p>
          <div className="flex items-center gap-6">
            <span className="flex items-center gap-1"><Award className="w-3.5 h-3.5 text-amber-400" /> 100% Fresh Daily Guarantee</span>
            <span className="flex items-center gap-1"><ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> QR Express Counter Pickup</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
