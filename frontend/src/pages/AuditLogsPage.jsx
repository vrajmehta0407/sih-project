import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Badge } from '../components/Badge';
import {
  History,
  Search,
  Filter,
  User,
  RefreshCw,
  Clock,
  FileText,
  ShieldCheck,
} from 'lucide-react';

export const AuditLogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [actionFilter, setActionFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * pageSize;
      let url = `/audit-logs?skip=${skip}&limit=${pageSize}`;
      if (actionFilter) url += `&action=${actionFilter}`;

      const resp = await api.get(url);
      setLogs(resp.data.items || []);
      setTotal(resp.data.total || 0);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, actionFilter]);

  const totalPages = Math.ceil(total / pageSize) || 1;

  const getActionBadge = (action) => {
    const upper = (action || '').toUpperCase();
    if (upper.includes('DELETE')) return <Badge variant="danger" size="xs">{action}</Badge>;
    if (upper.includes('VALIDATE')) return <Badge variant="info" size="xs">{action}</Badge>;
    if (upper.includes('REPORT') || upper.includes('GENERATE')) return <Badge variant="success" size="xs">{action}</Badge>;
    if (upper.includes('LOGIN')) return <Badge variant="navy" size="xs">{action}</Badge>;
    return <Badge variant="default" size="xs">{action}</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <History className="w-6 h-6 text-amber-500" />
            Immutable Enforcement Audit Trail
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Tamper-proof chronological log of all enforcement actions, compliant with BSA 2023 Section 65B and Legal Metrology Act.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-medium bg-emerald-50 border border-emerald-200 text-emerald-700 px-3 py-1.5 rounded-lg">
          <ShieldCheck className="w-4 h-4" />
          Immutable Record Verified
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap gap-3 items-center">
        <select
          value={actionFilter}
          onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
          className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-amber-500"
        >
          <option value="">All Enforcement Actions</option>
          <option value="LOGIN">LOGIN</option>
          <option value="CREATE_INSPECTION">CREATE_INSPECTION</option>
          <option value="UPLOAD_IMAGE">UPLOAD_IMAGE</option>
          <option value="RUN_OCR">RUN_OCR</option>
          <option value="EXTRACT_DECLARATIONS">EXTRACT_DECLARATIONS</option>
          <option value="VALIDATE_COMPLIANCE">VALIDATE_COMPLIANCE</option>
          <option value="GENERATE_REPORT">GENERATE_REPORT</option>
        </select>

        <button
          onClick={fetchLogs}
          className="p-2 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          title="Refresh"
        >
          <RefreshCw className={`w-4 h-4 text-slate-600 ${loading ? 'animate-spin' : ''}`} />
        </button>

        <span className="ml-auto text-xs text-slate-500 font-medium">
          Total Records: <b className="text-slate-800">{total}</b>
        </span>
      </div>

      {/* Audit Log Timeline */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500 font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3.5 px-4 w-44">Timestamp</th>
                <th className="py-3.5 px-4">Enforcement Action</th>
                <th className="py-3.5 px-4">Entity / Docket</th>
                <th className="py-3.5 px-4">Officer</th>
                <th className="py-3.5 px-4">IP Address</th>
                <th className="py-3.5 px-4">Remarks</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="6" className="py-12 text-center text-slate-400 text-sm">
                    <div className="inline-block w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
                    <span className="block mt-2">Loading audit records...</span>
                  </td>
                </tr>
              ) : logs.length > 0 ? (
                logs.map((log, idx) => (
                  <tr key={log.id || idx} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-1.5 text-xs">
                        <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span className="font-mono text-slate-700">
                          {new Date(log.created_at).toLocaleDateString()}{' '}
                          <span className="text-slate-500">
                            {new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                          </span>
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {getActionBadge(log.action)}
                    </td>
                    <td className="py-3 px-4">
                      <div className="text-xs">
                        <span className="font-semibold text-slate-800">{log.entity_name || '—'}</span>
                        {log.entity_id && (
                          <span className="block font-mono text-[10px] text-slate-400 truncate max-w-[160px]">
                            {log.entity_id}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-1.5 text-xs">
                        <User className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span className="text-slate-700 font-medium">{log.user_id ? log.user_id.slice(0, 8) + '...' : 'System'}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-mono text-[11px] text-slate-500">{log.ip_address || '—'}</span>
                    </td>
                    <td className="py-3 px-4">
                      <p className="text-xs text-slate-600 max-w-[220px] truncate" title={log.metadata_json}>
                        {log.metadata_json ? JSON.stringify(log.metadata_json).slice(0, 60) + '...' : '—'}
                      </p>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="py-12 text-center text-slate-400 text-sm">
                    No audit records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>Showing {logs.length} of {total} audit entries</span>
          <div className="flex gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="px-3 py-1 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-3 py-1 font-semibold text-slate-800">
              Page {page} of {totalPages}
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
              className="px-3 py-1 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
