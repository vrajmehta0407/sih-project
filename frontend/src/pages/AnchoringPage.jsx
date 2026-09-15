import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
  MapPin,
  LocateFixed,
  Navigation,
  Plus,
  Trash2,
  RefreshCw,
  Compass,
  CheckCircle2,
} from 'lucide-react';

const CATEGORY_OPTIONS = [
  { value: 'market', label: 'Market' },
  { value: 'retail', label: 'Retail Shop' },
  { value: 'warehouse', label: 'Warehouse' },
  { value: 'gas_station', label: 'Fuel Station' },
  { value: 'portable', label: 'Portable/Van' },
];

export const AnchoringPage = () => {
  const { user } = useAuth();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    name: '',
    category: 'market',
    address: '',
    latitude: '',
    longitude: '',
  });

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const res = await api.get('/anchoring/');
      const data = res.data?.data ?? res.data ?? [];
      setRecords(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not load anchored locations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const onLocate = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser.');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setForm((f) => ({
          ...f,
          latitude: pos.coords.latitude.toFixed(6),
          longitude: pos.coords.longitude.toFixed(6),
        }));
        setError('');
      },
      () => setError('Could not fetch current location (permission denied).')
    );
  };

  const addRecord = async () => {
    setError('');
    try {
      const payload = {
        name: form.name,
        category: form.category,
        address: form.address,
        latitude: form.latitude ? parseFloat(form.latitude) : null,
        longitude: form.longitude ? parseFloat(form.longitude) : null,
      };
      await api.post('/anchoring/', payload);
      setForm({
        name: '',
        category: 'market',
        address: '',
        latitude: '',
        longitude: '',
      });
      fetchRecords();
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not add anchored location.');
    }
  };

  const removeRecord = async (id) => {
    try {
      await api.delete(`/anchoring/${id}`);
      setRecords((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not remove anchored location.');
    }
  };

  const input = 'w-full px-3 py-2.5 rounded-2xl bg-white border border-slate-200 shadow-sm text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-mesh-vibrant rounded-3xl p-6 sm:p-8 border border-white/60 shadow-soft">
        <div className="flex items-center space-x-3 mb-3">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-violet-600 to-pink-600 flex items-center justify-center text-white shadow-tinted-blue">
            <MapPin className="h-5 w-5" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-extrabold text-slate-900">
              Location Anchoring
            </h1>
            <p className="text-xs text-slate-500 font-medium">
              Anchor high-risk traders and premises for targeted inspection
            </p>
          </div>
        </div>
        <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-white/70 text-amber-700 border border-amber-200">
          <LocateFixed className="h-3 w-3" />
          <span>GIS-augmented risk profile</span>
        </span>
      </div>

      {error && (
        <div className="px-4 py-3 rounded-2xl text-sm font-semibold bg-rose-50 text-rose-700 border border-rose-200">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Add form */}
        <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-5 sm:p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-display text-lg font-bold text-slate-900">
              Anchor a Location
            </h2>
            <Compass className="h-5 w-5 text-blue-500" />
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wide">
                Premise Name
              </label>
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className={input}
                placeholder="Sharma Traders"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wide">
                Category
              </label>
              <select
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                className={input}
              >
                {CATEGORY_OPTIONS.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wide">
                Address
              </label>
              <input
                value={form.address}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
                className={input}
                placeholder="Shop 12, MG Road Market"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wide">
                  Latitude
                </label>
                <input
                  value={form.latitude}
                  onChange={(e) => setForm({ ...form, latitude: e.target.value })}
                  className={input}
                  placeholder="28.6139"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wide">
                  Longitude
                </label>
                <input
                  value={form.longitude}
                  onChange={(e) => setForm({ ...form, longitude: e.target.value })}
                  className={input}
                  placeholder="77.2090"
                />
              </div>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={onLocate}
                className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-2xl bg-slate-100 text-slate-700 border border-slate-200 text-sm font-bold hover:bg-slate-200 transition-colors"
              >
                <Navigation className="h-4 w-4" />
                <span>Use My Location</span>
              </button>
              <button
                onClick={addRecord}
                className="flex-1 inline-flex items-center justify-center space-x-2 px-4 py-2.5 rounded-2xl bg-gradient-to-r from-blue-600 via-violet-600 to-pink-600 text-white font-bold text-sm shadow-tinted-blue hover:opacity-95 transition-opacity"
              >
                <Plus className="h-4 w-4" />
                <span>Anchor Location</span>
              </button>
            </div>
          </div>
        </div>

        {/* Records list */}
        <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-5 sm:p-6">
          <div className="flex items-center justify-between mb-1">
            <h2 className="font-display text-lg font-bold text-slate-900">
              Anchored Locations
            </h2>
            <span className="text-xs font-bold text-slate-400">{records.length} total</span>
          </div>
          <p className="text-xs text-slate-500 mb-5">
            Pinned premises refine the AI dispatch map.
          </p>
          {loading ? (
            <div className="h-48 rounded-2xl animate-pulse bg-slate-100" />
          ) : records.length === 0 ? (
            <div className="text-center py-12">
              <div className="h-14 w-14 rounded-2xl bg-slate-50 flex items-center justify-center text-slate-300 shadow-sm mx-auto mb-3">
                <MapPin className="h-7 w-7" />
              </div>
              <p className="text-sm font-semibold text-slate-400">
                No anchored locations yet
              </p>
            </div>
          ) : (
            <div className="space-y-3 max-h-[34rem] overflow-y-auto pr-1">
              {records.map((r) => (
                <div
                  key={r.id}
                  className="flex items-start justify-between p-3 rounded-2xl border border-slate-100 bg-slate-50/60"
                >
                  <div className="min-w-0 pr-2">
                    <p className="text-sm font-bold text-slate-800">{r.name}</p>
                    <p className="text-xs text-slate-500">{r.address || r.category}</p>
                    <div className="flex flex-wrap gap-1.5 mt-1.5">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-violet-50 text-violet-600 border border-violet-100 uppercase">
                        {r.category}
                      </span>
                      {typeof r.latitude === 'number' &&
                        typeof r.longitude === 'number' && (
                          <span className="inline-flex items-center space-x-0.5 text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 border border-blue-100">
                            <LocateFixed className="h-2.5 w-2.5" />
                            <span>
                              {r.latitude.toFixed(4)}, {r.longitude.toFixed(4)}
                            </span>
                          </span>
                        )}
                      {r.is_anchored === false && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 border border-slate-200">
                          Partner-provided
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => removeRecord(r.id)}
                    className="text-slate-300 hover:text-rose-500 transition-colors shrink-0"
                    aria-label="Remove"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="text-right text-[11px] text-slate-400 font-medium flex items-center justify-end space-x-1">
        <CheckCircle2 className="h-3 w-3" />
        <span>Anchoring syncs via /anchoring ({user?.full_name || 'officer'})</span>
      </div>
    </div>
  );
};

export default AnchoringPage;
