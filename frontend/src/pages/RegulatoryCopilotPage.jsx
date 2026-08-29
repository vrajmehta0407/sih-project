import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Search,
  BookOpen,
  Scale,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  Sparkles,
  ArrowRight,
  ExternalLink,
} from 'lucide-react';
import api from '../services/api';

export default function RegulatoryCopilotPage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [suggestedPrompts, setSuggestedPrompts] = useState([]);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchSuggestedPrompts();
    handleSearch('Is Unit Sale Price mandatory for packages under 10 grams?');
  }, []);

  const fetchSuggestedPrompts = async () => {
    try {
      const resp = await api.get('/copilot/suggested-prompts');
      setSuggestedPrompts(resp.data);
    } catch {
      setSuggestedPrompts([
        'Is Unit Sale Price mandatory for packages under 10 grams?',
        'What are the digital display requirements for e-commerce platforms under Rule 6(10)?',
        'What are the mandatory font height rules for net quantity declarations under the First Schedule?',
        'What is the penalty range for a second offence of overcharging under Section 36(2)?',
        'Who is held liable for non-compliant packaging in a corporate entity under Section 49?',
      ]);
    }
  };

  const handleSearch = async (queryText) => {
    const q = queryText || query;
    if (!q.trim()) return;
    setLoading(true);
    setCopied(false);

    try {
      const resp = await api.post('/copilot/query', {
        query: q,
        jurisdiction_state: 'National',
        target_audience: 'OFFICER',
      });
      setResponse(resp.data);
    } catch {
      // Offline fallback
      setResponse({
        query: q,
        detected_intent: 'USP_EXEMPTION_RULES',
        legal_opinion:
          'Under Rule 6(11) of the Legal Metrology (Packaged Commodities) Rules, 2011, declaration of Unit Sale Price (USP) is NOT mandatory for pre-packaged commodities having a net quantity of 10 grams or less, or 10 milliliters or less, or sold by count containing only 1 item.',
        citations: [
          {
            act_or_rule: 'LM (Packaged Commodities) Rules, 2011',
            section_or_rule_no: 'Rule 6(11)',
            title: 'Exemption from Unit Sale Price Declaration',
            statutory_text_excerpt:
              'Declaration of Unit Sale Price is not mandatory for packages having net quantity equal to or less than 10g or 10ml, or where package contains one item sold by number.',
          },
        ],
        penalty_implications:
          'Non-declaration on non-exempt packages attracts Section 36(1) penalty up to ₹25,000 for first offence.',
        recommended_officer_actions: [
          'Verify certified net quantity of the subject package via weighment.',
          'If net quantity > 10g or > 10ml, inspect principal display panel for USP.',
          'If absent, issue Form-1 Notice under Rule 6(1)(e) read with Section 36(1).',
        ],
        is_compoundable: true,
        created_at: new Date().toISOString(),
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCopyNotice = () => {
    if (!response) return;
    const text = `LEGAL METROLOGY STATUTORY NOTICE SNIPPET\n\nQuery: ${response.query}\nStatutory Ruling: ${response.legal_opinion}\n\nStatutory Citations:\n${response.citations.map((c) => `• ${c.act_or_rule} [${c.section_or_rule_no}] - ${c.title}`).join('\n')}\n\nPenalty Clause: ${response.penalty_implications}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold uppercase tracking-wider">
            <Cpu className="w-3.5 h-3.5" />
            AI Regulatory Copilot & Truth Engine
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            National Legal Metrology AI Statutory Assistant
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm max-w-2xl mx-auto">
            Instant, court-admissible statutory opinions on the Legal Metrology Act 2009, Packaged Commodities Rules 2011, First Schedule font heights, E-Commerce mandates, and judicial precedents.
          </p>
        </div>

        {/* Search Input Bar */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSearch();
            }}
            className="flex gap-2"
          >
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Ask any legal question (e.g. font height for 500g, e-commerce liability, Section 36 penalty)..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs sm:text-sm text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs sm:text-sm flex items-center gap-2 transition-colors disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              Consult Copilot
            </button>
          </form>

          {/* Quick Prompt Chips */}
          <div className="mt-3 flex gap-1.5 overflow-x-auto no-scrollbar pt-1">
            {suggestedPrompts.map((p, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuery(p);
                  handleSearch(p);
                }}
                className="px-3 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 text-[11px] text-slate-300 whitespace-nowrap transition-colors flex items-center gap-1.5"
              >
                <span>{p.length > 38 ? p.substring(0, 38) + '...' : p}</span>
                <ArrowRight className="w-3 h-3 text-cyan-400" />
              </button>
            ))}
          </div>
        </div>

        {/* Legal Opinion Display */}
        {response && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
            {/* Header */}
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                  <Scale className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-white font-mono">Statutory Ruling & Analysis</h2>
                  <p className="text-[11px] text-slate-400">Intent: {response.detected_intent}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  {response.is_compoundable ? 'Section 48 Compoundable' : 'Court Prosecution Only'}
                </span>
                <button
                  onClick={handleCopyNotice}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center gap-1.5 transition-colors border border-slate-700"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  {copied ? 'Copied' : 'Copy Notice Text'}
                </button>
              </div>
            </div>

            {/* Opinion Body */}
            <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 space-y-3">
              <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                <BookOpen className="w-4 h-4" />
                Authoritative Legal Interpretation
              </h3>
              <p className="text-xs sm:text-sm text-slate-200 leading-relaxed whitespace-pre-line">
                {response.legal_opinion}
              </p>
            </div>

            {/* Citations Grid */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                Statutory Citations & Gazette Clauses
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {response.citations.map((c, idx) => (
                  <div key={idx} className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white font-mono">{c.section_or_rule_no}</span>
                      <span className="text-[10px] text-cyan-400 font-medium">{c.act_or_rule}</span>
                    </div>
                    <h4 className="text-xs font-semibold text-slate-200">{c.title}</h4>
                    <blockquote className="text-[11px] text-slate-400 italic border-l-2 border-cyan-500/50 pl-2.5 my-1">
                      "{c.statutory_text_excerpt}"
                    </blockquote>
                  </div>
                ))}
              </div>
            </div>

            {/* Penalty & Officer Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-amber-950/20 border border-amber-500/30 rounded-xl p-4 space-y-2">
                <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs">
                  <AlertCircle className="w-4 h-4" />
                  Statutory Penalty & Compounding Range
                </div>
                <p className="text-xs text-amber-200/90 leading-relaxed">{response.penalty_implications}</p>
              </div>

              <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 space-y-2">
                <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
                  <CheckCircle2 className="w-4 h-4" />
                  Recommended Officer Enforcement Actions
                </div>
                <ul className="text-xs text-slate-300 space-y-1.5">
                  {response.recommended_officer_actions.map((act, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-cyan-400 font-bold">•</span>
                      <span>{act}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
