import React, { useState } from 'react';
import {
  ShieldAlert,
  Send,
  Search,
  CheckCircle,
  Clock,
  AlertTriangle,
  FileText,
  MapPin,
  DollarSign,
  Copy,
  Check,
  UserCheck,
} from 'lucide-react';
import api from '../services/api';

export default function CitizenPortalPage() {
  const [activeTab, setActiveTab] = useState('submit'); // 'submit' | 'track'

  // Submit form state
  const [formData, setFormData] = useState({
    citizen_name: '',
    citizen_contact: '',
    retailer_name: '',
    retailer_address: '',
    state: 'Maharashtra',
    district: 'Mumbai',
    violation_category: 'OVERCHARGING_MRP',
    complaint_description: '',
    charged_price: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [submittedTicket, setSubmittedTicket] = useState(null);
  const [copied, setCopied] = useState(false);

  // Track ticket state
  const [trackNumber, setTrackNumber] = useState('');
  const [trackingLoading, setTrackingLoading] = useState(false);
  const [trackedData, setTrackedData] = useState(null);
  const [trackError, setTrackError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload = {
        ...formData,
        charged_price: formData.charged_price ? parseFloat(formData.charged_price) : null,
      };
      const resp = await api.post('/citizen/complaints', payload);
      setSubmittedTicket(resp.data);
    } catch (err) {
      alert('Failed to submit grievance. Please verify all required fields.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleTrack = async (e) => {
    e.preventDefault();
    if (!trackNumber.trim()) return;
    setTrackingLoading(true);
    setTrackError('');
    setTrackedData(null);
    try {
      const resp = await api.get(`/citizen/complaints/track/${trackNumber.trim()}`);
      setTrackedData(resp.data);
    } catch (err) {
      setTrackError('No grievance record found with this ticket number. Please verify the code.');
    } finally {
      setTrackingLoading(false);
    }
  };

  const copyTicket = () => {
    if (submittedTicket?.ticket_number) {
      navigator.clipboard.writeText(submittedTicket.ticket_number);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Government Portal Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold mb-3 tracking-widest uppercase">
            <ShieldAlert className="w-3.5 h-3.5" />
            National Consumer Protection Gateway
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Legal Metrology Public Grievance Portal
          </h1>
          <p className="text-slate-400 text-sm mt-2 max-w-xl mx-auto">
            Report overcharging above MRP, altered expiry dates, or misleading packaging directly to government enforcement authorities.
          </p>
        </div>

        {/* Tab Selector */}
        <div className="flex border-b border-slate-800 mb-8 bg-slate-900/60 p-1 rounded-xl">
          <button
            onClick={() => setActiveTab('submit')}
            className={`flex-1 py-3 text-sm font-semibold rounded-lg transition-all flex items-center justify-center gap-2 ${
              activeTab === 'submit'
                ? 'bg-amber-500 text-slate-950 shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Send className="w-4 h-4" />
            File New Grievance
          </button>
          <button
            onClick={() => setActiveTab('track')}
            className={`flex-1 py-3 text-sm font-semibold rounded-lg transition-all flex items-center justify-center gap-2 ${
              activeTab === 'track'
                ? 'bg-amber-500 text-slate-950 shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Search className="w-4 h-4" />
            Track Grievance Ticket
          </button>
        </div>

        {/* ================================================================= */}
        {/* TAB 1: FILE NEW GRIEVANCE */}
        {/* ================================================================= */}
        {activeTab === 'submit' && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl">
            {submittedTicket ? (
              <div className="text-center py-8 space-y-6">
                <div className="w-16 h-16 bg-emerald-500/20 border border-emerald-500/40 rounded-full flex items-center justify-center mx-auto text-emerald-400">
                  <CheckCircle className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white">Grievance Successfully Registered</h3>
                  <p className="text-slate-400 text-sm mt-1">
                    Your complaint has been processed and assigned to the jurisdictional Legal Metrology cell.
                  </p>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 max-w-md mx-auto">
                  <div className="text-xs text-slate-400 uppercase font-semibold mb-1">Your Tracking Ticket Number</div>
                  <div className="text-2xl font-mono font-bold text-amber-400 flex items-center justify-center gap-3">
                    {submittedTicket.ticket_number}
                    <button
                      onClick={copyTicket}
                      title="Copy Ticket Number"
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                    >
                      {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                  <div className="mt-3 flex items-center justify-between text-xs text-slate-400 pt-3 border-t border-slate-800">
                    <span>AI Credibility Score: <b>{submittedTicket.ai_credibility_score}%</b></span>
                    <span>Status: <b className="text-amber-400">{submittedTicket.status}</b></span>
                  </div>
                </div>

                <button
                  onClick={() => {
                    setSubmittedTicket(null);
                    setFormData({
                      citizen_name: '',
                      citizen_contact: '',
                      retailer_name: '',
                      retailer_address: '',
                      state: 'Maharashtra',
                      district: 'Mumbai',
                      violation_category: 'OVERCHARGING_MRP',
                      complaint_description: '',
                      charged_price: '',
                    });
                  }}
                  className="px-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-sm font-semibold transition-colors"
                >
                  File Another Grievance
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                      Your Full Name (Optional)
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Ananya Sen"
                      value={formData.citizen_name}
                      onChange={(e) => setFormData({ ...formData, citizen_name: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                      Email or Mobile Number <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. ananya@example.com / 9876543210"
                      value={formData.citizen_contact}
                      onChange={(e) => setFormData({ ...formData, citizen_contact: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                      Retailer / Establishment Name <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Modern Retail Store"
                      value={formData.retailer_name}
                      onChange={(e) => setFormData({ ...formData, retailer_name: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                      Violation Category <span className="text-rose-500">*</span>
                    </label>
                    <select
                      value={formData.violation_category}
                      onChange={(e) => setFormData({ ...formData, violation_category: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
                    >
                      <option value="OVERCHARGING_MRP">Overcharging Above Printed MRP</option>
                      <option value="DUAL_MRP">Dual MRP Stickers / Altered Label</option>
                      <option value="MISSING_DECLARATIONS">Missing Mandatory Declarations</option>
                      <option value="EXPIRED_SALE">Sale of Expired Packaged Commodity</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                      State <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.state}
                      onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                      District <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.district}
                      onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                      Charged Price (₹)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      placeholder="e.g. 150.00"
                      value={formData.charged_price}
                      onChange={(e) => setFormData({ ...formData, charged_price: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                    Retailer Full Address / Landmark
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Shop No. 12, High Street Mall, Sector 4"
                    value={formData.retailer_address}
                    onChange={(e) => setFormData({ ...formData, retailer_address: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                    Grievance Details <span className="text-rose-500">*</span>
                  </label>
                  <textarea
                    required
                    rows={4}
                    placeholder="Describe what occurred, product name, printed MRP vs price charged, etc."
                    value={formData.complaint_description}
                    onChange={(e) => setFormData({ ...formData, complaint_description: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-amber-500 resize-none"
                  />
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {submitting ? 'Submitting & Running AI Triage...' : 'Submit Grievance to Legal Metrology Department'}
                </button>
              </form>
            )}
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 2: TRACK TICKET */}
        {/* ================================================================= */}
        {activeTab === 'track' && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
            <form onSubmit={handleTrack} className="flex gap-3">
              <input
                type="text"
                placeholder="Enter Tracking Ticket Number (e.g. LM-CIT-2026-12345)"
                value={trackNumber}
                onChange={(e) => setTrackNumber(e.target.value)}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm font-mono text-white focus:outline-none focus:border-amber-500"
              />
              <button
                type="submit"
                disabled={trackingLoading}
                className="px-6 py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-sm rounded-xl transition-all disabled:opacity-50"
              >
                {trackingLoading ? 'Searching...' : 'Track Ticket'}
              </button>
            </form>

            {trackError && (
              <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl p-4 text-sm flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 shrink-0" />
                <span>{trackError}</span>
              </div>
            )}

            {trackedData && (
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 space-y-5">
                <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
                  <div>
                    <div className="text-xs text-slate-400 uppercase">Ticket Number</div>
                    <div className="text-xl font-mono font-bold text-amber-400">{trackedData.ticket_number}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-slate-400 uppercase">Enforcement Status</div>
                    <div className="inline-block px-2.5 py-1 rounded-full text-xs font-bold uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
                      {trackedData.status}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                  <div>
                    <span className="text-slate-500 block">Retailer:</span>
                    <span className="text-white font-semibold">{trackedData.retailer_name}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Jurisdiction:</span>
                    <span className="text-white font-semibold">{trackedData.district}, {trackedData.state}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Category:</span>
                    <span className="text-white font-semibold">{trackedData.violation_category}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">AI Credibility:</span>
                    <span className="text-emerald-400 font-bold">{trackedData.ai_credibility_score}%</span>
                  </div>
                </div>

                {trackedData.resolution_notes && (
                  <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 text-xs">
                    <div className="text-amber-400 font-semibold mb-1">Official Officer Finding / Resolution:</div>
                    <p className="text-slate-300">{trackedData.resolution_notes}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
