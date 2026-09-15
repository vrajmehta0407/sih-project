import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
  ShieldCheck,
  Users,
  UserCog,
  Activity,
  Database,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Cpu,
} from 'lucide-react';

export const AdminPage = () => {
  const { user } = useAuth();
  const [system, setSystem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchSystem = async () => {
    setLoading(true);
    try {
      const res = await api.get('/admin/system/status');
      setSystem(res.data?.data ?? res.data ?? res);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not load system status.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystem();
  }, []);

  const STATS = [
    { icon: Users, label: 'Registered Officers', key: 'users', color: 'from-blue-500 to-violet-500' },
    { icon: Database, label: 'Active Inspections', key: 'inspections', color: 'from-violet-500 to-pink-500' },
    { icon: Activity, label: 'Reports Filed', key: 'reports', color: 'from-emerald-500 to-teal-500' },
    { icon: UserCog, label: 'Active Roles', key: 'roles', color: 'from-amber-500 to-rose-500' },
  ];

  const count = (key) => {
    const obj = system?.counts ?? system?.stats ?? system ?? {};
    if (typeof obj === 'object' && obj !== null) return obj[key] ?? '—';
    return '—';
  };

  const statusOk = system?.status === 'ok' || system?.healthy === true || system?.db_connected === true;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-mesh-vibrant rounded-3xl p-6 sm:p-8 border border-white/60 shadow-soft">
        <div className="flex items-center space-x-3 mb-3">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-violet-600 to-pink-600 flex items-center justify-center text-white shadow-tinted-blue">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-extrabold text-slate-900">
              Admin Console
            </h1>
            <p className="text-xs text-slate-500 font-medium">
              System health, platform statistics and configuration
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span
            className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold border ${
              statusOk
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-amber-50 text-amber-700 border-amber-200'
            }`}
          >
            {statusOk ? (
              <CheckCircle2 className="h-3.5 w-3.5" />
            ) : (
              <AlertTriangle className="h-3.5 w-3.5" />
            )}
            <span>{statusOk ? 'All Systems Operational' : 'Check Required'}</span>
          </span>
          <button
            onClick={fetchSystem}
            className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-white/70 text-slate-700 border border-slate-200 hover:bg-white transition-colors"
          >
            <RefreshCw className="h-3 w-3" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="px-4 py-3 rounded-2xl text-sm font-semibold bg-rose-50 text-rose-700 border border-rose-200">
          {error}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {STATS.map((s, i) => {
          const Icon = s.icon;
          return (
            <div
              key={i}
              className="rounded-3xl bg-white border border-slate-200 shadow-sm p-4"
            >
              <div
                className={`h-10 w-10 rounded-2xl bg-gradient-to-br ${s.color} flex items-center justify-center text-white shadow-sm mb-3`}
              >
                <Icon className="h-5 w-5" />
              </div>
              <p className="text-2xl font-extrabold text-slate-900">
                {loading ? '—' : count(s.key)}
              </p>
              <p className="text-xs font-semibold text-slate-500">{s.label}</p>
            </div>
          );
        })}
      </div>

      {/* System info */}
      <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-5 sm:p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Cpu className="h-5 w-5 text-blue-500" />
          <h2 className="font-display text-lg font-bold text-slate-900">
            Platform Details
          </h2>
        </div>
        {loading ? (
          <div className="h-32 rounded-2xl animate-pulse bg-slate-100" />
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {[
              { label: 'API Status', value: system?.api ?? 'online' },
              { label: 'Database', value: system?.database ?? (statusOk ? 'connected' : 'checking') },
              { label: 'Version', value: system?.version ?? system?.app_version ?? 'v4' },
              { label: 'Environment', value: system?.environment ?? system?.env ?? 'production' },
              { label: 'Registered Roles', value: system?.role_count ?? system?.roles ?? '—' },
            ].map((f, i) => (
              <div
                key={i}
                className="p-4 rounded-2xl bg-slate-50 border border-slate-100"
              >
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-1">
                  {f.label}
                </p>
                <p className="text-sm font-bold text-slate-700">{f.value}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-3xl border border-amber-100 bg-amber-50 p-4 flex items-start space-x-2.5">
        <AlertTriangle className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
        <p className="text-xs text-amber-800 font-medium">
          The Admin Console exposes platform-level status. Role-based access is
          enforced server-side to restrict sensitive administrative actions to
          privileged operators.
        </p>
      </div>

      <div className="text-right text-[11px] text-slate-400 font-medium">
        Console synced via /admin/system/status ({user?.full_name || 'admin'})
      </div>
    </div>
  );
};

export default AdminPage;
