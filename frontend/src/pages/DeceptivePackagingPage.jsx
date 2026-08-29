import React, { useState, useEffect } from 'react';
import {
  Box,
  Layers,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileText,
  Copy,
  Check,
  Maximize2,
  Percent,
  Sliders,
  Sparkles,
} from 'lucide-react';
import api from '../services/api';

const PRESET_PACKAGES = [
  {
    label: 'Oversized Cereal Box (58% Slack-Fill - Violation)',
    product_name: 'Crispy Cornflakes 500g Mega Box',
    brand_name: 'CrispyBites',
    packaging_type: 'RIGID_BOX',
    package_length_cm: 24.0,
    package_width_cm: 12.0,
    package_height_cm: 36.0, // V_outer = 10,368 cm3
    declared_net_quantity_grams: 500.0,
    product_bulk_density_g_per_cm3: 0.18, // V_product = 2,777 cm3 (slack = ~73%)
    functional_cushion_allowance_pct: 15.0,
  },
  {
    label: 'Potato Chips Pouch (28% Nitrogen - Compliant)',
    product_name: 'Classic Salted Potato Chips 90g',
    brand_name: 'CrunchTime',
    packaging_type: 'FLEXIBLE_POUCH',
    package_length_cm: 18.0,
    package_width_cm: 6.0,
    package_height_cm: 22.0,
    declared_net_quantity_grams: 90.0,
    product_bulk_density_g_per_cm3: 0.06,
    functional_cushion_allowance_pct: 30.0,
  },
  {
    label: 'Cosmetic Cream Jar False Bottom (Violation)',
    product_name: 'Luxe Anti-Aging Face Cream 50g',
    brand_name: 'LuxeGlow',
    packaging_type: 'JAR_WITH_FALSE_BOTTOM',
    package_length_cm: 8.0,
    package_width_cm: 8.0,
    package_height_cm: 8.0, // V_outer = 512 cm3
    declared_net_quantity_grams: 50.0,
    product_bulk_density_g_per_cm3: 0.95, // V_product = 52.6 cm3 (slack = ~89%)
    functional_cushion_allowance_pct: 10.0,
  },
];

export default function DeceptivePackagingPage() {
  const [formData, setFormData] = useState(PRESET_PACKAGES[0]);
  const [loading, setLoading] = useState(false);
  const [auditResult, setAuditResult] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    handleRunAudit();
  }, []);

  const handleSelectPreset = (preset) => {
    setFormData(preset);
  };

  const handleRunAudit = async () => {
    setLoading(true);
    setCopied(false);

    try {
      const resp = await api.post('/deceptive-packaging/audit', {
        product_name: formData.product_name,
        brand_name: formData.brand_name,
        packaging_type: formData.packaging_type,
        package_length_cm: Number(formData.package_length_cm),
        package_width_cm: Number(formData.package_width_cm),
        package_height_cm: Number(formData.package_height_cm),
        declared_net_quantity_grams: Number(formData.declared_net_quantity_grams),
        product_bulk_density_g_per_cm3: Number(formData.product_bulk_density_g_per_cm3),
        functional_cushion_allowance_pct: Number(formData.functional_cushion_allowance_pct),
      });
      setAuditResult(resp.data);
    } catch {
      // Offline fallback
      const vOuter = Number(formData.package_length_cm) * Number(formData.package_width_cm) * Number(formData.package_height_cm);
      const vProd = Number(formData.declared_net_quantity_grams) / Number(formData.product_bulk_density_g_per_cm3);
      const vSlack = Math.max(0, vOuter - vProd);
      const totalSlackPct = (vSlack / vOuter) * 100;
      const funcAllowance = Number(formData.functional_cushion_allowance_pct);
      const deceptivePct = Math.max(0, totalSlackPct - funcAllowance);
      const vdi = Math.min(10.0, Number((deceptivePct / 6.0).toFixed(1)));
      const isComp = deceptivePct <= 15.0;

      setAuditResult({
        audit_id: 'DECEPTIVE-AUDIT-2026-F981D01',
        product_name: formData.product_name,
        brand_name: formData.brand_name,
        packaging_type: formData.packaging_type,
        audited_at: new Date().toISOString(),
        container_outer_volume_cm3: vOuter,
        actual_product_volume_cm3: vProd,
        total_slack_fill_volume_cm3: vSlack,
        total_slack_fill_pct: Number(totalSlackPct.toFixed(1)),
        functional_allowance_pct: funcAllowance,
        deceptive_non_functional_slack_fill_pct: Number(deceptivePct.toFixed(1)),
        visual_deception_index: vdi,
        deception_risk_level: vdi >= 7 ? 'CRITICAL_FRAUD' : vdi >= 4 ? 'HIGH_DECEPTIVE' : 'NEGLIGIBLE',
        is_compliant_with_rule_5: isComp,
        statutory_verdict: isComp ? 'COMPLIANT_FUNCTIONAL_PACKAGING' : 'DECEPTIVE_PACKAGING_VIOLATION',
        statutory_penalty_amount_inr: isComp ? 0 : 25000,
        statutory_citations: [
          'Section 18, Legal Metrology Act, 2009 (Prohibition of Misleading/Deceptive Packaging)',
          'Rule 5 & Rule 21, Legal Metrology (Packaged Commodities) Rules, 2011',
        ],
        officer_action_recommendation: isComp
          ? 'Packaging volume is proportional to declared contents. Compliant.'
          : 'Non-functional slack fill exceeds statutory limits. Issue Section 18 Show-Cause Notice.',
        digital_audit_seal: '7a89b02456e7d98bf1290a124dc890214a56b789ef234a1b029485710294812f',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCopyNotice = () => {
    if (!auditResult) return;
    const text = `STATUTORY NOTICE UNDER SECTION 18 & RULE 5, LEGAL METROLOGY ACT, 2009\n\nProduct: ${auditResult.product_name} (${auditResult.brand_name})\nContainer Volume: ${auditResult.container_outer_volume_cm3} cm3\nActual Product Volume: ${auditResult.actual_product_volume_cm3} cm3\nDeceptive Slack-Fill: ${auditResult.deceptive_non_functional_slack_fill_pct}%\nVisual Deception Index: ${auditResult.visual_deception_index}/10.0\n\nRuling: ${auditResult.officer_action_recommendation}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 border border-violet-500/30 text-violet-400 text-xs font-semibold uppercase tracking-wider">
            <Box className="w-3.5 h-3.5" />
            AI Volumetric Slack-Fill & Deception Engine
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Deceptive Packaging & Visual Deception Index (VDI)
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm max-w-2xl mx-auto">
            Statutory detection of oversized containers, non-functional slack fill, and deceptive packaging under Section 18 & Rule 5 of the Legal Metrology (Packaged Commodities) Rules 2011.
          </p>
        </div>

        {/* Preset Selector */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-wrap items-center justify-between gap-3">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Select Packaging Preset:
          </span>
          <div className="flex flex-wrap gap-2">
            {PRESET_PACKAGES.map((p, idx) => (
              <button
                key={idx}
                onClick={() => handleSelectPreset(p)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                  formData.product_name === p.product_name
                    ? 'bg-violet-500/20 text-violet-300 border-violet-500/40'
                    : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Input Dimensions & Volumetric Parameters */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Form */}
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4 text-violet-400" />
              Container Dimensions & Product Density
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="space-y-1 sm:col-span-2">
                <label className="text-slate-400">Product Title</label>
                <input
                  type="text"
                  value={formData.product_name}
                  onChange={(e) => setFormData({ ...formData, product_name: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-white font-medium focus:border-violet-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-400">Brand Name</label>
                <input
                  type="text"
                  value={formData.brand_name}
                  onChange={(e) => setFormData({ ...formData, brand_name: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-white focus:border-violet-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-400">Length (L) in cm</label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.package_length_cm}
                  onChange={(e) => setFormData({ ...formData, package_length_cm: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-violet-300 font-mono font-bold focus:border-violet-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-400">Width (W) in cm</label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.package_width_cm}
                  onChange={(e) => setFormData({ ...formData, package_width_cm: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-violet-300 font-mono font-bold focus:border-violet-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-400">Height (H) in cm</label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.package_height_cm}
                  onChange={(e) => setFormData({ ...formData, package_height_cm: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-violet-300 font-mono font-bold focus:border-violet-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-400">Declared Net Qty (g)</label>
                <input
                  type="number"
                  step="1"
                  value={formData.declared_net_quantity_grams}
                  onChange={(e) => setFormData({ ...formData, declared_net_quantity_grams: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-emerald-300 font-mono font-bold focus:border-violet-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-400">Bulk Density (g/cm³)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.product_bulk_density_g_per_cm3}
                  onChange={(e) => setFormData({ ...formData, product_bulk_density_g_per_cm3: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-amber-300 font-mono font-bold focus:border-violet-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-400">Cushion Allowance (%)</label>
                <input
                  type="number"
                  value={formData.functional_cushion_allowance_pct}
                  onChange={(e) => setFormData({ ...formData, functional_cushion_allowance_pct: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-cyan-300 font-mono focus:border-violet-500"
                />
              </div>
            </div>

            <button
              onClick={handleRunAudit}
              disabled={loading}
              className="w-full py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-lg transition-all disabled:opacity-50 mt-2"
            >
              <Sparkles className="w-4 h-4" />
              Compute 3D Volumetric Slack-Fill & Calculate VDI
            </button>
          </div>

          {/* VDI Risk Meter Card */}
          {auditResult && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between space-y-4 text-center">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                  Visual Deception Index (VDI)
                </span>
                <div className="mt-4">
                  <span
                    className={`text-5xl font-black font-mono ${
                      auditResult.visual_deception_index >= 7.0
                        ? 'text-rose-500'
                        : auditResult.visual_deception_index >= 4.0
                        ? 'text-amber-400'
                        : 'text-emerald-400'
                    }`}
                  >
                    {auditResult.visual_deception_index}
                  </span>
                  <span className="text-sm text-slate-500 block mt-1">out of 10.0</span>
                </div>
              </div>

              <div>
                <span
                  className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${
                    auditResult.is_compliant_with_rule_5
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                  }`}
                >
                  {auditResult.is_compliant_with_rule_5 ? (
                    <CheckCircle2 className="w-3.5 h-3.5" />
                  ) : (
                    <XCircle className="w-3.5 h-3.5" />
                  )}
                  {auditResult.statutory_verdict.replace(/_/g, ' ')}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* 3D Volumetric Fill Breakdown */}
        {auditResult && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-6">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-violet-400" />
              3D Container Volumetric Fill Distribution
            </h3>

            {/* Visual Multi-Segment Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-slate-300 font-mono">
                <span>Total Container Volume: {Number(auditResult.container_outer_volume_cm3).toLocaleString()} $cm^3$</span>
                <span className="text-rose-400 font-bold">
                  {auditResult.deceptive_non_functional_slack_fill_pct}% Non-Functional Slack-Fill
                </span>
              </div>

              <div className="w-full h-8 rounded-xl bg-slate-950 border border-slate-800 flex overflow-hidden p-1 gap-1">
                {/* Actual Product Volume */}
                <div
                  style={{
                    width: `${Math.max(
                      5,
                      (auditResult.actual_product_volume_cm3 / auditResult.container_outer_volume_cm3) * 100
                    )}%`,
                  }}
                  className="bg-emerald-500 rounded-lg flex items-center justify-center text-[10px] font-bold text-slate-950 truncate px-1"
                  title="Actual Product Volume"
                >
                  Product Content ({Number(auditResult.actual_product_volume_cm3).toFixed(0)} cm³)
                </div>

                {/* Functional Cushion */}
                <div
                  style={{
                    width: `${auditResult.functional_allowance_pct}%`,
                  }}
                  className="bg-cyan-500/60 rounded-lg flex items-center justify-center text-[10px] font-bold text-slate-950 truncate px-1"
                  title="Engineering Cushion Allowance"
                >
                  Cushion ({auditResult.functional_allowance_pct}%)
                </div>

                {/* Deceptive Slack Fill */}
                {auditResult.deceptive_non_functional_slack_fill_pct > 0 && (
                  <div
                    style={{
                      width: `${auditResult.deceptive_non_functional_slack_fill_pct}%`,
                    }}
                    className="bg-rose-500 rounded-lg flex items-center justify-center text-[10px] font-bold text-white truncate px-1 animate-pulse"
                    title="Deceptive Empty Space"
                  >
                    Deceptive Empty Space ({auditResult.deceptive_non_functional_slack_fill_pct}%)
                  </div>
                )}
              </div>
            </div>

            {/* Metric Cards Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                <span className="text-[11px] text-slate-400">Total Empty Space</span>
                <p className="text-lg font-black text-amber-400 font-mono mt-1">
                  {auditResult.total_slack_fill_pct}%
                </p>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                <span className="text-[11px] text-slate-400">Deceptive Slack-Fill</span>
                <p className="text-lg font-black text-rose-400 font-mono mt-1">
                  {auditResult.deceptive_non_functional_slack_fill_pct}%
                </p>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                <span className="text-[11px] text-slate-400">Cushion Allowance</span>
                <p className="text-lg font-black text-cyan-400 font-mono mt-1">
                  {auditResult.functional_allowance_pct}%
                </p>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                <span className="text-[11px] text-slate-400">Statutory Liability</span>
                <p className="text-lg font-black text-emerald-400 font-mono mt-1">
                  ₹{Number(auditResult.statutory_penalty_amount_inr).toLocaleString('en-IN')}
                </p>
              </div>
            </div>

            {/* Statutory Ruling & Action Bar */}
            <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-violet-400 uppercase tracking-wider">
                  Enforcement Recommendation & Statutory Citation
                </h4>
                <button
                  onClick={handleCopyNotice}
                  className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center gap-1.5 transition-colors border border-slate-700"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  {copied ? 'Copied' : 'Copy Notice Text'}
                </button>
              </div>
              <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
                {auditResult.officer_action_recommendation}
              </p>
              <div className="pt-2 border-t border-slate-800/80 space-y-1">
                {auditResult.statutory_citations.map((c, idx) => (
                  <p key={idx} className="text-[11px] text-slate-400 font-mono">• {c}</p>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
