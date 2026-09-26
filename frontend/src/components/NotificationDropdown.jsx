import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bell,
  CheckCheck,
  Trash2,
  ExternalLink,
  ShoppingBag,
  Flame,
  AlertTriangle,
  CreditCard,
  CheckCircle2,
  RefreshCw,
  X
} from 'lucide-react';
import { notificationService } from '../services/notificationService.js';
import { useToast } from '../context/ToastContext.jsx';

const formatTimeAgo = (dateString) => {
  if (!dateString) return '';
  const now = new Date();
  const past = new Date(dateString.endsWith('Z') ? dateString : dateString + 'Z');
  const diffSec = Math.floor((now - past) / 1000);

  if (diffSec < 60) return 'Just now';
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  return `${Math.floor(diffSec / 86400)}d ago`;
};

const getNotificationIcon = (type) => {
  switch (type) {
    case 'order_created':
      return <ShoppingBag className="w-4 h-4 text-amber-500" />;
    case 'order_status':
      return <Flame className="w-4 h-4 text-bakery-orange" />;
    case 'payment':
      return <CreditCard className="w-4 h-4 text-emerald-500" />;
    case 'inventory':
      return <AlertTriangle className="w-4 h-4 text-red-500" />;
    case 'loyalty':
      return <CheckCircle2 className="w-4 h-4 text-amber-400" />;
    default:
      return <Bell className="w-4 h-4 text-amber-600" />;
  }
};

const NotificationDropdown = ({ isOpen, onClose, user, onUnreadCountChange }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all'); // 'all' or 'unread'
  const toast = useToast();
  const navigate = useNavigate();
  const panelRef = useRef(null);

  const fetchNotifications = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const data = await notificationService.getNotifications({
        limit: 20,
        is_read: filter === 'unread' ? false : undefined
      });
      setNotifications(data.items || []);
      if (onUnreadCountChange) {
        onUnreadCountChange(data.unread_count || 0);
      }
    } catch (err) {
      console.error('Failed to load notifications', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen, filter, user]);

  // Click outside listener
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);

  const handleMarkAsRead = async (id, linkUrl, e) => {
    if (e) e.stopPropagation();
    try {
      await notificationService.markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      if (onUnreadCountChange) {
        setNotifications((latest) => {
          const count = latest.filter((n) => !n.is_read).length;
          onUnreadCountChange(count);
          return latest;
        });
      }
      if (linkUrl) {
        onClose();
        navigate(linkUrl);
      }
    } catch (err) {
      console.error('Failed to mark read', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      if (onUnreadCountChange) {
        onUnreadCountChange(0);
      }
      toast.success('All notifications marked as read');
    } catch (err) {
      toast.error('Failed to mark notifications as read');
    }
  };

  const handleDelete = async (id, e) => {
    if (e) e.stopPropagation();
    try {
      await notificationService.deleteNotification(id);
      const remaining = notifications.filter((n) => n.id !== id);
      setNotifications(remaining);
      if (onUnreadCountChange) {
        const count = remaining.filter((n) => !n.is_read).length;
        onUnreadCountChange(count);
      }
    } catch (err) {
      toast.error('Failed to dismiss notification');
    }
  };

  if (!isOpen) return null;

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <div
      ref={panelRef}
      className="absolute right-0 mt-2 w-80 sm:w-96 bg-white dark:bg-bakery-chocolate rounded-3xl shadow-2xl border border-amber-900/10 dark:border-amber-500/20 z-50 overflow-hidden animate-in fade-in slide-in-from-top-2"
    >
      {/* Header */}
      <div className="p-4 border-b border-amber-900/10 dark:border-amber-500/10 flex items-center justify-between bg-amber-50/50 dark:bg-amber-950/40">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-bakery-orange" />
          <h3 className="font-serif font-bold text-sm text-bakery-dark dark:text-cream-100">
            Notifications
          </h3>
          {unreadCount > 0 && (
            <span className="bg-bakery-orange text-white text-[10px] font-extrabold px-2 py-0.5 rounded-full">
              {unreadCount} new
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllRead}
              className="text-[11px] font-semibold text-amber-700 dark:text-amber-300 hover:text-bakery-orange flex items-center gap-1 transition"
              title="Mark all as read"
            >
              <CheckCheck className="w-3.5 h-3.5" />
              <span>Mark all read</span>
            </button>
          )}
          <button
            onClick={onClose}
            className="p-1 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-cream-100 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="px-4 py-2 border-b border-amber-900/10 dark:border-amber-500/10 flex gap-2 text-xs">
        <button
          onClick={() => setFilter('all')}
          className={`px-3 py-1 rounded-full font-bold transition ${
            filter === 'all'
              ? 'bg-bakery-orange text-white'
              : 'text-gray-500 hover:text-bakery-orange'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setFilter('unread')}
          className={`px-3 py-1 rounded-full font-bold transition ${
            filter === 'unread'
              ? 'bg-bakery-orange text-white'
              : 'text-gray-500 hover:text-bakery-orange'
          }`}
        >
          Unread only
        </button>
      </div>

      {/* Notification List */}
      <div className="max-h-80 overflow-y-auto divide-y divide-amber-900/5 dark:divide-amber-500/10">
        {loading ? (
          <div className="p-8 text-center text-xs text-gray-400 space-y-2">
            <RefreshCw className="w-5 h-5 text-bakery-orange animate-spin mx-auto" />
            <p>Loading notifications...</p>
          </div>
        ) : notifications.length === 0 ? (
          <div className="p-8 text-center space-y-2">
            <span className="text-3xl block">🥐</span>
            <p className="text-xs font-bold text-gray-600 dark:text-amber-200">
              {filter === 'unread' ? 'No unread notifications' : 'No notifications yet'}
            </p>
            <p className="text-[11px] text-gray-400">
              When fresh orders or baking status changes happen, you will see them here!
            </p>
          </div>
        ) : (
          notifications.map((n) => (
            <div
              key={n.id}
              onClick={() => handleMarkAsRead(n.id, n.link_url)}
              className={`p-3.5 hover:bg-amber-50/80 dark:hover:bg-amber-900/30 transition cursor-pointer flex gap-3 items-start group ${
                !n.is_read
                  ? 'bg-amber-50/40 dark:bg-amber-950/30'
                  : 'opacity-85'
              }`}
            >
              <div className="mt-0.5 p-2 rounded-xl bg-amber-100 dark:bg-amber-900/50 shrink-0">
                {getNotificationIcon(n.notification_type)}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-1">
                  <p
                    className={`text-xs font-bold leading-tight truncate ${
                      !n.is_read
                        ? 'text-bakery-dark dark:text-cream-100 font-extrabold'
                        : 'text-gray-600 dark:text-amber-200/80'
                    }`}
                  >
                    {n.title}
                  </p>
                  <span className="text-[10px] text-gray-400 shrink-0">
                    {formatTimeAgo(n.created_at)}
                  </span>
                </div>

                <p className="text-[11px] text-gray-500 dark:text-gray-300 mt-1 line-clamp-2 leading-relaxed">
                  {n.message}
                </p>

                {n.link_url && (
                  <div className="mt-1.5 flex items-center gap-1 text-[10px] font-bold text-bakery-orange">
                    <span>View Details</span>
                    <ExternalLink className="w-3 h-3" />
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex flex-col items-center gap-1 shrink-0 pt-0.5">
                {!n.is_read && (
                  <span
                    className="w-2 h-2 rounded-full bg-bakery-orange"
                    title="Unread"
                  />
                )}
                <button
                  onClick={(e) => handleDelete(n.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition rounded"
                  title="Dismiss notification"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="p-2.5 bg-amber-50/50 dark:bg-amber-950/40 border-t border-amber-900/10 dark:border-amber-500/10 text-center">
        <button
          onClick={() => {
            onClose();
            navigate('/profile?tab=notifications');
          }}
          className="text-xs font-bold text-bakery-orange hover:underline"
        >
          View All Notifications in Profile →
        </button>
      </div>
    </div>
  );
};

export default NotificationDropdown;
