import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Lock, Mail, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';
import { api } from '../services/api.js';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await api.post('/auth/login', { email, password });
      login(res.data.access_token, res.data.user);
      if (res.data.user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/');
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-12 px-4">
      <div className="bg-white dark:bg-bakery-chocolate/80 rounded-3xl p-8 border border-amber-900/10 dark:border-amber-500/20 shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-bakery-orange text-white flex items-center justify-center text-2xl mx-auto shadow-md">
            🥐
          </div>
          <h1 className="font-serif text-2xl font-bold">Welcome Back to Sweet Crumbs</h1>
          <p className="text-xs text-gray-500">Sign in to track orders, manage addresses & access VIP points.</p>
        </div>

        {error && (
          <div className="p-3 bg-red-50 text-red-600 rounded-xl text-xs font-semibold text-center border border-red-200">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold mb-1">Email Address</label>
            <div className="relative">
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="customer@example.com"
                className="w-full pl-9 pr-3 py-2.5 text-xs rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/30"
              />
              <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold mb-1">Password</label>
            <div className="relative">
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2.5 text-xs rounded-xl border border-amber-900/20 bg-cream-50 dark:bg-amber-900/30"
              />
              <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-bakery-brown to-bakery-orange text-white font-extrabold text-xs rounded-xl shadow-lg hover:opacity-95 transition flex items-center justify-center gap-2"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="p-3 bg-amber-50 dark:bg-amber-950/40 rounded-2xl text-[11px] text-gray-600 dark:text-amber-200/80 space-y-1 border border-amber-900/10">
          <p className="font-bold text-bakery-orange">Demo Credentials:</p>
          <p>• Admin: <code>admin@sweetcrumbs.com</code> / <code>admin123</code></p>
          <p>• Customer: <code>sarah@example.com</code> / <code>customer123</code></p>
        </div>

        <p className="text-center text-xs text-gray-500">
          Don't have an account?{' '}
          <Link to="/register" className="font-bold text-bakery-orange hover:underline">
            Register Here
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
