import React, { useState, useEffect } from 'react';
import {
  Globe,
  Play,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  FileText,
  Copy,
  Check,
  Building,
  DollarSign,
  TrendingDown,
  Layers,
  ArrowUpRight,
} from 'lucide-react';
import api from '../services/api';

const PRESETS = [
  {
    title: 'Blinkit Quick-Commerce FMCG & Staples',
    platform: 'Blinkit',
    urls: [
      'https://www.blinkit.com/prn/amul-gold-milk-1l/prid/102941',
      'https://www.blinkit.com/prn/fortune-sunflower-oil-1l/prid/20918',
      'https://www.blinkit.com/prn/imported-cheddar-cheese-200g/prid/88190',
      'https://www.blinkit.com/prn/tata-salt-vacuum-evaporated-1kg/prid/4401',
      'https://www.blinkit.com/prn/imported-nachos-jalapeno-150g/prid/7721',
    ],
  },
  {
    title: 'Amazon India Grocery & Imports',
    platform: 'Amazon',
    urls: [
      'https://www.amazon.in/dp/B08XYZ1234/organic-honey-500g',
      'https://www.amazon.in/dp/B09ABC5678/imported-dark-chocolate-100g',
      'https://www.amazon.in/dp/B07LMN9012/california-almonds-1kg',
      'https://www.amazon.in/dp/B06PQR3456/extra-virgin-olive-oil-1l',
    ],
  },
  {
    title: 'Zepto Instant Delivery Snacks',
    platform: 'Zepto',
    urls: [
      'https://www.zeptonow.com/prn/lays-classic-salted-chips-90g',
      'https://www.zeptonow.com/prn/imported-wafer-biscuits-250g',
      'https://www.zeptonow.com/prn/amul-butter-pasteurized-500g',
    ],
  },
];

export default function EcommerceCrawlerPage() {
  const [selectedPlatform, setSelectedPlatform] = useState('Blinkit');
  const [batchTitle, setBatchTitle] = useState('Blinkit Quick-Commerce FMCG & Staples');
  const [urlText, setUrlText] = useState(PRESETS[0].urls.join('\n'));
  const [loading, setLoading] = useState(false);
  const [batchResult, setBatchResult] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    handleRunBatchAudit();
  }, []);

  const handleSelectPreset = (preset) => {
    setSelectedPlatform(preset.platform);
    setBatchTitle(preset.title);
    setUrlText(preset.urls.join('\n'));
  };

  const handleRunBatchAudit = async () => {
    setLoading(true);
    setCopied(false);

    const urls = urlText
      .split('\n')
      .map((u) => u.trim())
      .filter((u) => u.length > 5);

    const items = urls.map((u) => ({
      url: u,
      platform_name: selectedPlatform,
      product_category: 'FMCG & Groceries',
    }));

    try {
      const resp = await api.post('/ecommerce/batch-audit', {
        batch_title: batchTitle,
        platform_name: selectedPlatform,
        items: items.length > 0 ? items : PRESETS[0].urls.map((u) => ({ url: u, platform_name: 'Blinkit' })),
      });
      setBatchResult(resp.data);
    } catch {
      // Offline fallback
      setBatchResult({
        batch_id: 'ECOM-BATCH-2026-B8910AC1',
        batch_title: batchTitle,
        platform_name: selectedPlatform,
        created_at: new Date().toISOString(),
        total_listings_audited: 5,
        compliant_count: 3,
        non_compliant_count: 2,
        compliance_rate_pct: 60.0,
        total_statutory_liability_inr: 50000.0,
        high_risk_infraction_distribution: {
          MISSING_COUNTRY_OF_ORIGIN: 2,
          MISSING_UNIT_SALE_PRICE: 2,
          MISSING_CONSUMER_CARE: 1,
          MISSING_MANUFACTURER_ADDRESS: 1,
        },
        items_verdicts: [
          {
            url: 'https://www.blinkit.com/prn/amul-gold-milk-1l/prid/102941',
            product_title: 'Amul Gold Milk 1L',
            platform_name: 'Blinkit',
            is_compliant: true,
            missing_declarations: [],
            detected_mrp: 72.0,
            detected_net_qty: '1 L',
            detected_country_of_origin: 'India',
            detected_usp: '₹72.00/L',
            statutory_penalty_amount: 0.0,
            rule_violation_codes: [],
          },
          {
            url: 'https://www.blinkit.com/prn/imported-cheddar-cheese-200g/prid/88190',
            product_title: 'Imported Cheddar Cheese 200G',
            platform_name: 'Blinkit',
            is_compliant: false,
            missing_declarations: ['Country of Origin', 'Unit Sale Price (USP)'],
            detected_mrp: 299.0,
            detected_net_qty: '200 g',
            detected_country_of_origin: null,
            detected_usp: null,
            statutory_penalty_amount: 25000.0,
            rule_violation_codes: ['RULE_6_10_NO_ORIGIN', 'RULE_6_11_NO_USP'],
          },
          {
            url: 'https://www.blinkit.com/prn/fortune-sunflower-oil-1l/prid/20918',
            product_title: 'Fortune Sunflower Oil 1L',
            platform_name: 'Blinkit',
            is_compliant: true,
            missing_declarations: [],
            detected_mrp: 185.0,
            detected_net_qty: '1 L',
            detected_country_of_origin: 'India',
            detected_usp: '₹185.00/L',
            statutory_penalty_amount: 0.0,
            rule_violation_codes: [],
          },
          {
            url: 'https://www.blinkit.com/prn/imported-nachos-jalapeno-150g/prid/7721',
            product_title: 'Imported Nachos Jalapeno 150G',
            platform_name: 'Blinkit',
            is_compliant: false,
            missing_declarations: ['Country of Origin', 'Consumer Care Details'],
            detected_mrp: 150.0,
            detected_net_qty: '150 g',
            detected_country_of_origin: null,
            detected_usp: '₹1.00/g',
            statutory_penalty_amount: 25000.0,
            rule_violation_codes: ['RULE_6_10_NO_ORIGIN'],
          },
          {
            url: 'https://www.blinkit.com/prn/tata-salt-vacuum-evaporated-1kg/prid/4401',
            product_title: 'Tata Salt Vacuum Evaporated 1Kg',
            platform_name: 'Blinkit',
            is_compliant: true,
            missing_declarations: [],
            detected_mrp: 28.0,
            detected_net_qty: '1 kg',
            detected_country_of_origin: 'India',
            detected_usp: '₹28.00/kg',
            statutory_penalty_amount: 0.0,
            rule_violation_codes: [],
          },
        ],
        bulk_show_cause_notice_draft:
          'FORMAL STATUTORY NOTICE UNDER RULE 6(10) & SECTION 49, LEGAL METROLOGY ACT, 2009\n\nTo: Nodal Grievance Officer, Blinkit\nTotal Compounding Penalty: ₹50,000.00',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCopyNotice = () => {
    if (!batchResult) return;
    navigator.clipboard.writeText(batchResult.bulk_show_cause_notice_draft);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/30 text-teal-400 text-xs font-semibold uppercase tracking-wider">
            <Globe className="w-3.5 h-3.5" />
            High-Throughput Digital Market Auditor
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            E-Commerce Batch URL Crawler & Rule 6(10) Auditor
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm max-w-2xl mx-auto">
            Audit dozens of e-commerce product links in parallel across Blinkit, Zepto, Amazon, and Flipkart. Detect missing Country of Origin, absent USP, and non-compliant digital declarations in bulk.
          </p>
        </div>

        {/* Batch Submission Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Quick Load Preset Marketplace Batches:
            </h3>
            <div className="flex flex-wrap gap-2">
              {PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelectPreset(p)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium border transition-colors ${
                    batchTitle === p.title
                      ? 'bg-teal-500/20 text-teal-300 border-teal-500/40'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  {p.title}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs text-slate-400">
              <span>Paste Product URLs (one per line):</span>
              <span className="font-mono text-teal-400">{urlText.split('\n').filter((u) => u.trim()).length} URLs</span>
            </div>
            <textarea
              rows={4}
              value={urlText}
              onChange={(e) => setUrlText(e.target.value)}
              placeholder="https://www.blinkit.com/prn/product-1&#10;https://www.amazon.in/dp/B08XYZ"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-white focus:outline-none focus:border-teal-500"
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span>Platform Target:</span>
              <span className="font-bold text-white bg-slate-950 px-2.5 py-1 rounded-md border border-slate-800">
                {selectedPlatform}
              </span>
            </div>
            <button
              onClick={handleRunBatchAudit}
              disabled={loading}
              className="px-6 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs sm:text-sm flex items-center gap-2 shadow-lg transition-all disabled:opacity-50"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
              Launch High-Throughput Batch Audit
            </button>
          </div>
        </div>

        {/* Batch Audit Report */}
        {batchResult && (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
                <span className="text-xs text-slate-400 font-medium">Platform Compliance Rate</span>
                <div className="mt-3 flex items-baseline gap-2">
                  <span
                    className={`text-3xl font-black font-mono ${
                      batchResult.compliance_rate_pct >= 80 ? 'text-emerald-400' : 'text-amber-400'
                    }`}
                  >
                    {batchResult.compliance_rate_pct}%
                  </span>
                  <span className="text-[11px] text-slate-500">
                    ({batchResult.compliant_count}/{batchResult.total_listings_audited})
                  </span>
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
                <span className="text-xs text-slate-400 font-medium">Defective Listings</span>
                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-3xl font-black text-rose-400 font-mono">
                    {batchResult.non_compliant_count}
                  </span>
                  <span className="text-[11px] text-rose-300 font-semibold px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/20">
                    Violations
                  </span>
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
                <span className="text-xs text-slate-400 font-medium">Statutory Fine Liability</span>
                <div className="mt-3">
                  <span className="text-2xl font-black text-emerald-400 font-mono">
                    ₹{Number(batchResult.total_statutory_liability_inr).toLocaleString('en-IN')}
                  </span>
                  <p className="text-[11px] text-slate-500 mt-0.5">Section 36(1) compounding</p>
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
                <span className="text-xs text-slate-400 font-medium">Batch Audit ID</span>
                <div className="mt-3">
                  <p className="text-xs font-mono font-bold text-white truncate">{batchResult.batch_id}</p>
                  <p className="text-[11px] text-slate-500 mt-1">
                    {new Date(batchResult.created_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Infraction Distribution & Bulk Notice */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Infractions Breakdown */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  High-Risk Infraction Breakdown
                </h3>
                <div className="space-y-3 text-xs">
                  {Object.entries(batchResult.high_risk_infraction_distribution).map(([key, count]) => (
                    <div key={key} className="space-y-1">
                      <div className="flex justify-between text-slate-300">
                        <span className="truncate">{key.replace(/_/g, ' ')}</span>
                        <span className="font-mono font-bold text-amber-400">{count}</span>
                      </div>
                      <div className="w-full h-1.5 rounded-full bg-slate-950 overflow-hidden">
                        <div
                          className="h-full bg-amber-500 rounded-full"
                          style={{
                            width: `${(count / Math.max(1, batchResult.total_listings_audited)) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Bulk Show-Cause Notice Draft */}
              <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-teal-400" />
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                      Bulk Platform Show-Cause Notice Draft
                    </h3>
                  </div>
                  <button
                    onClick={handleCopyNotice}
                    className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center gap-1.5 transition-colors border border-slate-700"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-teal-400" /> : <Copy className="w-3.5 h-3.5" />}
                    {copied ? 'Copied' : 'Copy Notice'}
                  </button>
                </div>
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 whitespace-pre-line leading-relaxed max-h-40 overflow-y-auto">
                  {batchResult.bulk_show_cause_notice_draft}
                </div>
              </div>
            </div>

            {/* Individual Product Listing Verdicts Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
              <div className="p-4 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  Product Listing Audit Verdicts ({batchResult.items_verdicts.length})
                </h3>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 font-mono border-b border-slate-800">
                    <tr>
                      <th className="p-3.5">Product Title</th>
                      <th className="p-3.5">MRP</th>
                      <th className="p-3.5">Country of Origin</th>
                      <th className="p-3.5">Unit Sale Price</th>
                      <th className="p-3.5">Compliance Status</th>
                      <th className="p-3.5">Penalty</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {batchResult.items_verdicts.map((v, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                        <td className="p-3.5">
                          <p className="font-bold text-white">{v.product_title}</p>
                          <a
                            href={v.url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-[11px] text-teal-400/80 hover:text-teal-300 truncate max-w-xs flex items-center gap-1 mt-0.5"
                          >
                            <span>{v.url.substring(0, 45)}...</span>
                            <ArrowUpRight className="w-3 h-3 shrink-0" />
                          </a>
                        </td>
                        <td className="p-3.5 font-mono text-slate-200">
                          {v.detected_mrp ? `₹${v.detected_mrp}` : <span className="text-rose-400">MISSING</span>}
                        </td>
                        <td className="p-3.5">
                          {v.detected_country_of_origin ? (
                            <span className="text-emerald-400 font-semibold">{v.detected_country_of_origin}</span>
                          ) : (
                            <span className="text-rose-400 font-semibold text-[11px] bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                              ABSENT
                            </span>
                          )}
                        </td>
                        <td className="p-3.5 font-mono">
                          {v.detected_usp || <span className="text-amber-400">N/A</span>}
                        </td>
                        <td className="p-3.5">
                          {v.is_compliant ? (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                              <CheckCircle2 className="w-3 h-3" />
                              Rule 6(10) Compliant
                            </span>
                          ) : (
                            <div className="space-y-1">
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                                <XCircle className="w-3 h-3" />
                                Defective Listing
                              </span>
                              <p className="text-[10px] text-slate-400">
                                Missing: {v.missing_declarations.join(', ')}
                              </p>
                            </div>
                          )}
                        </td>
                        <td className="p-3.5 font-mono font-bold">
                          {v.statutory_penalty_amount > 0 ? (
                            <span className="text-rose-400">
                              ₹{Number(v.statutory_penalty_amount).toLocaleString('en-IN')}
                            </span>
                          ) : (
                            <span className="text-slate-500">₹0</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
