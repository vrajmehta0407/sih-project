import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
  Star,
  MessageSquareHeart,
  Send,
  Copy,
  Check,
  Users,
  RefreshCw,
  Link2,
} from 'lucide-react';

const CATEGORY_OPTIONS = [
  { value: 'inspection', label: 'Inspection Feedback' },
  { value: 'citizen_support', label: 'Citizen Support' },
  { value: 'trader_service', label: 'Trader Service' },
];

export const CSATPage = () => {
  const { user } = useAuth();
  const [category, setCategory] = useState('inspection');
  const [citizenName, setCitizenName] = useState('');
  const [citizenContact, setCitizenContact] = useState('');
  const [inspectionId, setInspectionId] = useState('');
  const [generating, setGenerating] = useState(false);
  const [survey, setSurvey] = useState(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const generateSurvey = async () => {
    setGenerating(true);
    setError('');
    setSurvey(null);
    try {
      const payload = {
        category,
        citizen_name: citizenName || 'Anonymous',
        citizen_contact: citizenContact,
      };
      if (inspectionId) payload.inspection_id = inspectionId;
      const res = await api.post('/csat/surveys', payload);
      const data = res.data?.data ?? res.data ?? res;
      const token = data.feedback_token;
      if (!token) {
        const publicUrl = `${window.location.origin}${window.location.pathname
          .replace(/\/[^/]*$/, '')
          .replace(/\/[^/]*$/, '')}/csat-submit?token=`;
        setSurvey({ data, feedbackLink: `${publicUrl}${data.id || ''}` });
      } else {
        const publicUrl = `${window.location.origin}/csat-submit?token=${token}`;
        setSurvey({ data, feedbackLink: publicUrl });
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not generate CSAT survey.');
    } finally {
      setGenerating(false);
    }
  };

  const copyLink = async () => {
    if (!survey?.feedbackLink) return;
    try {
      await navigator.clipboard.writeText(survey.feedbackLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError('Could not copy link.');
    }
  };

  const StarRow = ({ n }) => (
    <div className="flex space-x-1">
      {[1, 2, 3, 4, 5].map((i) => (
        <Star
          key={i}
          className={`h-8 w-8 ${
            i <= n ? 'fill-amber-400 text-amber-400' : 'text-slate-200'
          }`}
        />
      ))}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-mesh-vibrant rounded-3xl p-6 sm:p-8 border border-white/60 shadow-soft">
        <div className="flex items-center space-x-3 mb-3">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-violet-600 to-pink-600 flex items-center justify-center text-white shadow-tinted-blue">
            <MessageSquareHeart className="h-5 w-5" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-extrabold text-slate-900">
              CSAT Feedback
            </h1>
            <p className="text-xs text-slate-500 font-medium">
              Post-inspection citizen satisfaction scoring
            </p>
          </div>
        </div>
        <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-white/70 text-blue-700 border border-blue-200">
          <Users className="h-3 w-3" />
          <span>Token-based anonymous feedback</span>
        </span>
      </div>

      {error && (
        <div className="px-4 py-3 rounded-2xl text-sm font-semibold bg-rose-50 text-rose-700 border border-rose-200">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Generate */}
        <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-5 sm:p-6">
          <h2 className="font-display text-lg font-bold text-slate-900 mb-1">
            Generate Feedback Link
          </h2>
          <p className="text-xs text-slate-500 mb-5">
            Create a CSAT survey and share the token with the citizen.
          </p>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wide">
                Category
              </label>
              <div className="flex rounded-2xl bg-slate-100 border border-slate-200 p-1">
                {CATEGORY_OPTIONS.map((c) => (
                  <button
                    key={c.value}
                    onClick={() => setCategory(c.value)}
                    className={`flex-1 px-2 py-2 rounded-xl text-xs font-bold transition-colors ${
                      category === c.value
                        ? 'bg-gradient-to-r from-blue-600 to-violet-600 text-white shadow-sm'
                        : 'text-slate-500 hover:text-slate-700'
                    }`}
                  >
                    {c.label}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wide">
                Citizen Name (optional)
              </label>
              <input
                value={citizenName}
                onChange={(e) => setCitizenName(e.target.value)}
                className="w-full px-3 py-2.5 rounded-2xl bg-white border border-slate-200 shadow-sm text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wide">
                Citizen Contact (optional)
              </label>
              <input
                value={citizenContact}
                onChange={(e) => setCitizenContact(e.target.value)}
                placeholder="Mobile / e-mail / none"
                className="w-full px-3 py-2.5 rounded-2xl bg-white border border-slate-200 shadow-sm text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wide">
                Inspection ID (optional)
              </label>
              <input
                value={inspectionId}
                onChange={(e) => setInspectionId(e.target.value)}
                className="w-full px-3 py-2.5 rounded-2xl bg-white border border-slate-200 shadow-sm text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              />
            </div>
            <button
              onClick={generateSurvey}
              disabled={generating}
              className="w-full inline-flex items-center justify-center space-x-2 px-4 py-3 rounded-2xl bg-gradient-to-r from-blue-600 via-violet-600 to-pink-600 text-white font-bold text-sm shadow-tinted-blue hover:opacity-95 transition-opacity disabled:opacity-60"
            >
              {generating ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              <span>{generating ? 'Generating...' : 'Generate Survey'}</span>
            </button>
          </div>
        </div>

        {/* Preview / Result */}
        <div className="rounded-3xl bg-gradient-to-br from-violet-50 to-pink-50 border border-violet-100 shadow-sm p-5 sm:p-6">
          <h2 className="font-display text-lg font-bold text-slate-900 mb-1">
            Citizen Feedback Slip
          </h2>
          <p className="text-xs text-slate-500 mb-5">
            Preview of the star-rating UI citizens will see.
          </p>

          {survey ? (
            <div className="space-y-4">
              <div className="text-center p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
                <p className="text-sm font-bold text-slate-800 mb-4">
                  How would you rate the inspection service?
                </p>
                <div className="flex justify-center">
                  <StarRow n={4} />
                </div>
                <p className="text-xs text-slate-400 mt-3">
                  Category: {survey.data?.category ?? category}
                </p>
                <p className="text-xs font-mono text-violet-600 mt-1">
                  Token: {survey.data?.feedback_token ?? survey.data?.id ?? 'generated'}
                </p>
              </div>
              <div className="flex items-center justify-between p-3 rounded-2xl bg-white border border-slate-200 shadow-sm">
                <div className="flex items-center space-x-2 min-w-0">
                  <Link2 className="h-4 w-4 text-violet-500 shrink-0" />
                  <span className="text-xs text-slate-600 truncate">
                    {survey.feedbackLink}
                  </span>
                </div>
                <button
                  onClick={copyLink}
                  className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-violet-50 text-violet-700 border border-violet-200 text-xs font-bold hover:bg-violet-100 transition-colors shrink-0"
                >
                  {copied ? (
                    <Check className="h-3.5 w-3.5" />
                  ) : (
                    <Copy className="h-3.5 w-3.5" />
                  )}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-14">
              <div className="h-14 w-14 rounded-2xl bg-white flex items-center justify-center text-violet-400 shadow-sm mx-auto mb-3">
                <Star className="h-7 w-7" />
              </div>
              <p className="text-sm font-semibold text-slate-500">
                Generate a survey to preview the slip
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="text-right text-[11px] text-slate-400 font-medium">
        Surveys sync via /csat/surveys · public submission via /csat/submit
      </div>
    </div>
  );
};

export default CSATPage;
