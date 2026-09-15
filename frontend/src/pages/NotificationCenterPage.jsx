import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
  Bell,
  BellRing,
  Megaphone,
  Inbox,
  CheckCheck,
  AlertTriangle,
  Info,
  Sparkles,
  Star,
  Search,
  Filter,
  RefreshCw,
  Clock,
} from 'lucide-react';

const priorityStyles = {
  urgent: 'bg-rose-50 text-rose-700 border-rose-200',
  high: 'bg-orange-50 text-orange-700 border-orange-200',
  normal: 'bg-blue-50 text-blue-700 border-blue-200',
  low: 'bg-slate-100 text-slate-600 border-slate-200',
};

const categoryStyles = {
  announcement: 'bg-violet-50 text-violet-700 border-violet-200',
  alert: 'bg-amber-50 text-amber-700 border-amber-200',
  inspection: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  system: 'bg-slate-100 text-slate-600 border-slate-200',
  general: 'bg-blue-50 text-blue-700 border-blue-200',
};

const CategoryIcon = ({ category }) => {
  if (category === 'announcement') return <Megaphone className="h-4 w-4" />;
  if (category === 'alert') return <AlertTriangle className="h-4 w-4" />;
  if (category === 'inspection') return <Search className="h-4 w-4" />;
  if (category === 'system') return <Sparkles className="h-4 w-4" />;
  return <Info className="h-4 w-4" />;
};

export const NotificationCenterPage = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);
  const [filter, setFilter] = useState('all');
  const [category, setCategory] = useState('');
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const res = await api.get('/notifications/', {
        params: {
          category: category || undefined,
          unread_only: filter === 'unread',
        },
      });
      const data = res.data?.data ?? res.data;
      const items = Array.isArray(data) ? data : data?.items ?? data?.notifications ?? [];
      setNotifications(items);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not load notifications.');
    } finally {
      setLoading(false);
    }
  };

  const fetchUnreadCount = async () => {
    try {
      const res = await api.get('/notifications/unread-count');
      setUnreadCount(res.data?.data?.unread_count ?? 0);
    } catch {
      setUnreadCount(0);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [category, filter]);

  useEffect(() => {
    fetchUnreadCount();
  }, [notifications]);

  const markRead = async (id) => {
    try {
      await api.patch(`/notifications/${id}/read`, {});
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setSuccess('Notification marked as read.');
      setTimeout(() => setSuccess(''), 2500);
    } catch {
      setError('Could not mark notification as read.');
    }
  };

  const markAllRead = async () => {
    try {
      await api.patch('/notifications/read-all', {});
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setSuccess('All notifications marked as read.');
      setTimeout(() => setSuccess(''), 2500);
    } catch {
      setError('Could not mark all as read.');
    }
  };

  const filtered = notifications.filter((n) => {
    const q = search.toLowerCase();
    const titleMatch = (n.title || '').toLowerCase().includes(q);
    const bodyMatch = (n.body || '').toLowerCase().includes(q);
    return titleMatch || bodyMatch;
  });

  const unread = notifications.filter((n) => !n.is_read).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-mesh-vibrant rounded-3xl p-6 sm:p-8 border border-white/60 shadow-soft">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-violet-600 to-pink-600 flex items-center justify-center text-white shadow-tinted-blue">
                <BellRing className="h-5 w-5" />
              </div>
              <h1 className="font-display text-2xl font-extrabold text-slate-900">
                Notification Center
              </h1>
            </div>
            <p className="text-sm text-slate-500 font-medium">
              Targeted officer alerts, announcements and system broadcasts
            </p>
            <div className="mt-3 flex items-center space-x-3">
              <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200">
                <span className="h-2 w-2 rounded-full bg-rose-500 animate-pulse" />
                <span>{unreadCount} unread</span>
              </span>
              <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                <Inbox className="h-3.5 w-3.5" />
                <span>{filtered.length} in inbox</span>
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={markAllRead}
              className="inline-flex items-center space-x-1.5 text-xs font-bold px-3.5 py-2 rounded-full bg-white hover:bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-sm transition-colors"
            >
              <CheckCheck className="h-3.5 w-3.5" />
              <span>Mark All Read</span>
            </button>
            <button
              onClick={() => {
                fetchNotifications();
                fetchUnreadCount();
              }}
              className="inline-flex items-center space-x-1.5 text-xs font-bold px-3.5 py-2 rounded-full bg-white hover:bg-blue-50 text-blue-700 border border-blue-200 shadow-sm transition-colors"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {(error || success) && (
        <div
          className={`px-4 py-3 rounded-2xl text-sm font-semibold border ${
            error
              ? 'bg-rose-50 text-rose-700 border-rose-200'
              : 'bg-emerald-50 text-emerald-700 border-emerald-200'
          }`}
        >
          {error || success}
        </div>
      )}

      {/* Filter / Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex rounded-2xl bg-white border border-slate-200 shadow-sm p-1 flex-1">
          {[
            { key: 'all', label: 'All' },
            { key: 'unread', label: 'Unread' },
          ].map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`flex-1 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors ${
                filter === f.key
                  ? 'bg-gradient-to-r from-blue-600 to-violet-600 text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search notifications..."
            className="w-full pl-9 pr-3 py-2 rounded-2xl bg-white border border-slate-200 shadow-sm text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          />
        </div>

        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="pl-9 pr-3 py-2 rounded-2xl bg-white border border-slate-200 shadow-sm text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40 appearance-none cursor-pointer"
          >
            <option value="">All Categories</option>
            <option value="announcement">Announcement</option>
            <option value="alert">Alert</option>
            <option value="inspection">Inspection</option>
            <option value="system">System</option>
            <option value="general">General</option>
          </select>
        </div>
      </div>

      {/* Notification List */}
      <div className="space-y-3">
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="h-24 rounded-3xl bg-white border border-slate-200 shadow-sm animate-pulse"
            />
          ))
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 rounded-3xl bg-white border border-slate-200 shadow-sm">
            <div className="h-14 w-14 rounded-2xl bg-slate-100 flex items-center justify-center text-slate-400 mx-auto mb-3">
              <Bell className="h-7 w-7" />
            </div>
            <p className="text-sm font-semibold text-slate-500">No notifications found</p>
            <p className="text-xs text-slate-400 mt-1">New alerts will appear here.</p>
          </div>
        ) : (
          filtered.map((n) => (
            <button
              key={n.id}
              onClick={() => !n.is_read && markRead(n.id)}
              className={`w-full text-left rounded-3xl p-4 sm:p-5 border shadow-sm transition-all hover:shadow-soft ${
                n.is_read
                  ? 'bg-white border-slate-200'
                  : 'bg-gradient-to-br from-blue-50/80 to-violet-50/50 border-blue-200'
              } ${!n.is_read ? 'cursor-pointer ring-1 ring-blue-100' : ''}`}
            >
              <div className="flex items-start space-x-3">
                <div
                  className={`h-9 w-9 rounded-2xl flex items-center justify-center shrink-0 ${
                    n.is_read ? 'bg-slate-100 text-slate-500' : 'bg-white text-blue-600 shadow-sm'
                  }`}
                >
                  <CategoryIcon category={n.category} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p
                      className={`text-sm font-bold truncate ${
                        n.is_read ? 'text-slate-600' : 'text-slate-900'
                      }`}
                    >
                      {n.title}
                    </p>
                    {!n.is_read && (
                      <span className="h-2.5 w-2.5 rounded-full bg-blue-500 shrink-0 animate-pulse" />
                    )}
                  </div>
                  {n.body && (
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed">{n.body}</p>
                  )}
                  <div className="mt-2.5 flex flex-wrap items-center gap-2">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide border ${
                        priorityStyles[n.priority] || priorityStyles.normal
                      }`}
                    >
                      {n.priority || 'normal'}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide border capitalize ${
                        categoryStyles[n.category] || categoryStyles.general
                      }`}
                    >
                      {n.category || 'general'}
                    </span>
                    {n.created_at && (
                      <span className="inline-flex items-center space-x-1 text-[10px] font-medium text-slate-400">
                        <Clock className="h-3 w-3" />
                        <span>{new Date(n.created_at).toLocaleString()}</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </button>
          ))
        )}
      </div>

      {/* Profile footer */}
      <div className="text-right text-[11px] text-slate-400 font-medium">
        Labeled for {user?.full_name || 'Officer'}
      </div>
    </div>
  );
};

export default NotificationCenterPage;
