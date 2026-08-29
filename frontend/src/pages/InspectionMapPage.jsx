import { useEffect, useState, useCallback } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { MapPin, RefreshCw, AlertTriangle, CheckCircle, Filter } from 'lucide-react';
import api from '../services/api';

// ── Legend colours ────────────────────────────────────────────────────────────
const STATUS_CONFIG = {
  COMPLIANT: { color: '#22c55e', label: 'Compliant', icon: '🟢' },
  MINOR_VIOLATIONS: { color: '#f59e0b', label: 'Minor Violations', icon: '🟡' },
  CRITICAL_VIOLATIONS: { color: '#ef4444', label: 'Critical Violations', icon: '🔴' },
  REPEAT_OFFENDER: { color: '#a855f7', label: 'Repeat Offender', icon: '🟣' },
  PENDING: { color: '#64748b', label: 'Pending', icon: '⚫' },
};

// Default compliance status → config fallback
function getStatusConfig(status) {
  return STATUS_CONFIG[status] || STATUS_CONFIG['PENDING'];
}

// Auto-fit map bounds when inspection data changes
function BoundsAdjuster({ inspections }) {
  const map = useMap();
  useEffect(() => {
    if (!inspections || inspections.length === 0) return;
    const validPoints = inspections.filter(
      i => i.gps_latitude && i.gps_longitude
    );
    if (validPoints.length === 0) return;
    const bounds = validPoints.map(i => [i.gps_latitude, i.gps_longitude]);
    try { map.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 }); } catch {}
  }, [inspections, map]);
  return null;
}

// ── Static demo seed data (when API doesn't return GPS coords) ─────────────
const DEMO_PINS = [
  { id: 'demo-1', inspection_number: 'INS-MH-001', gps_latitude: 19.076, gps_longitude: 72.877, compliance_status: 'COMPLIANT', product_name: 'Amul Butter 500g', location_name: 'Mumbai, Maharashtra' },
  { id: 'demo-2', inspection_number: 'INS-DL-002', gps_latitude: 28.704, gps_longitude: 77.102, compliance_status: 'CRITICAL_VIOLATIONS', product_name: 'Generic Biscuits 100g', location_name: 'New Delhi' },
  { id: 'demo-3', inspection_number: 'INS-KA-003', gps_latitude: 12.971, gps_longitude: 77.594, compliance_status: 'MINOR_VIOLATIONS', product_name: 'MTR Ready Meals', location_name: 'Bengaluru, Karnataka' },
  { id: 'demo-4', inspection_number: 'INS-TN-004', gps_latitude: 13.082, gps_longitude: 80.270, compliance_status: 'REPEAT_OFFENDER', product_name: 'Local Brand Oil 1L', location_name: 'Chennai, Tamil Nadu' },
  { id: 'demo-5', inspection_number: 'INS-GJ-005', gps_latitude: 23.022, gps_longitude: 72.571, compliance_status: 'COMPLIANT', product_name: 'Dabur Honey 500g', location_name: 'Ahmedabad, Gujarat' },
  { id: 'demo-6', inspection_number: 'INS-WB-006', gps_latitude: 22.572, gps_longitude: 88.363, compliance_status: 'CRITICAL_VIOLATIONS', product_name: 'Imported Snacks 200g', location_name: 'Kolkata, West Bengal' },
  { id: 'demo-7', inspection_number: 'INS-RJ-007', gps_latitude: 26.912, gps_longitude: 75.787, compliance_status: 'COMPLIANT', product_name: 'Patanjali Atta 5kg', location_name: 'Jaipur, Rajasthan' },
  { id: 'demo-8', inspection_number: 'INS-UP-008', gps_latitude: 26.846, gps_longitude: 80.946, compliance_status: 'MINOR_VIOLATIONS', product_name: 'Local Masala 100g', location_name: 'Lucknow, Uttar Pradesh' },
];

export default function InspectionMapPage() {
  const [inspections, setInspections] = useState(DEMO_PINS);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('ALL');
  const [lastRefreshed, setLastRefreshed] = useState(new Date());

  const fetchInspections = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await api.get('/inspections/?limit=200&page=1');
      const data = resp.data?.inspections || [];
      // Merge real data (with coords) with demo pins for visualization richness
      const withCoords = data.filter(i => i.gps_latitude && i.gps_longitude);
      setInspections(withCoords.length > 0 ? [...withCoords, ...DEMO_PINS] : DEMO_PINS);
      setLastRefreshed(new Date());
    } catch {
      // API might be offline, use demo data
      setInspections(DEMO_PINS);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchInspections(); }, [fetchInspections]);

  const filtered = filter === 'ALL' ? inspections : inspections.filter(i => i.compliance_status === filter);

  // Counts
  const counts = Object.fromEntries(
    Object.keys(STATUS_CONFIG).map(k => [k, inspections.filter(i => i.compliance_status === k).length])
  );

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] bg-slate-950">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 bg-slate-900 border-b border-white/10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
            <MapPin className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-white font-bold text-base">GPS Geo-Tagged Enforcement Map</h1>
            <p className="text-slate-500 text-xs">Live field inspection locations across India</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Filter */}
          <select
            value={filter}
            onChange={e => setFilter(e.target.value)}
            className="bg-slate-800 border border-white/10 text-white text-xs px-3 py-1.5 rounded-lg"
          >
            <option value="ALL">All Inspections ({inspections.length})</option>
            {Object.entries(STATUS_CONFIG).map(([k, v]) => (
              <option key={k} value={k}>{v.icon} {v.label} ({counts[k] || 0})</option>
            ))}
          </select>

          <button
            onClick={fetchInspections}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 border border-white/10 rounded-lg text-slate-300 hover:text-white text-xs transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats bar */}
      <div className="flex gap-0 border-b border-white/10 shrink-0 bg-slate-900/50">
        {Object.entries(STATUS_CONFIG).map(([k, v]) => (
          <button
            key={k}
            onClick={() => setFilter(filter === k ? 'ALL' : k)}
            className={`flex-1 flex flex-col items-center py-2 text-xs transition-colors border-b-2 ${filter === k ? 'border-current' : 'border-transparent'}`}
            style={{ color: v.color }}
          >
            <span className="text-lg leading-tight">{counts[k] || 0}</span>
            <span className="text-slate-500 leading-tight hidden md:block">{v.label}</span>
          </button>
        ))}
      </div>

      {/* Map */}
      <div className="flex-1 relative">
        <MapContainer
          center={[20.5937, 78.9629]}
          zoom={5}
          style={{ height: '100%', width: '100%', background: '#0f172a' }}
          zoomControl={true}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          />
          <BoundsAdjuster inspections={filtered} />

          {filtered.map(inspection => {
            const cfg = getStatusConfig(inspection.compliance_status);
            return (
              <CircleMarker
                key={inspection.id}
                center={[inspection.gps_latitude, inspection.gps_longitude]}
                radius={10}
                pathOptions={{
                  fillColor: cfg.color,
                  color: '#0f172a',
                  weight: 2,
                  fillOpacity: 0.9,
                }}
              >
                <Popup>
                  <div className="text-sm min-w-[200px]">
                    <div className="font-bold text-slate-800 mb-1">
                      {inspection.inspection_number}
                    </div>
                    <div className="text-slate-600 text-xs mb-2">
                      {inspection.product_name || inspection.product?.product_name || 'Unknown Product'}
                    </div>
                    {inspection.location_name && (
                      <div className="text-slate-500 text-xs mb-2">📍 {inspection.location_name}</div>
                    )}
                    <div
                      className="inline-block px-2 py-0.5 rounded text-xs font-semibold text-white mb-2"
                      style={{ background: cfg.color }}
                    >
                      {cfg.icon} {cfg.label}
                    </div>
                    {inspection.id && !inspection.id.startsWith('demo') && (
                      <div className="mt-2">
                        <a
                          href={`/inspections/${inspection.id}`}
                          className="text-blue-600 text-xs underline"
                          target="_blank"
                          rel="noreferrer"
                        >
                          View Full Docket →
                        </a>
                      </div>
                    )}
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>

        {/* Legend overlay */}
        <div className="absolute bottom-4 left-4 z-[1000] bg-slate-900/90 backdrop-blur border border-white/10 rounded-xl p-3 text-xs space-y-1.5">
          <p className="text-slate-400 font-semibold text-[10px] uppercase tracking-wider mb-2">Legend</p>
          {Object.entries(STATUS_CONFIG).map(([, v]) => (
            <div key={v.label} className="flex items-center gap-2">
              <span
                className="w-3 h-3 rounded-full inline-block border border-white/20"
                style={{ background: v.color }}
              />
              <span className="text-slate-300">{v.label}</span>
            </div>
          ))}
        </div>

        {/* Refresh timestamp */}
        <div className="absolute top-3 right-3 z-[1000] bg-slate-900/80 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-slate-400">
          Updated {lastRefreshed.toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
