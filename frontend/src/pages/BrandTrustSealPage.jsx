import React, { useState, useEffect } from 'react';
import {
  Award,
  Search,
  CheckCircle,
  ShieldCheck,
  AlertTriangle,
  FileCheck,
  Building2,
  TrendingUp,
  ExternalLink,
  Sparkles,
} from 'lucide-react';
import api from '../services/api';

const FEATURED_BRANDS = ['Amul', 'Dabur', 'Patanjali', 'Tata Tea', 'Britannia'];

export default function BrandTrustSealPage() {
  const [searchTerm, setSearchTerm] = useState('Amul');
  const [loading, setLoading] = useState(false);
  const [scorecard, setScorecard] = useState(null);
  const [error, setError] = useState('');

  const fetchScorecard = async (brand) => {
    if (!brand || !brand.trim()) return;
    setLoading(true);
    setError('');
    try {
      const resp = await api.get(`/registry/brands/${encodeURIComponent(brand.trim())}/scorecard`);
      setScorecard(resp.data);
    } catch (err) {
      setError('Unable to retrieve brand scorecard. Please check connection or brand name.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScorecard('Amul');
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchScorecard(searchTerm);
  };

  const getTierColor = (tier) => {
    switch (tier) {
      case 'PLATINUM_GREEN':
        return { bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-400', badge: 'bg-emerald-500' };
      case 'GOLD_COMPLIANT':
        return { bg: 'bg-amber-500/10', border: 'border-amber-500/30', text: 'text-amber-400', badge: 'bg-amber-500' };
      case 'AMBER_WATCHLIST':
        return { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400', badge: 'bg-orange-500' };
      case 'RED_RECIDIVIST':
        return { bg: 'bg-rose-500/10', border: 'border-rose-500/30', text: 'text-rose-400', badge: 'bg-rose-500' };
      default:
        return { bg: 'bg-slate-800/40', border: 'border-slate-700', text: 'text-slate-300', badge: 'bg-slate-600' };
    }
  };

  const colors = scorecard ? getTierColor(scorecard.trust_tier) : getTierColor('');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold tracking-widest uppercase">
            <Award className="w-3.5 h-3.5" />
            National Metrology Trust Gateway
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Brand Compliance Scorecard & Trust Seal
          </h1>
          <p className="text-slate-400 text-sm max-w-xl mx-auto">
            Verify official Legal Metrology packaging compliance ratings, verified model registrations, and national trust tiers for FMCG manufacturers.
          </p>
        </div>

        {/* Search & Quick Select */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <form onSubmit={handleSearch} className="flex gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-500 absolute left-4 top-3.5" />
              <input
                type="text"
                placeholder="Search brand or manufacturer name (e.g. Amul, Patanjali, Dabur)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-11 pr-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm rounded-xl transition-all disabled:opacity-50"
            >
              {loading ? 'Evaluating...' : 'Verify Brand'}
            </button>
          </form>

          {/* Quick Select Tags */}
          <div className="flex items-center gap-2 flex-wrap pt-2 border-t border-slate-800 text-xs">
            <span className="text-slate-500">Popular Brands:</span>
            {FEATURED_BRANDS.map((b) => (
              <button
                key={b}
                onClick={() => {
                  setSearchTerm(b);
                  fetchScorecard(b);
                }}
                className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition-colors"
              >
                {b}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl p-4 text-sm flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Scorecard Display */}
        {scorecard && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl space-y-6">
            {/* Top Brand Banner */}
            <div className={`p-6 sm:p-8 ${colors.bg} border-b ${colors.border} flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4`}>
              <div>
                <div className="text-xs text-slate-400 uppercase font-semibold">Legal Metrology Compliance Docket</div>
                <h2 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">{scorecard.brand_name}</h2>
                <p className="text-xs text-slate-400 mt-1">{scorecard.risk_assessment_summary}</p>
              </div>

              <div className="text-right">
                <div className="text-3xl sm:text-4xl font-extrabold text-white">{scorecard.compliance_rate}%</div>
                <div className={`text-xs font-bold mt-1 px-3 py-1 rounded-full text-slate-950 ${colors.badge} inline-block shadow-md`}>
                  {scorecard.trust_seal_badge}
                </div>
              </div>
            </div>

            {/* Metric KPI Cards */}
            <div className="p-6 sm:p-8 grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-center">
                <ShieldCheck className="w-5 h-5 text-emerald-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">{scorecard.compliant_inspections}</div>
                <div className="text-xs text-slate-400 mt-1">Clean Inspections</div>
              </div>

              <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-center">
                <AlertTriangle className="w-5 h-5 text-amber-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">{scorecard.violation_inspections}</div>
                <div className="text-xs text-slate-400 mt-1">Infractions Logged</div>
              </div>

              <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-center">
                <FileCheck className="w-5 h-5 text-blue-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">{scorecard.active_registered_models}</div>
                <div className="text-xs text-slate-400 mt-1">Registered Models</div>
              </div>

              <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-center">
                <Building2 className="w-5 h-5 text-purple-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">{scorecard.total_inspections}</div>
                <div className="text-xs text-slate-400 mt-1">Total Market Audits</div>
              </div>
            </div>

            {/* Legal Status Footer */}
            <div className="bg-slate-950 px-6 sm:px-8 py-4 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-3">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Government Authenticated • Rule 27 LM (Packaged Commodities) Rules, 2011</span>
              </div>
              <div>Last Evaluated: {new Date(scorecard.last_evaluated_at).toLocaleString()}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
