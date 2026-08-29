import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { Badge } from '../components/Badge';
import {
  FileText,
  Camera,
  Layers,
  FileSearch,
  ShieldAlert,
  ShieldCheck,
  Download,
  QrCode,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Building,
  MapPin,
  Calendar,
  Sparkles,
  ExternalLink,
  ChevronRight,
  Gavel,
  DollarSign,
  Scale,
  Check,
} from 'lucide-react';
import { BoundingBoxOverlay } from '../components/BoundingBoxOverlay';

export const InspectionDetailPage = () => {
  const { id } = useParams();
  const [inspection, setInspection] = useState(null);
  const [ocrData, setOcrData] = useState(null);
  const [declarations, setDeclarations] = useState(null);
  const [violations, setViolations] = useState([]);
  const [report, setReport] = useState(null);
  const [activeTab, setActiveTab] = useState('declarations'); // 'preprocessing' | 'ocr' | 'declarations' | 'violations' | 'report' | 'adjudication'

  // Explainability & Bounding Box State
  const [highlightText, setHighlightedText] = useState('');
  const [selectedSide, setSelectedSide] = useState('front');

  // Adjudication Modal State
  const [adjudicationModalOpen, setAdjudicationModalOpen] = useState(false);
  const [adjAction, setAdjAction] = useState('COMPOUND_OFFENCE');
  const [adjAmount, setAdjAmount] = useState(25000);
  const [adjReceipt, setAdjReceipt] = useState('');
  const [adjOrderNo, setAdjOrderNo] = useState('');
  const [adjCourt, setAdjCourt] = useState('');
  const [adjNotes, setAdjNotes] = useState('');

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const isMatch = (target, val) => {
    if (!target || !val) return false;
    const cleanT = String(target).toLowerCase().replace(/[^a-z0-9]/g, '');
    const cleanV = String(val).toLowerCase().replace(/[^a-z0-9]/g, '');
    return cleanT.includes(cleanV) || cleanV.includes(cleanT);
  };

  // Normalize API declarations to the field names the JSX expects
  const normalizeDeclarations = (raw) => {
    if (!raw) return null;
    const mrp = raw.mrp || {};
    const nq = raw.net_quantity || {};
    const mfr = raw.manufacturer_details || {};
    const bn = raw.batch_number || {};
    const dates = raw.dates || {};
    const summary = raw.summary || {};
    return {
      mrp: {
        value: mrp.value,
        confidence: mrp.confidence ?? 0.85,
        inclusive_of_taxes: mrp.inclusive_taxes_declared ?? mrp.inclusive_of_taxes ?? false,
        raw_text: mrp.raw ?? mrp.raw_text ?? '',
      },
      net_quantity: {
        value: nq.value,
        confidence: nq.confidence ?? 0.85,
        standard_unit: nq.unit ?? nq.standard_unit ?? '',
        is_standard_unit: nq.is_standard_unit ?? true,
        raw_text: nq.raw ?? nq.raw_text ?? '',
      },
      dates: {
        mfg_date_raw: dates.mfg_date ?? dates.mfg_date_raw ?? dates.manufacturing_date ?? '',
        exp_date_raw: dates.exp_date ?? dates.exp_date_raw ?? dates.expiry_date ?? dates.best_before ?? '',
      },
      batch: {
        batch_number: bn.value ?? bn.batch_number ?? '',
      },
      entity: {
        manufacturer_name: mfr.manufacturer_name ?? mfr.name ?? '',
        packer_name: mfr.packer_name ?? '',
        manufacturer_address: mfr.manufacturer_address ?? mfr.address ?? '',
        packer_address: mfr.packer_address ?? '',
      },
      consumer_care: raw.consumer_care || {},
      country_of_origin: raw.country_of_origin || {},
      missing_mandatory_fields: summary.missing_mandatory_fields ?? [],
      declared_fields_count: summary.declared_fields_count ?? 0,
      overall_confidence: summary.overall_confidence ?? 0,
    };
  };

  const fetchInspectionDetails = async () => {
    setLoading(true);
    try {
      const resp = await api.get(`/inspections/${id}`);
      // Normalize inspection: ensure preprocessed_images and raw_images always exist
      const insp = resp.data;
      if (!insp.preprocessed_images) insp.preprocessed_images = [];
      if (!insp.raw_images) insp.raw_images = [];
      setInspection(insp);

      // Fetch additional pipeline data in parallel
      const [oRes, dRes, vRes] = await Promise.allSettled([
        api.get(`/inspections/${id}/ocr`),
        api.get(`/inspections/${id}/declarations`),
        api.get(`/inspections/${id}/violations`),
      ]);

      if (oRes.status === 'fulfilled') setOcrData(oRes.value.data);
      if (dRes.status === 'fulfilled') {
        setDeclarations(normalizeDeclarations(dRes.value.data.declarations));
      }
      if (vRes.status === 'fulfilled') setViolations(vRes.value.data);
    } catch (err) {
      console.error('Error fetching inspection:', err);
      setError('Failed to load inspection record.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInspectionDetails();
  }, [id]);

  // Pipeline Step Triggers
  const handleRunOCR = async () => {
    setActionLoading(true);
    setError('');
    setSuccessMsg('');
    try {
      const resp = await api.post(`/inspections/${id}/ocr`);
      setOcrData(resp.data);
      setSuccessMsg('Dual OCR Consensus executed successfully.');
      await fetchInspectionDetails();
      setActiveTab('ocr');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to execute Dual OCR.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleExtractDeclarations = async () => {
    setActionLoading(true);
    setError('');
    setSuccessMsg('');
    try {
      const resp = await api.post(`/inspections/${id}/extract-declarations`);
      setDeclarations(resp.data.declarations);
      setSuccessMsg('Rule 6 Statutory Declarations extracted.');
      await fetchInspectionDetails();
      setActiveTab('declarations');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to extract statutory declarations.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleValidateCompliance = async () => {
    setActionLoading(true);
    setError('');
    setSuccessMsg('');
    try {
      const resp = await api.post(`/inspections/${id}/validate`);
      setViolations(resp.data.violations);
      setSuccessMsg('Statutory compliance validation completed.');
      await fetchInspectionDetails();
      setActiveTab('violations');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to validate statutory compliance.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    setActionLoading(true);
    setError('');
    setSuccessMsg('');
    try {
      const resp = await api.post(`/inspections/${id}/report`);
      setReport(resp.data);
      setSuccessMsg('Court-admissible PDF Report & QR Token generated.');
      await fetchInspectionDetails();
      setActiveTab('report');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate PDF report.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleAdjudicate = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    setError('');
    setSuccessMsg('');
    try {
      const payload = {
        action: adjAction,
        compounding_amount: adjAction === 'COMPOUND_OFFENCE' ? Number(adjAmount) : null,
        receipt_number: adjReceipt || null,
        order_number: adjOrderNo || null,
        court_jurisdiction: adjCourt || null,
        adjudication_notes: adjNotes || null,
      };
      await api.post(`/inspections/${id}/adjudicate`, payload);
      setSuccessMsg('Statutory adjudication action recorded successfully.');
      setAdjudicationModalOpen(false);
      await fetchInspectionDetails();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to record adjudication action.');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center">
        <div className="inline-block w-8 h-8 border-3 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm text-slate-500 mt-2">Loading Inspection Studio...</p>
      </div>
    );
  }

  if (!inspection) {
    return (
      <div className="py-16 text-center text-slate-600">
        <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto mb-2" />
        <h2 className="text-lg font-bold">Inspection Record Not Found</h2>
        <Link to="/inspections" className="text-sm text-amber-600 hover:underline mt-2 inline-block">
          Return to Inspections List
        </Link>
      </div>
    );
  }

  const pipelineStages = [
    { key: 'preprocessed', label: '1. OpenCV Preprocessing', done: !!inspection.preprocessed_images?.length },
    { key: 'ocr', label: '2. Dual OCR Consensus', done: inspection.status !== 'pending' && inspection.status !== 'preprocessed' },
    { key: 'declarations', label: '3. Rule 6 Extractor', done: !!declarations || ['extracted', 'validated', 'completed'].includes(inspection.status) },
    { key: 'violations', label: '4. Statutory Validation', done: ['validated', 'completed'].includes(inspection.status) },
    { key: 'report', label: '5. Court PDF & QR Stamped', done: inspection.status === 'completed' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner with Inspection Meta & Status */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-slate-500">
            <span>INSPECTION DOCKET</span>
            <span>•</span>
            <span className="font-bold text-slate-900">{inspection.inspection_number}</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mt-0.5">
            {inspection.store_name || 'Retail Market Commodity Inspection'}
          </h1>
          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 mt-1">
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              {inspection.district}, {inspection.state}
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              {new Date(inspection.created_at).toLocaleDateString()} {new Date(inspection.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Badge
            variant={
              inspection.compliance_status === 'compliant'
                ? 'success'
                : inspection.compliance_status === 'non_compliant'
                ? 'danger'
                : inspection.compliance_status === 'review_required'
                ? 'warning'
                : 'default'
            }
            size="md"
          >
            {inspection.compliance_status ? inspection.compliance_status.toUpperCase() : 'PENDING EVALUATION'}
          </Badge>

          {/* Quick Action Button based on state */}
          {['pending', 'preprocessed'].includes(inspection.status) && (
            <button
              onClick={handleRunOCR}
              disabled={actionLoading}
              className="px-4 py-2 text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-amber-400 rounded-xl shadow transition-all flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Run Dual OCR
            </button>
          )}

          {inspection.status === 'ocr_completed' && (
            <button
              onClick={handleExtractDeclarations}
              disabled={actionLoading}
              className="px-4 py-2 text-xs font-semibold bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-xl shadow transition-all flex items-center gap-1.5 font-bold"
            >
              <FileSearch className="w-3.5 h-3.5" />
              Extract Declarations
            </button>
          )}

          {inspection.status === 'extracted' && (
            <button
              onClick={handleValidateCompliance}
              disabled={actionLoading}
              className="px-4 py-2 text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white rounded-xl shadow transition-all flex items-center gap-1.5"
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              Validate Statutory Compliance
            </button>
          )}

          {inspection.status === 'validated' && (
            <button
              onClick={handleGenerateReport}
              disabled={actionLoading}
              className="px-4 py-2 text-xs font-semibold bg-emerald-700 hover:bg-emerald-600 text-white rounded-xl shadow transition-all flex items-center gap-1.5"
            >
              <FileText className="w-3.5 h-3.5" />
              Issue Statutory Notice & PDF
            </button>
          )}

          {/* Adjudication Workflow Action */}
          <button
            onClick={() => setAdjudicationModalOpen(true)}
            className="px-4 py-2 text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-xl shadow transition-all flex items-center gap-1.5"
          >
            <Gavel className="w-3.5 h-3.5" />
            Legal Adjudication & Compounding
          </button>
        </div>
      </div>

      {/* Pipeline Progress Indicator */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs">
          {pipelineStages.map((stg, idx) => (
            <div
              key={stg.key}
              className={`p-2.5 rounded-lg flex items-center gap-2 border ${
                stg.done
                  ? 'bg-emerald-50/60 border-emerald-200 text-emerald-800'
                  : 'bg-slate-50 border-slate-200 text-slate-400'
              }`}
            >
              <CheckCircle2 className={`w-4 h-4 shrink-0 ${stg.done ? 'text-emerald-600' : 'text-slate-300'}`} />
              <span className="font-semibold truncate">{stg.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Notifications */}
      {successMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-sm flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}
      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Studio Tabs */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Tab Headers */}
        <div className="flex border-b border-slate-200 bg-slate-50/80 overflow-x-auto">
          {[
            { id: 'declarations', label: 'Statutory Declarations Matrix', icon: FileSearch, count: declarations ? declarations.declared_fields_count : 0 },
            { id: 'violations', label: 'Violations Docket', icon: ShieldAlert, count: violations.length },
            { id: 'ocr', label: 'Dual OCR Consensus', icon: Layers },
            { id: 'adjudication', label: 'Adjudication & Settlement', icon: Gavel, badge: inspection.adjudication_status || 'pending' },
            { id: 'preprocessing', label: 'OpenCV Quality Studio', icon: Camera, count: inspection.preprocessed_images?.length },
            { id: 'report', label: 'Court PDF & QR Chain', icon: QrCode },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-5 py-3.5 text-xs font-bold whitespace-nowrap flex items-center gap-2 border-b-2 transition-all ${
                  isActive
                    ? 'border-amber-500 text-slate-900 bg-white shadow-sm'
                    : 'border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-100'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-amber-500' : 'text-slate-400'}`} />
                {tab.label}
                {tab.count !== undefined && (
                  <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono ${isActive ? 'bg-amber-100 text-amber-800' : 'bg-slate-200 text-slate-600'}`}>
                    {tab.count}
                  </span>
                )}
                {tab.badge && (
                  <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-bold ${
                    tab.badge === 'compounded' ? 'bg-emerald-100 text-emerald-800' :
                    tab.badge === 'court_referred' ? 'bg-rose-100 text-rose-800' :
                    tab.badge === 'notice_issued' ? 'bg-amber-100 text-amber-800' :
                    'bg-slate-200 text-slate-600'
                  }`}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Tab Content Body */}
        <div className="p-6">
          {/* ── TAB 1: STATUTORY DECLARATIONS MATRIX ────────────────────── */}
          {activeTab === 'declarations' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Mandatory Declarations Matrix (Rule 6, Legal Metrology PCR 2011)
                  </h3>
                  <p className="text-xs text-slate-500">
                    Confidence metrics and structured values extracted from packaging OCR consensus.
                  </p>
                </div>
                <button
                  onClick={handleExtractDeclarations}
                  disabled={actionLoading}
                  className="px-3.5 py-1.5 text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg flex items-center gap-1.5"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${actionLoading ? 'animate-spin' : ''}`} />
                  Re-Extract Declarations
                </button>
              </div>

              {declarations ? (
                <div className="space-y-6">
                  {/* Missing Fields Banner */}
                  {declarations.missing_mandatory_fields?.length > 0 && (
                    <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl">
                      <div className="flex items-center gap-2 text-rose-800 font-bold text-xs">
                        <AlertTriangle className="w-4 h-4 text-rose-600" />
                        Missing Mandatory Statutory Declarations Detected ({declarations.missing_mandatory_fields.length}):
                      </div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {declarations.missing_mandatory_fields.map((mf, i) => (
                          <Badge key={i} variant="danger" size="xs">
                            {mf}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Interactive Spatial Explainability Visualizer */}
                  {inspection.preprocessed_images?.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                          <Layers className="w-4 h-4 text-amber-500" />
                          Spatial OCR Explainability Visualizer (Hover field below to locate bounding box)
                        </h4>
                        {/* Side selector */}
                        {inspection.preprocessed_images.length > 1 && (
                          <div className="flex gap-1.5">
                            {inspection.preprocessed_images.map((img) => (
                              <button
                                key={img.side}
                                onClick={() => setSelectedSide(img.side)}
                                className={`px-2.5 py-1 rounded-lg text-xs font-semibold uppercase ${
                                  selectedSide === img.side
                                    ? 'bg-slate-900 text-amber-400 font-bold'
                                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                                }`}
                              >
                                {img.side}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>

                      <BoundingBoxOverlay
                        imageUrl={
                          inspection.preprocessed_images?.find((img) => img.side === selectedSide)?.url ||
                          inspection.preprocessed_images?.[0]?.url ||
                          inspection.raw_images?.[0]?.url
                        }
                        boxes={
                          ocrData?.sides?.[selectedSide]?.consensus_boxes ||
                          ocrData?.sides?.['front']?.consensus_boxes ||
                          []
                        }
                        highlightText={highlightText}
                        selectedSide={selectedSide}
                        onSelectBox={(box) => setHighlightedText(box.text)}
                      />
                    </div>
                  )}

                  {/* Declarations Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {/* MRP Card */}
                    <div
                      className={`p-4 rounded-xl border transition-all cursor-pointer space-y-2 ${
                        highlightText && isMatch(highlightText, declarations.mrp.value)
                          ? 'border-amber-500 bg-amber-50/50 shadow-md ring-2 ring-amber-400'
                          : 'border-slate-200 bg-slate-50/50 hover:border-slate-300'
                      }`}
                      onMouseEnter={() => setHighlightedText(String(declarations.mrp.value || declarations.mrp.raw_text || 'mrp'))}
                      onMouseLeave={() => setHighlightedText('')}
                    >
                      <div className="flex justify-between items-start">
                        <span className="text-[11px] font-bold text-slate-500 uppercase">1. Maximum Retail Price (Rule 6(1)(e))</span>
                        <Badge variant={declarations.mrp.value ? 'success' : 'danger'} size="xs">
                          {declarations.mrp.value ? `${Math.round(declarations.mrp.confidence * 100)}% Conf` : 'MISSING'}
                        </Badge>
                      </div>
                      <div className="text-xl font-bold text-slate-900">
                        {declarations.mrp.value ? `₹ ${declarations.mrp.value.toFixed(2)}` : 'Not Declared'}
                      </div>
                      <div className="text-xs flex items-center gap-1">
                        <span className="text-slate-500">Taxes Phrase:</span>
                        {declarations.mrp.inclusive_of_taxes ? (
                          <span className="text-emerald-600 font-semibold flex items-center gap-0.5">
                            <CheckCircle2 className="w-3 h-3" /> Declared (incl. all taxes)
                          </span>
                        ) : (
                          <span className="text-rose-600 font-semibold">Missing 'incl. of taxes'</span>
                        )}
                      </div>
                      {declarations.mrp.raw_text && (
                        <p className="text-[10px] font-mono text-slate-400 truncate">Raw: "{declarations.mrp.raw_text}"</p>
                      )}
                    </div>

                    {/* Net Quantity Card */}
                    <div
                      className={`p-4 rounded-xl border transition-all cursor-pointer space-y-2 ${
                        highlightText && isMatch(highlightText, declarations.net_quantity.value)
                          ? 'border-amber-500 bg-amber-50/50 shadow-md ring-2 ring-amber-400'
                          : 'border-slate-200 bg-slate-50/50 hover:border-slate-300'
                      }`}
                      onMouseEnter={() => setHighlightedText(String(declarations.net_quantity.value || 'quantity'))}
                      onMouseLeave={() => setHighlightedText('')}
                    >
                      <div className="flex justify-between items-start">
                        <span className="text-[11px] font-bold text-slate-500 uppercase">2. Net Quantity (Rule 6(1)(c) & Rule 11)</span>
                        <Badge variant={declarations.net_quantity.value ? 'success' : 'danger'} size="xs">
                          {declarations.net_quantity.value ? `${Math.round(declarations.net_quantity.confidence * 100)}% Conf` : 'MISSING'}
                        </Badge>
                      </div>
                      <div className="text-xl font-bold text-slate-900">
                        {declarations.net_quantity.value
                          ? `${declarations.net_quantity.value} ${declarations.net_quantity.standard_unit}`
                          : 'Not Declared'}
                      </div>
                      <div className="text-xs flex items-center gap-1">
                        <span className="text-slate-500">Unit Standard:</span>
                        {declarations.net_quantity.is_standard_unit ? (
                          <span className="text-emerald-600 font-semibold">Standard Metric Unit</span>
                        ) : (
                          <span className="text-amber-600 font-semibold">Non-Standard Unit</span>
                        )}
                      </div>
                      {declarations.net_quantity.raw_text && (
                        <p className="text-[10px] font-mono text-slate-400 truncate">Raw: "{declarations.net_quantity.raw_text}"</p>
                      )}
                    </div>

                    {/* Dates Card */}
                    <div
                      className={`p-4 rounded-xl border transition-all cursor-pointer space-y-2 ${
                        highlightText && isMatch(highlightText, declarations.dates.mfg_date_raw)
                          ? 'border-amber-500 bg-amber-50/50 shadow-md ring-2 ring-amber-400'
                          : 'border-slate-200 bg-slate-50/50 hover:border-slate-300'
                      }`}
                      onMouseEnter={() => setHighlightedText(declarations.dates.mfg_date_raw || 'mfg')}
                      onMouseLeave={() => setHighlightedText('')}
                    >
                      <div className="flex justify-between items-start">
                        <span className="text-[11px] font-bold text-slate-500 uppercase">3. Mfg & Expiry Dates (Rule 6(1)(d))</span>
                        <Badge variant={declarations.dates.mfg_date_raw ? 'success' : 'danger'} size="xs">
                          {declarations.dates.mfg_date_raw ? 'DECLARED' : 'MISSING'}
                        </Badge>
                      </div>
                      <div className="text-sm font-semibold text-slate-900 space-y-1">
                        <div>Mfg Date: <span className="font-mono text-slate-700">{declarations.dates.mfg_date_raw || 'N/A'}</span></div>
                        <div>Exp Date: <span className="font-mono text-slate-700">{declarations.dates.exp_date_raw || 'N/A'}</span></div>
                      </div>
                    </div>

                    {/* Batch Number */}
                    <div
                      className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2 cursor-pointer hover:border-slate-300"
                      onMouseEnter={() => setHighlightedText(declarations.batch.batch_number || 'batch')}
                      onMouseLeave={() => setHighlightedText('')}
                    >
                      <div className="flex justify-between items-start">
                        <span className="text-[11px] font-bold text-slate-500 uppercase">4. Batch / Lot Code</span>
                        <Badge variant={declarations.batch.batch_number ? 'success' : 'default'} size="xs">
                          {declarations.batch.batch_number ? 'DECLARED' : 'MISSING'}
                        </Badge>
                      </div>
                      <div className="text-base font-mono font-bold text-slate-900">
                        {declarations.batch.batch_number || 'N/A'}
                      </div>
                    </div>

                    {/* Manufacturer Details */}
                    <div
                      className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2 lg:col-span-2 cursor-pointer hover:border-slate-300"
                      onMouseEnter={() => setHighlightedText(declarations.entity.manufacturer_name || 'manufacturer')}
                      onMouseLeave={() => setHighlightedText('')}
                    >
                      <div className="flex justify-between items-start">
                        <span className="text-[11px] font-bold text-slate-500 uppercase">5. Manufacturer / Packer (Rule 6(1)(a))</span>
                        <Badge variant={declarations.entity.manufacturer_name ? 'success' : 'danger'} size="xs">
                          {declarations.entity.manufacturer_name ? 'DECLARED' : 'MISSING'}
                        </Badge>
                      </div>
                      <div className="text-sm font-bold text-slate-900">
                        {declarations.entity.manufacturer_name || declarations.entity.packer_name || 'Not Declared'}
                      </div>
                      <p className="text-xs text-slate-600">
                        {declarations.entity.manufacturer_address || declarations.entity.packer_address || 'Address missing'}
                      </p>
                    </div>

                    {/* Consumer Care */}
                    <div
                      className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2 lg:col-span-2 cursor-pointer hover:border-slate-300"
                      onMouseEnter={() => setHighlightedText(declarations.consumer_care.phone || declarations.consumer_care.email || 'consumer')}
                      onMouseLeave={() => setHighlightedText('')}
                    >
                      <div className="flex justify-between items-start">
                        <span className="text-[11px] font-bold text-slate-500 uppercase">6. Consumer Grievance Redressal (Rule 6(1)(f))</span>
                        <Badge variant={declarations.consumer_care.phone || declarations.consumer_care.email ? 'success' : 'danger'} size="xs">
                          {declarations.consumer_care.phone || declarations.consumer_care.email ? 'DECLARED' : 'MISSING'}
                        </Badge>
                      </div>
                      <div className="text-xs space-y-1 text-slate-700">
                        <div><b>Toll-Free / Phone:</b> {declarations.consumer_care.phone || 'N/A'}</div>
                        <div><b>Email:</b> {declarations.consumer_care.email || 'N/A'}</div>
                      </div>
                    </div>

                    {/* Country of Origin */}
                    <div
                      className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2 cursor-pointer hover:border-slate-300"
                      onMouseEnter={() => setHighlightedText(declarations.country_of_origin.country || 'india')}
                      onMouseLeave={() => setHighlightedText('')}
                    >
                      <div className="flex justify-between items-start">
                        <span className="text-[11px] font-bold text-slate-500 uppercase">7. Country of Origin (Rule 6(1)(g))</span>
                        <Badge variant={declarations.country_of_origin.country ? 'success' : 'default'} size="xs">
                          {declarations.country_of_origin.country || 'DOMESTIC / UNKNOWN'}
                        </Badge>
                      </div>
                      <div className="text-base font-bold text-slate-900">
                        {declarations.country_of_origin.country || 'INDIA / DOMESTIC'}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center bg-slate-50 rounded-xl border border-dashed border-slate-300">
                  <FileSearch className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-slate-700">Declarations not yet parsed</p>
                  <p className="text-xs text-slate-500 mt-1 mb-4">Run the Rule 6 extractor on the OCR consensus text.</p>
                  <button
                    onClick={handleExtractDeclarations}
                    disabled={actionLoading}
                    className="px-4 py-2 bg-amber-500 text-slate-950 rounded-xl font-bold text-xs shadow hover:bg-amber-400"
                  >
                    Extract Declarations Now
                  </button>
                </div>
              )}
            </div>
          )}

          {/* ── TAB 2: VIOLATIONS DOCKET ───────────────────────────────── */}
          {activeTab === 'violations' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Statutory Infractions & Violations Docket
                  </h3>
                  <p className="text-xs text-slate-500">
                    Statutory grounding under Legal Metrology Act, 2009 (Sec 18, 25, 36) & PCR 2011.
                  </p>
                </div>
                <button
                  onClick={handleValidateCompliance}
                  disabled={actionLoading}
                  className="px-3.5 py-1.5 text-xs font-semibold bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 rounded-lg flex items-center gap-1.5"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${actionLoading ? 'animate-spin' : ''}`} />
                  Re-Validate Compliance
                </button>
              </div>

              {violations.length > 0 ? (
                <div className="space-y-4">
                  {violations.map((v, idx) => (
                    <div
                      key={idx}
                      className="p-5 rounded-2xl border border-rose-200 bg-rose-50/30 flex flex-col md:flex-row md:items-center justify-between gap-4"
                    >
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                          <Badge variant={v.severity === 'critical' ? 'danger' : 'warning'} size="xs">
                            {v.severity.toUpperCase()}
                          </Badge>
                          <span className="font-mono text-xs font-bold text-slate-900">
                            {v.section_violated}
                          </span>
                          {v.is_repeat_offender_alert && (
                            <Badge variant="danger" size="xs">
                              REPEAT OFFENDER (SEC 36(2))
                            </Badge>
                          )}
                        </div>
                        <h4 className="text-sm font-bold text-slate-900">{v.violation_title}</h4>
                        <p className="text-xs text-slate-600">{v.violation_description}</p>
                        <p className="text-[11px] text-slate-500">
                          <b>Statute:</b> {v.statute_title} • <b>Penalty Provision:</b> {v.penalty_provision}
                        </p>
                      </div>

                      <div className="bg-white p-3 rounded-xl border border-slate-200 text-right shrink-0">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block">Estimated Penalty</span>
                        <span className="text-sm font-extrabold text-rose-700">{v.estimated_fine || 'Sec 36 Penalty'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : inspection.status === 'validated' || inspection.status === 'completed' ? (
                <div className="py-12 text-center bg-emerald-50 rounded-2xl border border-emerald-200 p-8">
                  <ShieldCheck className="w-12 h-12 text-emerald-600 mx-auto mb-2" />
                  <h3 className="text-base font-bold text-emerald-900">100% Statutory Compliance Certified</h3>
                  <p className="text-xs text-emerald-700 mt-1 max-w-md mx-auto">
                    The pre-packaged commodity satisfies all mandatory disclosure standards under Rule 6 of the Legal Metrology (Packaged Commodities) Rules, 2011.
                  </p>
                </div>
              ) : (
                <div className="py-12 text-center bg-slate-50 rounded-xl border border-dashed border-slate-300">
                  <ShieldAlert className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-slate-700">Compliance validation not executed yet</p>
                  <button
                    onClick={handleValidateCompliance}
                    disabled={actionLoading}
                    className="mt-3 px-4 py-2 bg-rose-600 text-white rounded-xl font-bold text-xs shadow hover:bg-rose-500"
                  >
                    Run Statutory Validation Engine
                  </button>
                </div>
              )}
            </div>
          )}

          {/* ── TAB 3: DUAL OCR CONSENSUS ──────────────────────────────── */}
          {activeTab === 'ocr' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Dual OCR Engine Consensus (PaddleOCR + Tesseract)
                  </h3>
                  <p className="text-xs text-slate-500">
                    Spatial IoU box alignment and Levenshtein token arbitration.
                  </p>
                </div>
                <button
                  onClick={handleRunOCR}
                  disabled={actionLoading}
                  className="px-3.5 py-1.5 text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg flex items-center gap-1.5"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${actionLoading ? 'animate-spin' : ''}`} />
                  Re-Execute Dual OCR
                </button>
              </div>

              {ocrData ? (
                <div className="space-y-6">
                  {/* Consensus Summary Banner */}
                  <div className="p-4 bg-slate-900 text-white rounded-2xl flex flex-wrap items-center justify-between gap-4">
                    <div>
                      <span className="text-xs text-slate-400 block font-mono">ARBITRATION OUTCOME</span>
                      <span className="text-base font-bold text-amber-400">
                        {ocrData.consensus_summary.has_disagreement ? 'OCR Disagreement Flagged (Review Advised)' : 'Consensus Established (High Confidence)'}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-xs font-mono">
                      <div>Paddle Tokens: <b>{ocrData.paddle_total_boxes}</b></div>
                      <div>Tesseract Tokens: <b>{ocrData.tesseract_total_boxes}</b></div>
                      <div>Avg Similarity: <b>{ocrData.consensus_summary.avg_token_similarity}</b></div>
                    </div>
                  </div>

                  {/* Side-by-side Raw OCR View */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-slate-700 uppercase">PaddleOCR (RapidOCR ONNX)</span>
                        <Badge variant="navy" size="xs">Primary Engine</Badge>
                      </div>
                      <pre className="p-3 bg-white rounded-lg border border-slate-200 text-xs font-mono text-slate-800 whitespace-pre-wrap max-h-60 overflow-y-auto">
                        {ocrData.paddle_raw_text || 'No text recognized'}
                      </pre>
                    </div>

                    <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-slate-700 uppercase">Tesseract OCR Engine</span>
                        <Badge variant="info" size="xs">Secondary Engine</Badge>
                      </div>
                      <pre className="p-3 bg-white rounded-lg border border-slate-200 text-xs font-mono text-slate-800 whitespace-pre-wrap max-h-60 overflow-y-auto">
                        {ocrData.tesseract_raw_text || 'No text recognized'}
                      </pre>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center bg-slate-50 rounded-xl border border-dashed border-slate-300">
                  <Layers className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-slate-700">Dual OCR not executed yet</p>
                  <button
                    onClick={handleRunOCR}
                    disabled={actionLoading}
                    className="mt-3 px-4 py-2 bg-slate-900 text-amber-400 rounded-xl font-bold text-xs shadow hover:bg-slate-800"
                  >
                    Run Dual OCR Consensus Now
                  </button>
                </div>
              )}
            </div>
          )}

          {/* ── TAB 4: STATUTORY ADJUDICATION & COMPOUNDING WORKFLOW ─────── */}
          {activeTab === 'adjudication' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Statutory Adjudication & Offence Compounding (Section 48/49 LM Act 2009)
                  </h3>
                  <p className="text-xs text-slate-500">
                    Track case disposal status, compounding orders, treasury challan receipts, or judicial court referrals.
                  </p>
                </div>
                <button
                  onClick={() => setAdjudicationModalOpen(true)}
                  className="px-4 py-2 text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-xl shadow flex items-center gap-1.5"
                >
                  <Gavel className="w-3.5 h-3.5" />
                  Record Legal Action / Settle
                </button>
              </div>

              {/* Status Overview Card */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-1">
                  <span className="text-[11px] font-bold text-slate-500 uppercase">Case Status</span>
                  <div className="text-lg font-bold text-slate-900 uppercase">
                    {inspection.adjudication_status || 'PENDING'}
                  </div>
                  <p className="text-xs text-slate-500">
                    {inspection.adjudicated_at ? `Updated on ${new Date(inspection.adjudicated_at).toLocaleDateString()}` : 'Awaiting Officer Action'}
                  </p>
                </div>

                <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-1">
                  <span className="text-[11px] font-bold text-slate-500 uppercase">Compounding Fine (Sec 48)</span>
                  <div className="text-lg font-bold text-emerald-700">
                    {inspection.compounding_amount ? `₹ ${inspection.compounding_amount.toLocaleString()}` : 'Not Compounded'}
                  </div>
                  <p className="text-xs text-slate-500">
                    Challan: <span className="font-mono">{inspection.compounding_receipt_number || 'N/A'}</span>
                  </p>
                </div>

                <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-1">
                  <span className="text-[11px] font-bold text-slate-500 uppercase">Order / Court Reference</span>
                  <div className="text-sm font-bold font-mono text-slate-800 truncate">
                    {inspection.compounding_order_number || inspection.court_jurisdiction || 'No Order Assigned'}
                  </div>
                  <p className="text-xs text-slate-500">
                    {inspection.court_jurisdiction ? 'Designated Court Jurisdiction' : 'Executive Order'}
                  </p>
                </div>
              </div>

              {/* Notes & Summary */}
              {inspection.adjudication_notes && (
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                  <span className="text-xs font-bold text-slate-700">Adjudication Observations & Notes:</span>
                  <p className="text-xs text-slate-600 italic">{inspection.adjudication_notes}</p>
                </div>
              )}
            </div>
          )}

          {/* ── TAB 5: OPENCV PREPROCESSING QUALITY STUDIO ──────────────── */}
          {activeTab === 'preprocessing' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  OpenCV 10-Step Preprocessing Quality Studio
                </h3>
                <p className="text-xs text-slate-500">
                  Perspective correction, Hough deskewing, specular glare suppression, and CLAHE contrast enhancement.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                {inspection.preprocessed_images?.map((img, idx) => {
                  const meta = inspection.preprocessing_metadata?.[img.side] || {};
                  return (
                    <div key={idx} className="bg-slate-50 rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
                      <div className="p-3 bg-slate-100 border-b border-slate-200 flex justify-between items-center">
                        <span className="text-xs font-bold uppercase text-slate-800">{img.side} SIDE</span>
                        <Badge variant={meta.iqa_quality_score >= 60 ? 'success' : 'warning'} size="xs">
                          IQA Score: {meta.iqa_quality_score || 'N/A'}/100
                        </Badge>
                      </div>
                      <img
                        src={`/${img.file_path}`}
                        alt={`${img.side} Preprocessed`}
                        className="w-full h-48 object-cover bg-slate-900"
                      />
                      <div className="p-3 text-[11px] space-y-1 text-slate-600 font-mono">
                        <div>Deskew Angle: <b>{meta.deskew_angle_degrees ? `${meta.deskew_angle_degrees}°` : '0°'}</b></div>
                        <div>Glare Inpainted: <b>{meta.glare_suppressed ? 'Yes' : 'No'}</b></div>
                        <div>Resolution: <b>{meta.final_width}x{meta.final_height}px</b></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── TAB 6: COURT PDF & QR VERIFICATION ─────────────────────── */}
          {activeTab === 'report' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Court-Admissible Statutory Notice & PDF Inspection Dossier
                  </h3>
                  <p className="text-xs text-slate-500">
                    Generated via ReportLab with embedded SHA-256 cryptographic chain of custody and verification QR code.
                  </p>
                </div>
                <button
                  onClick={handleGenerateReport}
                  disabled={actionLoading}
                  className="px-4 py-2 text-xs font-semibold bg-emerald-700 hover:bg-emerald-600 text-white rounded-xl shadow flex items-center gap-1.5"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${actionLoading ? 'animate-spin' : ''}`} />
                  Regenerate Court Dossier
                </button>
              </div>

              {inspection.record_sha256_hash ? (
                <div className="p-6 bg-slate-900 text-white rounded-2xl space-y-6 shadow-xl">
                  {/* Cryptographic Hash Badge */}
                  <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        Tamper-Proof SHA-256 Chain of Custody Verified
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">Sec 65B BSA 2023</span>
                    </div>
                    <p className="font-mono text-xs text-slate-300 break-all bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                      {inspection.record_sha256_hash}
                    </p>
                  </div>

                  <div className="flex flex-col sm:flex-row items-center justify-between gap-6 pt-2">
                    <div className="space-y-2">
                      <h4 className="text-lg font-bold text-white">Statutory Report Available</h4>
                      <p className="text-xs text-slate-400 max-w-md">
                        Includes official ministry header, officer credentials, declared packaging specs, grounded violation dockets, and legal show-cause directive.
                      </p>
                      <div className="flex items-center gap-3 pt-2">
                        <a
                          href={`/api/v1/inspections/${id}/report/download`}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-2 px-5 py-2.5 text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-xl shadow-lg transition-all"
                        >
                          <Download className="w-4 h-4" />
                          Download PDF Report
                        </a>

                        {inspection.qr_verification_token && (
                          <Link
                            to={`/verify/${inspection.qr_verification_token}`}
                            target="_blank"
                            className="inline-flex items-center gap-2 px-4 py-2.5 text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-white rounded-xl border border-slate-700 transition-all"
                          >
                            <ExternalLink className="w-4 h-4" />
                            Open Public QR Verifier
                          </Link>
                        )}
                      </div>
                    </div>

                    <div className="p-4 bg-white rounded-2xl text-center shrink-0 shadow-lg">
                      <div className="text-slate-900 font-mono text-[10px] font-bold mb-1">SCAN TO VERIFY</div>
                      <div className="w-28 h-28 bg-slate-100 rounded-lg flex items-center justify-center border border-slate-200">
                        <QrCode className="w-20 h-20 text-slate-900" />
                      </div>
                      <div className="text-[9px] font-mono text-slate-500 mt-1 max-w-[120px] truncate">
                        {inspection.qr_verification_token}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center bg-slate-50 rounded-xl border border-dashed border-slate-300">
                  <QrCode className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-slate-700">Court report not yet compiled</p>
                  <p className="text-xs text-slate-500 mt-1 mb-4">Generate the official ReportLab PDF with cryptographic SHA-256 seal.</p>
                  <button
                    onClick={handleGenerateReport}
                    disabled={actionLoading}
                    className="px-4 py-2 bg-emerald-700 text-white rounded-xl font-bold text-xs shadow hover:bg-emerald-600"
                  >
                    Generate PDF Report & Notice Now
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ── ADJUDICATION MODAL DIALOG ────────────────────────────────────── */}
      {adjudicationModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4 animate-in fade-in">
          <div className="bg-white w-full max-w-lg rounded-2xl border border-slate-200 shadow-2xl overflow-hidden">
            <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Gavel className="w-5 h-5 text-amber-400" />
                <h3 className="font-bold text-sm">Statutory Adjudication & Settlement</h3>
              </div>
              <button
                onClick={() => setAdjudicationModalOpen(false)}
                className="text-slate-400 hover:text-white text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleAdjudicate} className="p-6 space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Select Legal Action</label>
                <select
                  value={adjAction}
                  onChange={(e) => setAdjAction(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl bg-white text-slate-800 font-medium focus:ring-2 focus:ring-amber-500 focus:outline-none"
                >
                  <option value="COMPOUND_OFFENCE">Compound Offence under Section 48 (Fine Payment)</option>
                  <option value="REFER_TO_COURT">Refer to Designated Magistrate Court (Section 36)</option>
                  <option value="ISSUE_SHOW_CAUSE">Issue 15-Day Statutory Show-Cause Notice</option>
                  <option value="CLOSE_WITH_WARNING">Close Docket with Formal Advisory Warning</option>
                </select>
              </div>

              {adjAction === 'COMPOUND_OFFENCE' && (
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Compounding Fine (₹)</label>
                    <input
                      type="number"
                      value={adjAmount}
                      onChange={(e) => setAdjAmount(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-xl font-bold text-slate-900 focus:ring-2 focus:ring-amber-500 focus:outline-none"
                      required
                    />
                  </div>
                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Challan / Receipt #</label>
                    <input
                      type="text"
                      placeholder="e.g. TR-2026-0842"
                      value={adjReceipt}
                      onChange={(e) => setAdjReceipt(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-xl font-mono text-slate-800 focus:ring-2 focus:ring-amber-500 focus:outline-none"
                    />
                  </div>
                </div>
              )}

              {adjAction === 'REFER_TO_COURT' && (
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Designated Court Jurisdiction</label>
                  <input
                    type="text"
                    placeholder="e.g. Court of Chief Judicial Magistrate, Pune"
                    value={adjCourt}
                    onChange={(e) => setAdjCourt(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-xl text-slate-800 focus:ring-2 focus:ring-amber-500 focus:outline-none"
                    required
                  />
                </div>
              )}

              <div>
                <label className="block font-bold text-slate-700 mb-1">Order / Docket Reference #</label>
                <input
                  type="text"
                  placeholder="e.g. CMP-ORD-2026-0842"
                  value={adjOrderNo}
                  onChange={(e) => setAdjOrderNo(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl font-mono text-slate-800 focus:ring-2 focus:ring-amber-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Officer Adjudication Notes</label>
                <textarea
                  rows="3"
                  placeholder="Observations and statutory terms for this adjudication order..."
                  value={adjNotes}
                  onChange={(e) => setAdjNotes(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl text-slate-800 focus:ring-2 focus:ring-amber-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setAdjudicationModalOpen(false)}
                  className="px-4 py-2 border border-slate-200 text-slate-600 rounded-xl hover:bg-slate-100 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-5 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl shadow flex items-center gap-1.5"
                >
                  <Check className="w-4 h-4" />
                  Save Adjudication Order
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
