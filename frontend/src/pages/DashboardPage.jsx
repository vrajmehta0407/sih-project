import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import {
  Scale,
  ShieldCheck,
  AlertTriangle,
  FileText,
  TrendingUp,
  MapPin,
  Users,
  ArrowUpRight,
  RefreshCw,
  PlusCircle,
  Building2,
  AlertOctagon,
  IndianRupee,
  Sparkles,
  Award,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { GlassCard, AnimatedCounter, StatusBadge, StaggeredList, StaggeredItem, SkeletonCard } from '../design-system';

export const DashboardPage = () => {
  const [metrics, setMetrics] = useState(null);
  const [trends, setTrends] = useState([]);
  const [topViolations, setTopViolations] = useState([]);
  const [heatmap, setHeatmap] = useState([]);
  const [repeatOffenders, setRepeatOffenders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedState, setSelectedState] = useState('');

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [mRes, tRes, vRes, hRes, rRes] = await Promise.all([
        api.get(`/dashboard/metrics${selectedState ? `?state=${selectedState}` : ''}`),
        api.get('/dashboard/trends?days=14'),
        api.get('/dashboard/top-violations?limit=5'),
        api.get('/dashboard/jurisdiction-heatmap'),
        api.get('/dashboard/repeat-offenders?limit=6'),
      ]);

      setMetrics(mRes.data);
      setTrends(tRes.data);
      setTopViolations(vRes.data);
      setHeatmap(hRes.data);
      setRepeatOffenders(rRes.data);
    } catch (err) {
      console.error('Error fetching dashboard metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [selectedState]);

  const severityPieData = metrics
    ? [
        { name: 'Critical', value: metrics.violations_summary.critical, color: '#EF4444' },
        { name: 'Major', value: metrics.violations_summary.major, color: '#F59E0B' },
        { name: 'Minor', value: metrics.violations_summary.minor, color: '#3B82F6' },
      ].filter((d) => d.value > 0)
    : [];

  return (
    <div className="space-y-8 pb-12">
      {/* Page Header Bar */}
      <GlassCard variant="default" className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-primary-600 mb-1">
              <span className="h-2 w-2 rounded-full bg-primary-600 animate-pulse" />
              <span>National Compliance Intelligence & Enforcement Hub</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold font-display text-slate-900">
              Executive Metrology Dashboard
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              Real-time statutory monitoring under Legal Metrology Act, 2009 & Packaged Commodities Rules, 2011.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="text-xs bg-slate-50 border border-slate-200 rounded-2xl px-3.5 py-2.5 text-slate-700 font-semibold focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Jurisdictions (National)</option>
              <option value="Maharashtra">Maharashtra (Western Zone)</option>
              <option value="Delhi">Delhi NCT (Northern Zone)</option>
              <option value="Gujarat">Gujarat (Western Zone)</option>
              <option value="Karnataka">Karnataka (Southern Zone)</option>
              <option value="Tamil Nadu">Tamil Nadu (Southern Zone)</option>
            </select>

            <button
              onClick={fetchDashboardData}
              title="Refresh Data"
              className="p-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-2xl transition-colors shadow-sm"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>

            <Link
              to="/inspections/new"
              className="inline-flex items-center space-x-2 px-5 py-2.5 text-xs font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:opacity-95 text-white rounded-2xl shadow-tinted-blue transition-transform hover:scale-105 active:scale-95"
            >
              <PlusCircle className="w-4 h-4" />
              <span>New Inspection</span>
            </Link>
          </div>
        </div>
      </GlassCard>

      {/* KPI Cards Grid */}
      <StaggeredList className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Compliance Rate Card */}
        <StaggeredItem>
          <GlassCard variant="emerald" className="p-6 h-full flex flex-col justify-between">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-bold text-emerald-700 uppercase tracking-wider">
                  Compliance Rate
                </p>
                <h3 className="text-3xl sm:text-4xl font-extrabold text-slate-900 font-display mt-2">
                  <AnimatedCounter
                    value={metrics ? metrics.compliance_rate_percentage : 0}
                    suffix="%"
                  />
                </h3>
              </div>
              <div className="p-3 bg-emerald-100/70 rounded-2xl text-emerald-700 shadow-sm">
                <ShieldCheck className="w-6 h-6 stroke-[2.2]" />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2 text-xs">
              <span className="font-bold text-emerald-700">
                {metrics?.compliance_breakdown.compliant || 0} Compliant
              </span>
              <span className="text-slate-300">•</span>
              <span className="text-rose-600 font-medium">
                {metrics?.compliance_breakdown.non_compliant || 0} Breaches
              </span>
            </div>
          </GlassCard>
        </StaggeredItem>

        {/* Total Inspections Card */}
        <StaggeredItem>
          <GlassCard variant="blue" className="p-6 h-full flex flex-col justify-between">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-bold text-blue-700 uppercase tracking-wider">
                  Total Scanned Dockets
                </p>
                <h3 className="text-3xl sm:text-4xl font-extrabold text-slate-900 font-display mt-2">
                  <AnimatedCounter
                    value={metrics ? metrics.total_inspections : 0}
                  />
                </h3>
              </div>
              <div className="p-3 bg-blue-100/70 rounded-2xl text-blue-700 shadow-sm">
                <FileText className="w-6 h-6 stroke-[2.2]" />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2 text-xs text-slate-500">
              <span className="font-bold text-slate-700">
                {metrics?.status_breakdown.completed || 0} Completed
              </span>
              <span className="text-slate-300">•</span>
              <span>{metrics?.status_breakdown.validated || 0} Validated</span>
            </div>
          </GlassCard>
        </StaggeredItem>

        {/* Total Violations Card */}
        <StaggeredItem>
          <GlassCard variant="rose" className="p-6 h-full flex flex-col justify-between">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-bold text-rose-700 uppercase tracking-wider">
                  Statutory Violations
                </p>
                <h3 className="text-3xl sm:text-4xl font-extrabold text-rose-600 font-display mt-2">
                  <AnimatedCounter
                    value={metrics ? metrics.violations_summary.total_violations : 0}
                  />
                </h3>
              </div>
              <div className="p-3 bg-rose-100/70 rounded-2xl text-rose-700 shadow-sm">
                <AlertTriangle className="w-6 h-6 stroke-[2.2]" />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2 text-xs">
              <span className="font-bold text-rose-600">
                {metrics?.violations_summary.critical || 0} Critical
              </span>
              <span className="text-slate-300">•</span>
              <span className="text-amber-600 font-semibold">
                {metrics?.violations_summary.major || 0} Major
              </span>
            </div>
          </GlassCard>
        </StaggeredItem>

        {/* Repeat Offender Recidivism Card */}
        <StaggeredItem>
          <GlassCard variant="amber" className="p-6 h-full flex flex-col justify-between">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-bold text-amber-700 uppercase tracking-wider">
                  Repeat Offender Alerts
                </p>
                <h3 className="text-3xl sm:text-4xl font-extrabold text-amber-600 font-display mt-2">
                  <AnimatedCounter
                    value={metrics ? metrics.violations_summary.repeat_offender_alerts : 0}
                  />
                </h3>
              </div>
              <div className="p-3 bg-amber-100/70 rounded-2xl text-amber-700 shadow-sm">
                <AlertOctagon className="w-6 h-6 stroke-[2.2]" />
              </div>
            </div>
            <div className="mt-4 text-xs font-bold text-amber-800">
              Section 36(2) 2x Penalty Escalation Active
            </div>
          </GlassCard>
        </StaggeredItem>
      </StaggeredList>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Compliance Trends Chart */}
        <GlassCard variant="default" className="lg:col-span-2 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold font-display text-slate-900">
                14-Day Compliance & Non-Compliance Velocity
              </h3>
              <p className="text-xs text-slate-500">
                Real-time statutory trends captured across active inspection zones
              </p>
            </div>
            <span className="px-3 py-1 text-xs font-bold rounded-full bg-blue-50 text-blue-700 border border-blue-200">
              Live Stream
            </span>
          </div>

          <div className="h-72 w-full pt-2">
            {trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="compGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="nonCompGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#94a3b8" />
                  <YAxis tick={{ fontSize: 11 }} stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                  <Area type="monotone" dataKey="compliant_count" name="Compliant" stroke="#10B981" fillOpacity={1} fill="url(#compGrad)" strokeWidth={2.5} />
                  <Area type="monotone" dataKey="non_compliant_count" name="Non-Compliant" stroke="#EF4444" fillOpacity={1} fill="url(#nonCompGrad)" strokeWidth={2.5} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                No time-series data captured for selected period.
              </div>
            )}
          </div>
        </GlassCard>

        {/* Severity Distribution Donut */}
        <GlassCard variant="default" className="p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold font-display text-slate-900">
              Violations by Severity
            </h3>
            <p className="text-xs text-slate-500">Statutory infraction distribution</p>
          </div>

          <div className="h-56 w-full my-auto">
            {severityPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {severityPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                No active violations recorded.
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-slate-100 flex justify-around text-center text-xs">
            <div>
              <span className="block font-bold text-rose-600 text-sm">
                {metrics?.violations_summary.critical || 0}
              </span>
              <span className="text-slate-400">Critical</span>
            </div>
            <div>
              <span className="block font-bold text-amber-600 text-sm">
                {metrics?.violations_summary.major || 0}
              </span>
              <span className="text-slate-400">Major</span>
            </div>
            <div>
              <span className="block font-bold text-blue-600 text-sm">
                {metrics?.violations_summary.minor || 0}
              </span>
              <span className="text-slate-400">Minor</span>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Lower Tables Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Top Breached Statutory Provisions */}
        <GlassCard variant="default" className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold font-display text-slate-900">
                Top Breached Statutory Provisions
              </h3>
              <p className="text-xs text-slate-500">Legal Metrology (Packaged Commodities) Rules, 2011</p>
            </div>
            <Link to="/rules" className="text-xs font-bold text-primary-600 hover:text-primary-800 flex items-center gap-1">
              <span>View Rulebook</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {topViolations.length > 0 ? (
              topViolations.map((v, idx) => (
                <div key={idx} className="p-3.5 bg-slate-50/80 rounded-2xl border border-slate-100 flex items-center justify-between hover:bg-white hover:border-slate-200 transition-all shadow-sm">
                  <div className="space-y-1 max-w-[75%]">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-slate-900">{v.section_violated}</span>
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full uppercase ${
                        v.severity === 'critical' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-800'
                      }`}>
                        {v.severity}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 truncate">{v.violation_title}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-base font-bold font-display text-slate-900">{v.violation_count}</span>
                    <span className="block text-[10px] text-slate-400 font-semibold">{v.percentage_of_total}% share</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-400 py-6 text-center">No violations reported in this period.</p>
            )}
          </div>
        </GlassCard>

        {/* Repeat Offender Recidivism Leaderboard */}
        <GlassCard variant="default" className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold font-display text-slate-900">
                Repeat Offender Recidivism Leaderboard
              </h3>
              <p className="text-xs text-slate-500">Manufacturers with repeated non-compliance</p>
            </div>
            <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
              Section 36(2) Priority
            </span>
          </div>

          <div className="divide-y divide-slate-100">
            {repeatOffenders.length > 0 ? (
              repeatOffenders.map((r, idx) => (
                <div key={idx} className="py-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-rose-50 border border-rose-200 flex items-center justify-center font-bold text-rose-700 text-xs">
                      #{idx + 1}
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-slate-900">{r.manufacturer_name}</h4>
                      <p className="text-xs text-slate-500">Brand: {r.brand_name} · Last Offence: {r.last_inspection_date}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-700">
                      {r.total_violations} Violations
                    </span>
                    <span className="block text-[10px] text-slate-400 mt-0.5 font-medium">{r.inspections_count} audits</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-400 py-6 text-center">No repeat offending entities identified.</p>
            )}
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
export default DashboardPage;
