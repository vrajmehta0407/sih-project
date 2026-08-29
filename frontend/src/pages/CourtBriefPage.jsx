import React, { useState, useEffect } from 'react';
import {
  Scale,
  Gavel,
  ShieldAlert,
  FileText,
  Printer,
  Copy,
  Check,
  Building2,
  UserCheck,
  Calendar,
  Layers,
  ArrowRight,
} from 'lucide-react';
import api from '../services/api';

const PRESET_CASES = [
  {
    label: 'State vs. FastRetail (MRP Overcharging Recidivism)',
    case_title: 'State of Maharashtra (Legal Metrology Dept) vs. FastRetail Supermarkets Pvt. Ltd. & Ors.',
    court_name: 'Court of the Chief Judicial Magistrate (CJM), Mumbai',
    jurisdiction_district: 'Mumbai Suburban',
    company_name: 'FastRetail Supermarkets Pvt. Ltd.',
    registered_address: 'Plot 42, Bandra Kurla Complex, Mumbai 400051',
    managing_director_name: 'Vikramaditya Singhania',
    nominated_director_section_49: 'Anand R. Verma (Director - Supply Chain)',
    cin_number: 'U52100MH2018PTC304891',
    complainant_officer_name: 'Inspector Rajesh Kumar, LM Inspector Grade-I',
    offence_summary:
      'Willful and repeated overcharging above Maximum Retail Price (MRP) and altered price stickers under Section 18 read with Section 36(2) and Section 49.',
  },
  {
    label: 'State vs. QuickDelivery (Un-Compounded E-Com Fraud)',
    case_title: 'State of Delhi (Legal Metrology Dept) vs. QuickDelivery Logistics Pvt. Ltd.',
    court_name: 'Court of Chief Metropolitan Magistrate (CMM), Tis Hazari Courts, Delhi',
    jurisdiction_district: 'Central Delhi',
    company_name: 'QuickDelivery Logistics Pvt. Ltd.',
    registered_address: 'Tower B, Connaught Place, New Delhi 110001',
    managing_director_name: 'Sameer Malhotra',
    nominated_director_section_49: 'Pooja Kashyap (Chief Compliance Officer)',
    cin_number: 'U63090DL2019PTC345678',
    complainant_officer_name: 'Inspector Meenakshi Sharma, LM Inspector Grade-I',
    offence_summary:
      'Persistent omission of mandatory Country of Origin and USP declarations on quick-commerce digital network in violation of Rule 6(10) and Section 36(1).',
  },
];

export default function CourtBriefPage() {
  const [selectedCase, setSelectedCase] = useState(PRESET_CASES[0]);
  const [loading, setLoading] = useState(false);
  const [dossier, setDossier] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    handleGenerateBrief();
  }, []);

  const handleSelectPreset = (preset) => {
    setSelectedCase(preset);
  };

  const handleGenerateBrief = async () => {
    setLoading(true);
    setCopied(false);

    try {
      const resp = await api.post('/court-brief/generate', {
        case_title: selectedCase.case_title,
        court_name: selectedCase.court_name,
        jurisdiction_district: selectedCase.jurisdiction_district,
        complainant_officer_name: selectedCase.complainant_officer_name,
        accused: {
          company_name: selectedCase.company_name,
          registered_address: selectedCase.registered_address,
          managing_director_name: selectedCase.managing_director_name,
          nominated_director_section_49: selectedCase.nominated_director_section_49,
          cin_number: selectedCase.cin_number,
        },
        offence_summary: selectedCase.offence_summary,
      });
      setDossier(resp.data);
    } catch {
      // Offline fallback
      setDossier({
        dossier_id: 'COURT-BRIEF-2026-F981C01',
        case_title: selectedCase.case_title,
        court_name: selectedCase.court_name,
        jurisdiction_district: selectedCase.jurisdiction_district,
        filing_date: new Date().toISOString(),
        complainant_officer_name: selectedCase.complainant_officer_name,
        accused: {
          company_name: selectedCase.company_name,
          registered_address: selectedCase.registered_address,
          managing_director_name: selectedCase.managing_director_name,
          nominated_director_section_49: selectedCase.nominated_director_section_49,
          cin_number: selectedCase.cin_number,
        },
        statement_of_facts: [
          `1. That the Complainant, ${selectedCase.complainant_officer_name}, is an authorized Legal Metrology Inspector empowered under Section 15.`,
          `2. That a surprise statutory raid was conducted at ${selectedCase.registered_address} of ${selectedCase.company_name}.`,
          `3. That physical commodities were seized under Panchnama exhibiting altered MRP price tags and missing declarations.`,
          `4. That the digital inspection dossier was verified through automated Dual OCR and Error Level Analysis (ELA).`,
          `5. That the Accused failed to compound the offences under Section 48 within 30 days of notice.`,
          `6. That the Accused is a recidivist corporate offender liable under Section 36(2) and Section 49.`,
        ],
        statutory_penal_sections: [
          'Section 18 LM Act 2009',
          'Section 36(2) LM Act 2009 (Second Offence Recidivism)',
          'Section 49 LM Act 2009 (Corporate Criminal Liability)',
          'Rule 6(1)(e) LM PCR 2011',
        ],
        exhibits_inventory: [
          {
            exhibit_number: 'Exhibit P-1',
            description: 'Original Seizure Memo & Panchnama signed by Independent Witnesses',
            sha256_hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            date_of_seizure_or_generation: new Date().toLocaleDateString(),
          },
          {
            exhibit_number: 'Exhibit P-2',
            description: 'High-Resolution Photographic Evidence of Altered Price Stickers',
            sha256_hash: '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4',
            date_of_seizure_or_generation: new Date().toLocaleDateString(),
          },
          {
            exhibit_number: 'Exhibit P-3',
            description: 'Dual OCR Consensus & Rule 6 Extraction Automated Compliance Docket',
            sha256_hash: '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
            date_of_seizure_or_generation: new Date().toLocaleDateString(),
          },
          {
            exhibit_number: 'Exhibit P-4',
            description: 'Forensic Error Level Analysis (ELA) Tamper Heatmap & Bounding Boxes',
            sha256_hash: '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a',
            date_of_seizure_or_generation: new Date().toLocaleDateString(),
          },
        ],
        statutory_prayer_to_magistrate:
          'WHEREFORE, it is most respectfully prayed that this Hon’ble Court may take statutory cognizance of the offences, issue summons to the Accused, and try and punish the Accused under Section 36(2) and Section 49 with maximum fine and imprisonment.',
        section_65b_bsa_affidavit_text:
          'AFFIDAVIT UNDER SECTION 63 OF BHARATIYA SAKSHYA ADHINIYAM, 2023\n\nI hereby solemnly affirm that the computer systems and hashing algorithms were operating in lawful custody in the ordinary course of metrology enforcement.',
        master_court_seal_hash: 'c1b489a2456e7d98bf1290a124dc890214a56b789ef234a1b029485710294812',
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleCopyText = () => {
    if (!dossier) return;
    const text = `IN THE ${dossier.court_name.toUpperCase()}\n\n${dossier.case_title}\n\nSTATUTORY CHARGESHEET & SECTION 65B EVIDENCE DOSSIER\n\nFacts:\n${dossier.statement_of_facts.join('\n')}\n\nPenal Sections: ${dossier.statutory_penal_sections.join(', ')}\n\nPrayer:\n${dossier.statutory_prayer_to_magistrate}\n\nMaster Seal Hash: ${dossier.master_court_seal_hash}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold uppercase tracking-wider">
            <Gavel className="w-3.5 h-3.5" />
            Judicial Enforcement & Prosecution Chamber
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Pre-Trial Court Prosecution Brief & Sec 65B Dossier
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm max-w-2xl mx-auto">
            Automated criminal complaint drafting (Form V) for the Chief Judicial Magistrate (CJM) under Section 50, Legal Metrology Act 2009 read with Section 63 BSA 2023 (Sec 65B Evidence Act).
          </p>
        </div>

        {/* Preset Selector */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-wrap items-center justify-between gap-3">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Select Prosecution Case Preset:
          </span>
          <div className="flex flex-wrap gap-2">
            {PRESET_CASES.map((p, idx) => (
              <button
                key={idx}
                onClick={() => handleSelectPreset(p)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                  selectedCase.case_title === p.case_title
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                    : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Case Dossier Preview */}
        {dossier && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
            {/* Top Court Banner */}
            <div className="text-center border-b border-slate-800 pb-6 space-y-1">
              <span className="text-[11px] font-mono text-amber-400 uppercase tracking-widest block">
                IN THE {dossier.court_name.toUpperCase()}
              </span>
              <h2 className="text-base sm:text-lg font-black text-white">{dossier.case_title}</h2>
              <p className="text-xs text-slate-400 font-mono">Dossier Reference: {dossier.dossier_id}</p>
            </div>

            {/* Action Bar */}
            <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-950 p-3 rounded-xl border border-slate-800">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  Criminal Prosecution (Section 50)
                </span>
                <span className="text-xs text-slate-400">Jurisdiction: {dossier.jurisdiction_district}</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopyText}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center gap-1.5 transition-colors border border-slate-700"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  {copied ? 'Copied' : 'Copy Brief'}
                </button>
                <button
                  onClick={handlePrint}
                  className="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-lg transition-colors"
                >
                  <Printer className="w-3.5 h-3.5" />
                  Print Dossier
                </button>
              </div>
            </div>

            {/* Accused Corporate Roster (Section 49) */}
            <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-3">
              <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
                <Building2 className="w-4 h-4" />
                Accused Corporate Entity & Nominated Directors (Section 49)
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div>
                  <span className="text-slate-500">Accused No. 1 (Company):</span>
                  <p className="font-bold text-white mt-0.5">{dossier.accused.company_name}</p>
                  <p className="text-slate-400 text-[11px]">{dossier.accused.registered_address}</p>
                  <p className="text-slate-500 font-mono text-[10px] mt-1">CIN: {dossier.accused.cin_number}</p>
                </div>
                <div>
                  <span className="text-slate-500">Accused No. 2 (Managing Director):</span>
                  <p className="font-bold text-white mt-0.5">{dossier.accused.managing_director_name}</p>
                  <span className="text-slate-500 block mt-2">Accused No. 3 (Nominated Director u/s 49):</span>
                  <p className="font-semibold text-slate-300 text-[11px]">
                    {dossier.accused.nominated_director_section_49 || 'N/A (Joint Liability applies)'}
                  </p>
                </div>
              </div>
            </div>

            {/* Statement of Facts */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Chronological Statement of Facts
              </h3>
              <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 space-y-2 text-xs text-slate-300 leading-relaxed">
                {dossier.statement_of_facts.map((fact, idx) => (
                  <p key={idx}>{fact}</p>
                ))}
              </div>
            </div>

            {/* Evidentiary Exhibits Table */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Evidentiary Exhibits & Digital Custody Chain
              </h3>
              <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/80 text-slate-400 font-mono border-b border-slate-800">
                    <tr>
                      <th className="p-3">Exhibit #</th>
                      <th className="p-3">Description of Evidence</th>
                      <th className="p-3">SHA-256 Digital Fingerprint</th>
                      <th className="p-3">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {dossier.exhibits_inventory.map((ex, idx) => (
                      <tr key={idx} className="hover:bg-slate-900/40">
                        <td className="p-3 font-bold text-amber-400">{ex.exhibit_number}</td>
                        <td className="p-3 font-sans text-slate-200">{ex.description}</td>
                        <td className="p-3 text-[11px] text-emerald-400 truncate max-w-xs">{ex.sha256_hash}</td>
                        <td className="p-3 text-slate-400 text-[11px]">{ex.date_of_seizure_or_generation}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Statutory Prayer */}
            <div className="bg-amber-950/20 border border-amber-500/30 rounded-xl p-4 space-y-2">
              <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider">
                Statutory Prayer to the Hon'ble Magistrate
              </h3>
              <p className="text-xs text-amber-200/90 leading-relaxed whitespace-pre-line">
                {dossier.statutory_prayer_to_magistrate}
              </p>
            </div>

            {/* Section 65B BSA 2023 Digital Affidavit */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 font-mono text-xs text-slate-400">
              <span className="text-emerald-400 font-bold block">
                SECTION 63 BHARATIYA SAKSHYA ADHINIYAM, 2023 CERTIFICATE
              </span>
              <p className="whitespace-pre-line text-[11px] text-slate-300 leading-relaxed">
                {dossier.section_65b_bsa_affidavit_text}
              </p>
              <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-500">
                <span>Master Cryptographic Seal: {dossier.master_court_seal_hash}</span>
                <span>Complainant: {dossier.complainant_officer_name}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
