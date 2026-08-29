import React, { useState, useEffect } from 'react';
import {
  Radar,
  Navigation,
  AlertCircle,
  MapPin,
  Clock,
  Banknote,
  Send,
  ShieldAlert,
  ChevronRight,
  TrendingUp,
  CheckCircle2,
} from 'lucide-react';
import api from '../services/api';

export default function PredictiveDispatchPage() {
  const [hotspots, setHotspots] = useState([]);
  const [loadingHotspots, setLoadingHotspots] = useState(true);

  const [selectedState, setSelectedState] = useState('Maharashtra');
  const [selectedDistrict, setSelectedDistrict] = useState('Mumbai');
  const [maxTargets, setMaxTargets] = useState(5);
  const [teamLead, setTeamLead] = useState('inspector.mumbai@legalmetrology.gov.in');

  const [dispatching, setDispatching] = useState(false);
  const [dispatchedRoute, setDispatchedRoute] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHotspots();
  }, []);

  const fetchHotspots = async () => {
    try {
      setLoadingHotspots(true);
      const resp = await api.get('/dashboard/predictive-hotspots');
      setHotspots(resp.data.hotspots || []);
    } catch (err) {
      console.error('Failed to load predictive hotspots', err);
    } finally {
      setLoadingHotspots(false);
    }
  };

  const handleDispatchRoute = async (e) => {
    e.preventDefault();
    setDispatching(true);
    setError('');
    try {
      const resp = await api.post('/dashboard/dispatch-raid-route', {
        state: selectedState,
        district: selectedDistrict,
        team_lead_email: teamLead,
        max_targets: parseInt(maxTargets, 10),
        focus_category: 'ALL',
      });
      setDispatchedRoute(resp.data);
    } catch (err) {
      setError('Unable to dispatch raid route. Ensure you have active officer authorization.');
    } finally {
      setDispatching(false);
    }
  };

  const getMviColor = (mvi) => {
    if (mvi >= 85) return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
    if (mvi >= 70) return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <Radar className="w-3.5 h-3.5" />
            AI Intelligence & Predictive Enforcement
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Market Vulnerability Index & Tactical Raid Planner
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Fusing citizen complaints, recidivism frequency, and forensic sticker tampering to dispatch optimal inspection routes.
          </p>
        </div>
      </div>

      {/* Predictive Hotspot Clusters Grid */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-amber-400" />
          High-Risk Commercial Clusters (AI Predicted)
        </h2>

        {loadingHotspots ? (
          <div className="text-slate-400 text-sm py-4">Evaluating national market vulnerability index...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {hotspots.map((h) => (
              <div
                key={h.cluster_id}
                onClick={() => {
                  setSelectedState(h.state);
                  setSelectedDistrict(h.district);
                }}
                className={`p-4 rounded-xl border cursor-pointer transition-all hover:scale-[1.02] bg-slate-900 ${
                  selectedDistrict === h.district ? 'border-rose-500 shadow-lg shadow-rose-500/10' : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500 font-mono">{h.cluster_id}</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-bold border ${getMviColor(h.market_vulnerability_index)}`}>
                    MVI: {h.market_vulnerability_index}
                  </span>
                </div>
                <h3 className="text-white font-bold text-sm mt-2">{h.cluster_name}</h3>
                <p className="text-xs text-slate-400 mt-1">{h.district}, {h.state}</p>
                <div className="mt-3 pt-3 border-t border-slate-800 flex justify-between text-xs text-slate-400">
                  <span>{h.repeat_offenders_count} High-Risk Outlets</span>
                  <span className="text-rose-400 font-semibold">{h.risk_level}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Dispatch Control Form & Generated Route */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Dispatch Parameters */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Navigation className="w-4 h-4 text-emerald-400" />
            Dispatch Parameters
          </h2>

          <form onSubmit={handleDispatchRoute} className="space-y-4 text-sm">
            <div>
              <label className="text-slate-400 text-xs font-semibold block mb-1">State Jurisdiction</label>
              <input
                type="text"
                value={selectedState}
                onChange={(e) => setSelectedState(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-white"
                required
              />
            </div>

            <div>
              <label className="text-slate-400 text-xs font-semibold block mb-1">District / Market Hub</label>
              <input
                type="text"
                value={selectedDistrict}
                onChange={(e) => setSelectedDistrict(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-white"
                required
              />
            </div>

            <div>
              <label className="text-slate-400 text-xs font-semibold block mb-1">Lead Field Inspector</label>
              <input
                type="email"
                value={teamLead}
                onChange={(e) => setTeamLead(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-white"
                required
              />
            </div>

            <div>
              <label className="text-slate-400 text-xs font-semibold block mb-1">Target Establishments ({maxTargets} Stops)</label>
              <input
                type="range"
                min="2"
                max="10"
                value={maxTargets}
                onChange={(e) => setMaxTargets(e.target.value)}
                className="w-full accent-emerald-500"
              />
            </div>

            <button
              type="submit"
              disabled={dispatching}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20 disabled:opacity-50"
            >
              {dispatching ? (
                <>Planning Optimal Itinerary...</>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Generate & Dispatch Patrol Route
                </>
              )}
            </button>
          </form>

          {error && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Right: Dispatched Tactical Itinerary */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-base font-bold text-white">Tactical Inspection Route</h2>
              <p className="text-xs text-slate-400 mt-0.5">Optimized stop sequence ordered by vulnerability & fine recovery</p>
            </div>
            {dispatchedRoute && (
              <span className="px-3 py-1 bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 rounded-full text-xs font-mono font-bold">
                {dispatchedRoute.dispatch_code}
              </span>
            )}
          </div>

          {!dispatchedRoute ? (
            <div className="py-16 text-center text-slate-500 text-sm">
              <Navigation className="w-8 h-8 text-slate-600 mx-auto mb-2 opacity-50" />
              Select a cluster on the left and click "Generate & Dispatch Patrol Route" to calculate the tactical field itinerary.
            </div>
          ) : (
            <div className="space-y-6">
              {/* Route Summary Metrics */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-center">
                  <Clock className="w-4 h-4 text-sky-400 mx-auto mb-1" />
                  <div className="text-lg font-bold text-white">{dispatchedRoute.estimated_duration_hours} hrs</div>
                  <div className="text-[11px] text-slate-400">Estimated Duration</div>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-center">
                  <Banknote className="w-4 h-4 text-emerald-400 mx-auto mb-1" />
                  <div className="text-lg font-bold text-white">₹{(dispatchedRoute.estimated_fine_recovery_inr / 1000).toFixed(1)}k</div>
                  <div className="text-[11px] text-slate-400">Est. Sec 48 Recovery</div>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-center">
                  <MapPin className="w-4 h-4 text-purple-400 mx-auto mb-1" />
                  <div className="text-lg font-bold text-white">{dispatchedRoute.total_stops} Targets</div>
                  <div className="text-[11px] text-slate-400">Establishments</div>
                </div>
              </div>

              {/* Ordered Stop Timeline */}
              <div className="space-y-3">
                {dispatchedRoute.targets.map((t) => (
                  <div
                    key={t.stop_sequence}
                    className="flex items-center gap-4 bg-slate-950 border border-slate-800 rounded-xl p-3.5 hover:border-slate-700 transition-colors"
                  >
                    <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-bold flex items-center justify-center shrink-0 text-xs">
                      #{t.stop_sequence}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-white font-bold text-sm truncate">{t.retailer_name}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          t.priority_level === 'URGENT' ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'
                        }`}>
                          {t.priority_level}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5 truncate">{t.location_address}</p>
                    </div>

                    <div className="text-right shrink-0">
                      <div className="text-xs font-mono font-bold text-slate-300">
                        ₹{t.predicted_compounding_recovery_inr.toLocaleString()}
                      </div>
                      <div className="text-[10px] text-amber-400 font-semibold">{t.primary_infraction_risk}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
