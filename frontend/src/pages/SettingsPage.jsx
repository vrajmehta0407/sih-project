import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
  Settings,
  Bell,
  Globe,
  Shield,
  SlidersHorizontal,
  UserCog,
  Languages,
  MapPin,
  Save,
  RefreshCw,
  Check,
  Moon,
  Volume2,
} from 'lucide-react';

const PREFERENCE_TABS = [
  { key: 'notification', label: 'Notifications', icon: Bell },
  { key: 'language', label: 'Language', icon: Languages },
  { key: 'privacy', label: 'Privacy', icon: Shield },
  { key: 'general', label: 'General', icon: SlidersHorizontal },
];

const LANGUAGE_OPTIONS = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिन्दी (Hindi)' },
  { code: 'ta', label: 'தமிழ் (Tamil)' },
  { code: 'te', label: 'తెలుగు (Telugu)' },
  { code: 'bn', label: 'বাংলা (Bengali)' },
  { code: 'gu', label: 'ગુજરાતી (Gujarati)' },
  { code: 'mr', label: 'मराठी (Marathi)' },
];

export const SettingsPage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('notification');
  const [preferences, setPreferences] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  const fetchPreferences = async () => {
    setLoading(true);
    try {
      const res = await api.get('/settings/preferences');
      const data = res.data?.data ?? res.data ?? [];
      const map = {};
      (Array.isArray(data) ? data : []).forEach((p) => {
        map[p.preference_key] = p.preference_value;
      });
      setPreferences(map);
    } catch (err) {
      setPreferences({});
      setError(err.response?.data?.detail || 'Could not load preferences.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPreferences();
  }, []);

  const setPref = (key, value) => {
    setPreferences((prev) => ({ ...prev, [key]: value }));
  };

  const savePreference = async (key, value = preferences[key]) => {
    setSaving(true);
    try {
      await api.put('/settings/preferences', {
        preference_key: key,
        preference_value: String(value),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save preference.');
    } finally {
      setSaving(false);
    }
  };

  const saveAll = async () => {
    setSaving(true);
    try {
      const keys = Object.keys(preferences);
      for (const key of keys) {
        await api.put('/settings/preferences', {
          preference_key: key,
          preference_value: String(preferences[key]),
        });
      }
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save settings.');
    } finally {
      setSaving(false);
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

  const SettingCard = ({ title, description, children }) => (
    <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-5 sm:p-6">
      <h3 className="font-display text-base font-bold text-slate-900">{title}</h3>
      <p className="text-xs text-slate-500 mt-1 mb-4">{description}</p>
      {children}
    </div>
  );

  const Field = () => (
    <div>
      <Toggle
        checked={preferences['notification_' + activeTab + '_enabled'] === 'true'}
        onChange={(v) => setPref('notification_' + activeTab + '_enabled', String(v))}
      />
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-mesh-vibrant rounded-3xl p-6 sm:p-8 border border-white/60 shadow-soft">
        <div className="flex items-center space-x-3 mb-2">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-violet-600 to-pink-600 flex items-center justify-center text-white shadow-tinted-blue">
            <Settings className="h-5 w-5" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-extrabold text-slate-900">
              Officer Settings
            </h1>
            <p className="text-xs text-slate-500 font-medium">
              Personalize your command center preferences
            </p>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-white/70 text-blue-700 border border-blue-200">
            <UserCog className="h-3.5 w-3.5" />
            <span>{user?.full_name || 'Officer'}</span>
          </span>
          <button
            onClick={saveAll}
            disabled={saving}
            className="inline-flex items-center space-x-1.5 text-xs font-bold px-4 py-2 rounded-full bg-gradient-to-r from-blue-600 to-violet-600 text-white shadow-tinted-blue hover:opacity-95 transition-opacity disabled:opacity-60"
          >
            {saving ? (
              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Save className="h-3.5 w-3.5" />
            )}
            <span>{saving ? 'Saving...' : 'Save All'}</span>
          </button>
          {saved && (
            <span className="inline-flex items-center space-x-1 text-xs font-bold text-emerald-600">
              <Check className="h-3.5 w-3.5" />
              <span>Saved</span>
            </span>
          )}
        </div>
      </div>

      {error && (
        <div className="px-4 py-3 rounded-2xl text-sm font-semibold bg-rose-50 text-rose-700 border border-rose-200">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Tabs */}
        <div className="lg:col-span-1">
          <nav className="flex lg:flex-col gap-1 overflow-x-auto pb-2 lg:pb-0">
            {PREFERENCE_TABS.map((tab) => {
              const Icon = tab.icon;
              const active = activeTab === tab.key;
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`inline-flex items-center space-x-2.5 px-3 py-2.5 rounded-2xl text-sm font-semibold whitespace-nowrap transition-colors ${
                    active
                      ? 'bg-gradient-to-r from-blue-600 to-violet-600 text-white shadow-tinted-blue'
                      : 'text-slate-600 hover:bg-white hover:shadow-sm'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="lg:col-span-3 space-y-4">
          {loading ? (
            <div className="h-40 rounded-3xl bg-white border border-slate-200 animate-pulse" />
          ) : (
            <>
              {(activeTab === 'notification' || activeTab === 'general') && (
                <SettingCard
                  title="Push & In-App Alerts"
                  description="Control which notifications reach your device and inbox."
                >
                  <div className="space-y-4">
                    {[
                      { key: 'email_alerts', label: 'Email alerts for inspections', icon: Bell },
                      { key: 'sms_alerts', label: 'SMS / SMS gateway updates', icon: Bell },
                      { key: 'desktop_toasts', label: 'Desktop toast popups', icon: Bell },
                      { key: 'daily_digest', label: 'Daily compliance digest', icon: Bell },
                      { key: 'critical_alerts', label: 'Critical / urgent only mode', icon: AlertTriangle },
                    ].map((opt) => (
                      <div
                        key={opt.key}
                        className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0"
                      >
                        <div className="flex items-center space-x-3">
                          <span className="h-8 w-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                            <opt.icon className="h-4 w-4" />
                          </span>
                          <span className="text-sm font-medium text-slate-700">{opt.label}</span>
                        </div>
                        <Toggle
                          checked={preferences[opt.key] === 'true'}
                          onChange={(v) => setPref(opt.key, String(v))}
                        />
                      </div>
                    ))}
                  </div>
                </SettingCard>
              )}

              {activeTab === 'language' && (
                <SettingCard
                  title="Display Language"
                  description="Interface language and content script for officers and citizens."
                >
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {LANGUAGE_OPTIONS.map((lang) => {
                      const selected = preferences['language'] === lang.code;
                      return (
                        <button
                          key={lang.code}
                          onClick={() => {
                            setPref('language', lang.code);
                            savePreference('language', lang.code);
                          }}
                          className={`flex items-center justify-between px-4 py-3 rounded-2xl border text-sm font-semibold transition-colors ${
                            selected
                              ? 'bg-gradient-to-r from-blue-600 to-violet-600 text-white border-transparent shadow-tinted-blue'
                              : 'bg-white text-slate-700 border-slate-200 hover:border-blue-300'
                          }`}
                        >
                          <span>{lang.label}</span>
                          {selected && <Check className="h-4 w-4" />}
                        </button>
                      );
                    })}
                  </div>
                </SettingCard>
              )}

              {activeTab === 'privacy' && (
                <SettingCard
                  title="Privacy & Data Controls"
                  description="Manage location, data sharing and audit preferences."
                >
                  <div className="space-y-4">
                    {[
                      { key: 'location_tracking', label: 'Enable GPS location tracking', icon: MapPin },
                      { key: 'share_analytics', label: 'Share anonymized analytics', icon: Shield },
                      { key: 'audit_distinct', label: 'Distinct audit trail entries', icon: Shield },
                      { key: 'pii_masking', label: 'Mask PII in reports', icon: Shield },
                    ].map((opt) => (
                      <div
                        key={opt.key}
                        className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0"
                      >
                        <div className="flex items-center space-x-3">
                          <span className="h-8 w-8 rounded-xl bg-violet-50 text-violet-600 flex items-center justify-center">
                            <opt.icon className="h-4 w-4" />
                          </span>
                          <span className="text-sm font-medium text-slate-700">{opt.label}</span>
                        </div>
                        <Toggle
                          checked={preferences[opt.key] === 'true'}
                          onChange={(v) => setPref(opt.key, String(v))}
                        />
                      </div>
                    ))}
                  </div>
                </SettingCard>
              )}
            </>
          )}
        </div>
      </div>

      <div className="text-right text-[11px] text-slate-400 font-medium">
        Preference keys sync via /settings/preferences
      </div>
    </div>
  );
};

export default SettingsPage;
