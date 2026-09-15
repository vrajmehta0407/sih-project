import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
  BarChart3,
  Download,
  FileText,
  Database,
  Filter,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  FileJson,
  FileSpreadsheet,
  Clock,
  ExternalLink,
} from 'lucide-react';

export const ReportingHubPage = () => {
  const { user } = useAuth();
  const [options, setOptions] = useState({ job_types: [], formats: [] });
  const [jobType, setJobType] = useState('');
  const [format, setFormat] = useState('csv');
  const [filters, setFilters] = useState({});
  const [filterKey, setFilterKey] = useState('');
  const [filterValue, setFilterValue] = useState('');
  const [includeColumns, setIncludeColumns] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchOptions = async () => {
    setLoading(true);
    try {
      const res = await api.get('/export/options');
      const data = res.data?.data ?? {};
      setOptions({
        job_types: data.job_types ?? [],
        formats: data.formats ?? [],
      });
      if (!jobType && (data.job_types ?? []).length) {
        setJobType(data.job_types[0]);
      }
    } catch (err) {
      setOptions({ job_types: [], formats: ['csv', 'json'] });
      if (!jobType) setJobType('inspections');
      setError(err.response?.data?.detail || 'Could not load export options.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOptions();
  }, []);

  const addFilter = () => {
    if (!filterKey.trim()) return;
    setFilters((prev) => ({
      ...prev,
      [filterKey.trim()]: filterValue.trim(),
    }));
    setFilterKey('');
    setFilterValue('');
  };

  const removeFilter = (key) => {
    setFilters((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
  };

  const generateExport = async () => {
    setGenerating(true);
    setError('');
    setResult(null);
    try {
      const payload = {
        job_type: jobType,
        format,
        include_system_columns: includeColumns,
      };
      if (Object.keys(filters).length) {
        payload.filters = filters;
      }
      const res = await api.post('/export/exports', payload);
      const data = res.data?.data ?? res.data ?? res;
      setResult(data);
      setHistory((prev) => [
        {
          job_type: data.job_type ?? jobType,
          format: data.format ?? format,
          status: data.status ?? 'submitted',
          file_name: data.file_name,
          record_count: data.record_count,
          created_at: data.created_at,
          job_id: data.job_id,
        },
        ...prev,
      ]);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not generate export.');
    } finally {
      setGenerating(false);
    }
  };

  const formatLabel = (f) =>
    f === 'csv' ? (
      <FileSpreadsheet className="h-4 w-4" />
    ) : (
      <FileJson className="h-4 w-4" />
    );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-mesh-vibrant rounded-3xl p-6 sm:p-8 border border-white/60 shadow-soft">
        <div className="flex items-center space-x-3 mb-3">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-violet-600 to-pink-600 flex items-center justify-center text-white shadow-tinted-blue">
            <BarChart3 className="h-5 w-5" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-extrabold text-slate-900">
              Reporting Hub
            </h1>
            <p className="text-xs text-slate-500 font-medium">
              One-click CSV / JSON compliance data exports
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {(options.job_types ?? []).slice(0, 6).map((t) => (
            <span
              key={t}
              className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-white/70 text-violet-700 border border-violet-200"
            >
              <Database className="h-3 w-3" />
              <span>{t}</span>
            </span>
          ))}
        </div>
      </div>

      {error && (
        <div className="px-4 py-3 rounded-2xl text-sm font-semibold bg-rose-50 text-rose-700 border border-rose-200 flex items-start space-x-2">
          <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Builder */}
        <div className="lg:col-span-2 rounded-3xl bg-white border border-slate-200 shadow-sm p-5 sm:p-6">
          <h2 className="font-display text-lg font-bold text-slate-900 mb-1">
            New Export Job
          </h2>
          <p className="text-xs text-slate-500 mb-5">
            Select a dataset and format to generate a server-side compliance dump.
          </p>

          <div className="space-y-5">
            {/* Job type */}
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1.5 uppercase tracking-wide">
                Dataset
              </label>
              <select
                value={jobType}
                onChange={(e) => setJobType(e.target.value)}
                className="w-full px-3 py-2.5 rounded-2xl bg-white border border-slate-200 shadow-sm text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              >
                {loading ? (
                  <option>Loading...</option>
                ) : (
                  (options.job_types ?? []).map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))
                )}
              </select>
            </div>

            {/* Format */}
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1.5 uppercase tracking-wide">
                Format
              </label>
              <div className="flex rounded-2xl bg-slate-100 border border-slate-200 p-1">
                {(options.formats ?? ['csv', 'json']).map((f) => (
                  <button
                    key={f}
                    onClick={() => setFormat(f)}
                    disabled={f === 'xlsx'}
                    className={`flex-1 inline-flex items-center justify-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-colors ${
                      format === f
                        ? 'bg-gradient-to-r from-blue-600 to-violet-600 text-white shadow-sm'
                        : 'text-slate-500 hover:text-slate-700'
                    } disabled:opacity-40 disabled:cursor-not-allowed`}
                  >
                    {formatLabel(f)}
                    <span className="capitalize">{f}</span>
                    {f === 'xlsx' && <span>(soon)</span>}
                  </button>
                ))}
              </div>
            </div>

            {/* Filters */}
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1.5 uppercase tracking-wide">
                Filters (optional)
              </label>
              <div className="flex flex-col sm:flex-row gap-2">
                <input
                  value={filterKey}
                  onChange={(e) => setFilterKey(e.target.value)}
                  placeholder="e.g. state"
                  className="flex-1 px-3 py-2 rounded-2xl bg-white border border-slate-200 shadow-sm text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
                />
                <input
                  value={filterValue}
                  onChange={(e) => setFilterValue(e.target.value)}
                  placeholder="e.g. Maharashtra"
                  className="flex-1 px-3 py-2 rounded-2xl bg-white border border-slate-200 shadow-sm text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
                />
                <button
                  onClick={addFilter}
                  className="inline-flex items-center justify-center space-x-1.5 px-4 py-2 rounded-2xl bg-blue-50 text-blue-700 border border-blue-200 text-xs font-bold hover:bg-blue-100 transition-colors"
                >
                  <Filter className="h-3.5 w-3.5" />
                  <span>Add</span>
                </button>
              </div>
              {Object.keys(filters).length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {Object.entries(filters).map(([k, v]) => (
                    <span
                      key={k}
                      className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-violet-50 text-violet-700 border border-violet-200"
                    >
                      <span>{k}: {v}</span>
                      <button
                        onClick={() => removeFilter(k)}
                        className="text-violet-400 hover:text-violet-700"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Include system columns */}
            <label className="flex items-center space-x-2.5">
              <input
                type="checkbox"
                checked={includeColumns}
                onChange={(e) => setIncludeColumns(e.target.checked)}
                className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-slate-700">
                Include system columns
              </span>
            </label>

            <button
              onClick={generateExport}
              disabled={generating || !jobType}
              className="w-full inline-flex items-center justify-center space-x-2 px-4 py-3 rounded-2xl bg-gradient-to-r from-blue-600 via-violet-600 to-pink-600 text-white font-bold text-sm shadow-tinted-blue hover:opacity-95 transition-opacity disabled:opacity-60"
            >
              {generating ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              <span>{generating ? 'Generating...' : 'Generate Export'}</span>
            </button>
          </div>
        </div>

        {/* Result + History */}
        <div className="lg:col-span-1 space-y-4">
          {result && (
            <div className="rounded-3xl bg-emerald-50 border border-emerald-200 p-5">
              <div className="flex items-center space-x-2 mb-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                <h3 className="font-display text-base font-bold text-emerald-800">
                  Export Submitted
                </h3>
              </div>
              <dl className="space-y-1.5 text-sm">
                <div className="flex justify-between">
                  <dt className="text-emerald-700/70">Job ID</dt>
                  <dd className="font-mono text-xs text-emerald-800">{result.job_id || '—'}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-emerald-700/70">Status</dt>
                  <dd className="font-bold text-emerald-800">{result.status || 'submitted'}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-emerald-700/70">Records</dt>
                  <dd className="font-bold text-emerald-800">{result.record_count ?? '—'}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-emerald-700/70">File</dt>
                  <dd className="font-mono text-xs text-emerald-800">{result.file_name || '—'}</dd>
                </div>
              </dl>
            </div>
          )}

          <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-5">
            <h3 className="font-display text-base font-bold text-slate-900 mb-3 flex items-center space-x-2">
              <Clock className="h-4 w-4 text-violet-500" />
              <span>Recent Jobs</span>
            </h3>
            {history.length === 0 ? (
              <p className="text-xs text-slate-400">No exports generated this session.</p>
            ) : (
              <div className="space-y-2">
                {history.slice(0, 8).map((h, i) => (
                  <div
                    key={`${h.job_id || 'job'}-${i}`}
                    className="flex items-center justify-between px-3 py-2 rounded-xl bg-slate-50 border border-slate-100"
                  >
                    <div className="flex items-center space-x-2 min-w-0">
                      {formatLabel(h.format)}
                      <div className="min-w-0">
                        <p className="text-xs font-bold text-slate-700 capitalize truncate">
                          {h.job_type}
                        </p>
                        <p className="text-[10px] text-slate-400">
                          {h.record_count ?? '—'} rows ·{' '}
                          {h.created_at
                            ? new Date(h.created_at).toLocaleTimeString()
                            : 'just now'}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                        h.status === 'completed'
                          ? 'bg-emerald-50 text-emerald-700'
                          : 'bg-amber-50 text-amber-700'
                      }`}
                    >
                      {h.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="text-right text-[11px] text-slate-400 font-medium">
        Exports run server-side; download path returned in response
      </div>
    </div>
  );
};

export default ReportingHubPage;
