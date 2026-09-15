import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
  Shield,
  FileCheck2,
  Database,
  Clock,
  Check,
  X,
  Eye,
  Lock,
  Trash2,
} from 'lucide-react';

const CONSENT_TYPES = [
  { key: 'personal_data', label: 'Personal Data Processing', description: 'Allow processing of personal identification data for inspection handling.' },
  { key: 'location', label: 'Location Data', description: 'Allow collection of GPS / location data during field inspections.' },
  { key: 'photo_evidence', label: 'Photo Evidence', description: 'Allow capturing and storing photographic evidence of violations.' },
  { key: 'analytics', label: 'Analytics & Reporting', description: 'Allow anonymized aggregation for compliance analytics.' },
  { key: 'marketing', label: 'Communications', description: 'Allow compliance update communications via contact channels.' },
];

const RETENTION_POLICIES = [
  { category: 'Inspection Records', retention_days: 1825, disposal_method: 'Anonymized Purge', icon: Database },
  { category: 'Photo Evidence', retention_days: 730, disposal_method: 'Secure Delete', icon: Eye },
  { category: 'Complaints', retention_days: 1095, disposal_method: 'Anonymized Purge', icon: FileCheck2 },
  { category: 'Audit Logs', retention_days: 3650, disposal_method: 'Archive + Purge', icon: Clock },
];

export const PrivacyCenterPage = () => {
  const { user } = useAuth();
  const [consents, setConsents] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchConsents = async () => {
    setLoading(true);
    try {
      const res = await api.get('/privacy/consents');
      const data = res.data?.data ?? res.data ?? [];
      const map = {};
      (Array.isArray(data) ? data : []).forEach((c) => {
        map[c.consent_type] = c.is_granted;
      });
      setConsents(map);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not load consent records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConsents();
  }, []);

  const updateConsent = async (type, granted) => {
    try {
      await api.post('/privacy/consents', {
        consent_type: type,
        consent_version: '1.0',
        is_granted: granted,
      });
      setConsents((prev) => ({ ...prev, [type]: granted }));
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not update consent.');
      await fetchConsents();
    }
  };

  const Toggle = ({ checked, onChange }) => (
    <button
      onClick={() => onChange(!checked)}
      className={`relative inline-flex items-center h-6 w-11 rounded-full transition-colors ${
        checked ? 'bg-gradient-to-r from-blue-600 to-violet-600' : 'bg-slate-200'
      }`}
    >
      <span
        className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition-transform ${
          checked ? 'translate-x-5' : 'translate-x-0.5'
        }`}
      />
    </button>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-mesh-vibrant rounded-3xl p-6 sm:p-8 border border-white/60 shadow-soft">
        <div className="flex items-center space-x-3 mb-3">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-violet-600 to-pink-600 flex items-center justify-center text-white shadow-tinted-blue">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-extrabold text-slate-900">
              Privacy Center
            </h1>
            <p className="text-xs text-slate-500 font-medium">
              Consents, data retention and handling policies
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-white/70 text-emerald-700 border border-emerald-200">
            <Lock className="h-3 w-3" />
            <span>Data Protection · IT Act / DPDP</span>
          </span>
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-white/70 text-blue-700 border border-blue-200">
            <Eye className="h-3 w-3" />
            <span>Transparency by design</span>
          </span>
        </div>
      </div>

      {error && (
        <div className="px-4 py-3 rounded-2xl text-sm font-semibold bg-rose-50 text-rose-700 border border-rose-200">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Consents */}
        <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-5 sm:p-6">
          <h2 className="font-display text-lg font-bold text-slate-900 mb-1">
            Consent Management
          </h2>
          <p className="text-xs text-slate-500 mb-5">
            Grant or revoke processing consents. Your choices sync server-side.
          </p>
          {loading ? (
            <div className="h-40 rounded-2xl animate-pulse bg-slate-100" />
          ) : (
            <div className="space-y-3">
              {CONSENT_TYPES.map((c) => (
                <div
                  key={c.key}
                  className="flex items-start justify-between p-3 rounded-2xl border border-slate-100 bg-slate-50/60"
                >
                  <div className="pr-3">
                    <p className="text-sm font-bold text-slate-800">{c.label}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{c.description}</p>
                  </div>
                  <div className="flex items-center space-x-2 shrink-0">
                    {consents[c.key] === true ? (
                      <span className="text-[10px] font-bold text-emerald-600 flex items-center space-x-0.5">
                        <Check className="h-3 w-3" /> Granted
                      </span>
                    ) : consents[c.key] === false ? (
                      <span className="text-[10px] font-bold text-slate-400 flex items-center space-x-0.5">
                        <X className="h-3 w-3" /> Revoked
                      </span>
                    ) : null}
                    <Toggle
                      checked={consents[c.key] !== false}
                      onChange={(v) => updateConsent(c.key, v)}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Retention */}
        <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-5 sm:p-6">
          <h2 className="font-display text-lg font-bold text-slate-900 mb-1">
            Data Retention & Disposal
          </h2>
          <p className="text-xs text-slate-500 mb-5">
            Automatic disposal schedules for regulated data categories.
          </p>
          <div className="space-y-3">
            {RETENTION_POLICIES.map((p, i) => {
              const Icon = p.icon;
              return (
                <div
                  key={i}
                  className="flex items-center justify-between p-3 rounded-2xl border border-slate-100 bg-slate-50/60"
                >
                  <div className="flex items-center space-x-3">
                    <span className="h-9 w-9 rounded-xl bg-violet-50 text-violet-600 flex items-center justify-center">
                      <Icon className="h-4 w-4" />
                    </span>
                    <div>
                      <p className="text-sm font-bold text-slate-800">{p.category}</p>
                      <p className="text-[10px] text-slate-400">{p.disposal_method}</p>
                    </div>
                  </div>
                  <span className="text-xs font-bold text-slate-600">
                    {(p.retention_days / 365).toFixed(0)} yr
                  </span>
                </div>
              );
            })}
          </div>

          <div className="mt-5 flex items-start space-x-2.5 p-3 rounded-2xl bg-amber-50 border border-amber-200">
            <Trash2 className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
            <p className="text-xs text-amber-800 font-medium">
              Disposal is automated and logged. Anonymized purges remove personally
              identifiable attributes after the retention window elapses.
            </p>
          </div>
        </div>
      </div>

      <div className="text-right text-[11px] text-slate-400 font-medium">
        Consents sync via /privacy/consents ({user?.full_name || 'officer'})
      </div>
    </div>
  );
};

export default PrivacyCenterPage;
