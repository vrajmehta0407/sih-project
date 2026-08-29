import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { Badge } from '../components/Badge';
import {
  ClipboardList,
  Search,
  Filter,
  PlusCircle,
  Eye,
  Calendar,
  MapPin,
  Building,
  AlertCircle,
  FileCheck,
} from 'lucide-react';

export const InspectionsListPage = () => {
  const [inspections, setInspections] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [statusFilter, setStatusFilter] = useState('');
  const [complianceFilter, setComplianceFilter] = useState('');
  const [searchDistrict, setSearchDistrict] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchInspections = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * pageSize;
      let url = `/inspections/?skip=${skip}&limit=${pageSize}`;
      if (statusFilter) url += `&status=${statusFilter}`;
      if (complianceFilter) url += `&compliance_status=${complianceFilter}`;
      if (searchDistrict) url += `&district=${searchDistrict}`;

      const resp = await api.get(url);
      setInspections(resp.data.items || []);
      setTotal(resp.data.total || 0);
    } catch (err) {
      console.error('Error loading inspections:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInspections();
  }, [page, statusFilter, complianceFilter, searchDistrict]);

  const totalPages = Math.ceil(total / pageSize) || 1;

  const getComplianceBadge = (status) => {
    switch (status) {
      case 'compliant':
        return <Badge variant="success">COMPLIANT</Badge>;
      case 'non_compliant':
        return <Badge variant="danger">NON-COMPLIANT</Badge>;
      case 'review_required':
        return <Badge variant="warning">REVIEW REQUIRED</Badge>;
      default:
        return <Badge variant="default">PENDING</Badge>;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge variant="navy" size="xs">REPORT ISSUED</Badge>;
      case 'validated':
        return <Badge variant="info" size="xs">VALIDATED</Badge>;
      case 'extracted':
        return <Badge variant="info" size="xs">EXTRACTED</Badge>;
      case 'ocr_completed':
        return <Badge variant="default" size="xs">OCR DONE</Badge>;
      default:
        return <Badge variant="default" size="xs">{status.toUpperCase()}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <ClipboardList className="w-6 h-6 text-amber-500" />
            Field Inspection Records
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage, verify, and review scanned pre-packaged commodities and statutory dockets.
          </p>
        </div>
        <Link
          to="/inspections/new"
          className="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-xl shadow-md transition-all"
        >
          <PlusCircle className="w-4 h-4" />
          Create New Inspection
        </Link>
      </div>

      {/* Filters Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap gap-3 items-center">
        <div className="flex-1 min-w-[200px] relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Filter by district (e.g. Mumbai, Pune)..."
            value={searchDistrict}
            onChange={(e) => setSearchDistrict(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>

        <select
          value={complianceFilter}
          onChange={(e) => setComplianceFilter(e.target.value)}
          className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-amber-500"
        >
          <option value="">All Compliance Outcomes</option>
          <option value="compliant">Compliant</option>
          <option value="non_compliant">Non-Compliant</option>
          <option value="review_required">Review Required</option>
          <option value="pending">Pending</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-amber-500"
        >
          <option value="">All Pipeline Stages</option>
          <option value="pending">Pending</option>
          <option value="preprocessed">Preprocessed</option>
          <option value="ocr_completed">OCR Completed</option>
          <option value="extracted">Extracted</option>
          <option value="validated">Validated</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500 font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3.5 px-4">Inspection #</th>
                <th className="py-3.5 px-4">Establishment / Store</th>
                <th className="py-3.5 px-4">Location</th>
                <th className="py-3.5 px-4 text-center">Pipeline Stage</th>
                <th className="py-3.5 px-4 text-center">Compliance Outcome</th>
                <th className="py-3.5 px-4">Date / Time</th>
                <th className="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-400 text-sm">
                    <div className="inline-block w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
                    <span className="block mt-2">Loading inspection dockets...</span>
                  </td>
                </tr>
              ) : inspections.length > 0 ? (
                inspections.map((insp) => (
                  <tr key={insp.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-900 text-xs">
                      {insp.inspection_number}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-900">{insp.store_name || 'Retail Establishment'}</div>
                      <div className="text-xs text-slate-500 truncate max-w-[200px]">{insp.store_address || 'Address unrecorded'}</div>
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-600">
                      <div className="flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                        {insp.district}, {insp.state}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      {getStatusBadge(insp.status)}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      {getComplianceBadge(insp.compliance_status)}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-500">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5 text-slate-400" />
                        {new Date(insp.created_at).toLocaleDateString()} {new Date(insp.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        to={`/inspections/${insp.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold bg-slate-100 hover:bg-slate-900 hover:text-white rounded-lg transition-all"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        Open Studio
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-400 text-sm">
                    No inspection records found matching your filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>Showing {inspections.length} of {total} records</span>
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
