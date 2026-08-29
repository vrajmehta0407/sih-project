import { useState, useEffect, useCallback } from 'react';
import {
  ChevronLeft, ChevronRight, Play, Globe, Shield, FileText,
  BarChart2, AlertTriangle, Layers, Cpu, Wifi, Package, CheckCircle
} from 'lucide-react';

// ------------------------------------------------------------------
// Slide Data
// ------------------------------------------------------------------
const SLIDES = [
  {
    id: 1,
    type: 'title',
    badge: 'Smart India Hackathon 2026',
    title: 'Legal Metrology\nCompliance Enforcement\nPlatform',
    subtitle:
      'AI-powered automated inspection of packaged commodity labels under the Legal Metrology (Packaged Commodities) Rules, 2011',
    footer: 'Government of India · Bureau of Legal Metrology · Ministry of Consumer Affairs',
  },
  {
    id: 2,
    type: 'problem',
    badge: 'Problem Statement',
    title: 'The Enforcement Crisis',
    points: [
      { icon: Package, text: '150 crore+ packaged commodity units transact annually in India.' },
      { icon: AlertTriangle, text: 'Only ~0.04% of market inspected manually per year — enforcement gap is catastrophic.' },
      { icon: FileText, text: 'Rule 6, LM PCR 2011 mandates 11 statutory declarations on every package. 60–80% market non-compliance rate.' },
      { icon: Globe, text: 'Zero e-commerce Rule 6(10) enforcement: Amazon, Flipkart listings routinely missing mandatory disclosures.' },
      { icon: Shield, text: 'Manual inspection: 4–6 hours per lot. No tamper-proof digital audit trail. Adjudication backlog across courts.' },
    ],
  },
  {
    id: 3,
    type: 'solution',
    badge: 'Our Solution',
    title: 'End-to-End Enforcement\nAutomation in 90 Seconds',
    steps: [
      { step: '01', title: 'Photograph', desc: 'Inspector captures label image with any device.' },
      { step: '02', title: 'Preprocess', desc: 'OpenCV 12-step pipeline: deskew, CLAHE, EAN-13 barcode scan.' },
      { step: '03', title: 'OCR Consensus', desc: 'PaddleOCR ONNX + Tesseract dual engine. Token-level IoU consensus.' },
      { step: '04', title: 'Extract & Verify', desc: 'Rule 6 statutory declaration extraction in English + Hindi Devanagari.' },
      { step: '05', title: 'Adjudicate', desc: 'Automated violation docket. Section 48/49 compounding workflow.' },
      { step: '06', title: 'Seal & Submit', desc: 'SHA-256 sealed court PDF + Section 65B BSA 2023 admissibility.' },
    ],
  },
  {
    id: 4,
    type: 'architecture',
    badge: 'Technical Architecture',
    title: 'System Architecture',
    layers: [
      { name: 'PWA Mobile & Web Studio', color: 'from-amber-500 to-orange-500', tech: 'React 18 · Vite · Tailwind · Recharts · WebSocket' },
      { name: 'REST + WebSocket API Gateway', color: 'from-blue-500 to-indigo-500', tech: 'FastAPI · Uvicorn · OpenAPI 3.1 · JWT RBAC' },
      { name: 'AI Processing Engine', color: 'from-violet-500 to-purple-600', tech: 'OpenCV 12-Step · RapidOCR ONNX · Tesseract 5 · Hindi Devanagari NLP' },
      { name: 'Statutory Compliance Engine', color: 'from-green-500 to-emerald-600', tech: 'Rule 6 PCR 2011 · Sec 18/36 LM Act · Recidivism Escalator · Section 48/49 Compounding' },
      { name: 'Chain of Custody & Evidence', color: 'from-red-500 to-rose-600', tech: 'SHA-256 Canonical Hash · ReportLab PDF · Section 65B BSA 2023 QR Gateway' },
      { name: 'Data Layer', color: 'from-slate-500 to-slate-700', tech: 'PostgreSQL · SQLAlchemy ORM · Alembic · BSA 2023 Immutable Audit Log' },
    ],
  },
  {
    id: 5,
    type: 'stats',
    badge: 'Platform Metrics',
    title: 'Verified Benchmarks',
    stats: [
      { value: '90', unit: '/90', label: 'Automated Tests Passing', color: 'text-green-400' },
      { value: '< 4s', unit: '', label: 'Median Inspection Time (P50)', color: 'text-blue-400' },
      { value: '11', unit: '+', label: 'Rule 6 Statutory Declarations Extracted', color: 'text-amber-400' },
      { value: '100', unit: '%', label: 'Frontend Build Success (0 Errors)', color: 'text-violet-400' },
      { value: 'SHA-256', unit: '', label: 'Cryptographic Evidence Seal', color: 'text-red-400' },
      { value: 'Sec 65B', unit: '', label: 'BSA 2023 Court Admissibility', color: 'text-emerald-400' },
    ],
  },
  {
    id: 6,
    type: 'features',
    badge: 'Key Innovations',
    title: 'Unique Differentiators',
    features: [
      { icon: Globe, title: 'Bilingual OCR', desc: 'First-of-kind Hindi Devanagari statutory declaration extraction — MRP, Net Qty, Dates, Manufacturer in both scripts.' },
      { icon: Wifi, title: 'Real-Time WebSocket HQ', desc: 'Live field operations stream to Enforcement HQ dashboards. New violations trigger instant sirens without page refresh.' },
      { icon: Package, title: 'E-Commerce Rule 6(10) Auditor', desc: 'Automated audit of Amazon, Flipkart, Blinkit listings. Generates statutory show-cause notices for missing digital disclosures.' },
      { icon: Layers, title: 'Spatial Explainability Studio', desc: 'Hover any statutory field — the system highlights its exact bounding box on the product image. Full AI transparency.' },
      { icon: Shield, title: 'Section 48/49 Adjudication', desc: 'Complete compounding and court referral workflow with treasury receipt tracking, jurisdiction recording, and BSA audit trail.' },
      { icon: Cpu, title: 'PWA Offline Field App', desc: 'Installable Progressive Web App for offline data capture in areas without network connectivity.' },
    ],
  },
  {
    id: 7,
    type: 'cta',
    badge: 'Live Demonstration',
    title: 'Experience the Platform',
    links: [
      { label: 'Open Inspector Portal', url: 'http://localhost:5174/', color: 'bg-amber-500 hover:bg-amber-400' },
      { label: 'View Live API Docs', url: 'http://127.0.0.1:8001/docs', color: 'bg-blue-600 hover:bg-blue-500' },
      { label: 'QR Verification Gateway', url: 'http://localhost:5174/verify/demo', color: 'bg-violet-600 hover:bg-violet-500' },
    ],
    credentials: [
      { role: 'Field Inspector', email: 'inspector.mumbai@legalmetrology.gov.in', password: 'InspectorPassword@123' },
      { role: 'Enforcement Director', email: 'admin@legalmetrology.gov.in', password: 'AdminPassword@123' },
    ],
  },
];

// ------------------------------------------------------------------
// Slide Renderers
// ------------------------------------------------------------------
function TitleSlide({ slide }) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-8">
      <span className="bg-amber-500/20 border border-amber-500/40 text-amber-400 text-xs font-semibold px-4 py-1.5 rounded-full mb-6 tracking-widest uppercase">
        {slide.badge}
      </span>
      <h1 className="text-5xl md:text-6xl font-black text-white leading-tight mb-6 whitespace-pre-line">
        {slide.title}
      </h1>
      <p className="text-slate-300 text-lg max-w-2xl mb-10">{slide.subtitle}</p>
      <div className="text-slate-500 text-sm">{slide.footer}</div>
    </div>
  );
}

function ProblemSlide({ slide }) {
  return (
    <div className="flex flex-col h-full px-8 py-6">
      <span className="bg-red-500/20 border border-red-500/40 text-red-400 text-xs font-semibold px-4 py-1.5 rounded-full mb-4 self-start tracking-widest uppercase">
        {slide.badge}
      </span>
      <h2 className="text-4xl font-black text-white mb-8">{slide.title}</h2>
      <div className="flex flex-col gap-4">
        {slide.points.map(({ icon: Icon, text }, i) => (
          <div key={i} className="flex items-start gap-4 bg-white/5 border border-white/10 rounded-xl px-5 py-4">
            <Icon className="w-6 h-6 text-red-400 mt-0.5 shrink-0" />
            <p className="text-slate-200 text-base leading-relaxed">{text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function SolutionSlide({ slide }) {
  return (
    <div className="flex flex-col h-full px-8 py-6">
      <span className="bg-green-500/20 border border-green-500/40 text-green-400 text-xs font-semibold px-4 py-1.5 rounded-full mb-4 self-start tracking-widest uppercase">
        {slide.badge}
      </span>
      <h2 className="text-4xl font-black text-white mb-6 whitespace-pre-line">{slide.title}</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {slide.steps.map(({ step, title, desc }) => (
          <div key={step} className="bg-white/5 border border-white/10 rounded-xl p-5">
            <span className="text-3xl font-black text-amber-500/50">{step}</span>
            <h3 className="text-white font-bold mt-1 mb-1">{title}</h3>
            <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function ArchitectureSlide({ slide }) {
  return (
    <div className="flex flex-col h-full px-8 py-6">
      <span className="bg-blue-500/20 border border-blue-500/40 text-blue-400 text-xs font-semibold px-4 py-1.5 rounded-full mb-4 self-start tracking-widest uppercase">
        {slide.badge}
      </span>
      <h2 className="text-4xl font-black text-white mb-6">{slide.title}</h2>
      <div className="flex flex-col gap-3 flex-1">
        {slide.layers.map(({ name, color, tech }) => (
          <div key={name} className={`bg-gradient-to-r ${color} p-px rounded-xl`}>
            <div className="bg-slate-900 rounded-xl px-5 py-3 flex items-center justify-between gap-4">
              <span className="text-white font-semibold text-sm whitespace-nowrap">{name}</span>
              <span className="text-slate-400 text-xs text-right">{tech}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatsSlide({ slide }) {
  return (
    <div className="flex flex-col h-full px-8 py-6">
      <span className="bg-violet-500/20 border border-violet-500/40 text-violet-400 text-xs font-semibold px-4 py-1.5 rounded-full mb-4 self-start tracking-widest uppercase">
        {slide.badge}
      </span>
      <h2 className="text-4xl font-black text-white mb-8">{slide.title}</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-5 flex-1">
        {slide.stats.map(({ value, unit, label, color }) => (
          <div key={label} className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col justify-between">
            <div className={`text-4xl font-black ${color}`}>
              {value}<span className="text-xl">{unit}</span>
            </div>
            <p className="text-slate-400 text-sm mt-3">{label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function FeaturesSlide({ slide }) {
  return (
    <div className="flex flex-col h-full px-8 py-6">
      <span className="bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-xs font-semibold px-4 py-1.5 rounded-full mb-4 self-start tracking-widest uppercase">
        {slide.badge}
      </span>
      <h2 className="text-4xl font-black text-white mb-6">{slide.title}</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {slide.features.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="bg-white/5 border border-white/10 rounded-xl p-5">
            <Icon className="w-6 h-6 text-amber-400 mb-3" />
            <h3 className="text-white font-bold mb-1.5">{title}</h3>
            <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function CtaSlide({ slide }) {
  return (
    <div className="flex flex-col h-full px-8 py-6">
      <span className="bg-amber-500/20 border border-amber-500/40 text-amber-400 text-xs font-semibold px-4 py-1.5 rounded-full mb-4 self-start tracking-widest uppercase">
        {slide.badge}
      </span>
      <h2 className="text-4xl font-black text-white mb-6">{slide.title}</h2>
      <div className="flex flex-col gap-3 mb-8">
        {slide.links.map(({ label, url, color }) => (
          <a key={label} href={url} target="_blank" rel="noreferrer"
            className={`${color} text-white font-bold py-3 px-6 rounded-xl flex items-center gap-2 transition-colors text-sm`}>
            <Play className="w-4 h-4" /> {label}
          </a>
        ))}
      </div>
      <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
        <p className="text-slate-400 text-xs uppercase tracking-widest font-semibold mb-3">Demo Credentials</p>
        <div className="flex flex-col gap-3">
          {slide.credentials.map(({ role, email, password }) => (
            <div key={role} className="bg-slate-800 rounded-xl p-4">
              <p className="text-amber-400 font-semibold text-xs mb-1">{role}</p>
              <p className="text-slate-200 text-sm font-mono">{email}</p>
              <p className="text-slate-400 text-sm font-mono">{password}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const RENDERERS = {
  title: TitleSlide,
  problem: ProblemSlide,
  solution: SolutionSlide,
  architecture: ArchitectureSlide,
  stats: StatsSlide,
  features: FeaturesSlide,
  cta: CtaSlide,
};

// ------------------------------------------------------------------
// Presentation Page
// ------------------------------------------------------------------
export default function PresentationPage() {
  const [current, setCurrent] = useState(0);
  const total = SLIDES.length;

  const prev = useCallback(() => setCurrent(c => Math.max(0, c - 1)), []);
  const next = useCallback(() => setCurrent(c => Math.min(total - 1, c + 1)), [total]);

  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ') next();
      if (e.key === 'ArrowLeft') prev();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [next, prev]);

  const slide = SLIDES[current];
  const Renderer = RENDERERS[slide.type] || TitleSlide;

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4">
      {/* Slide Card */}
      <div className="w-full max-w-4xl bg-slate-900 border border-white/10 rounded-3xl shadow-2xl overflow-hidden"
        style={{ minHeight: '70vh' }}>
        <div className="flex flex-col h-full" style={{ minHeight: '70vh' }}>
          <Renderer slide={slide} />
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-6 mt-6">
        <button onClick={prev} disabled={current === 0}
          className="p-3 rounded-full bg-white/5 border border-white/10 text-white hover:bg-white/10 disabled:opacity-30 transition-all">
          <ChevronLeft className="w-5 h-5" />
        </button>

        {/* Dots */}
        <div className="flex gap-2">
          {SLIDES.map((_, i) => (
            <button key={i} onClick={() => setCurrent(i)}
              className={`w-2 h-2 rounded-full transition-all ${i === current ? 'bg-amber-400 w-6' : 'bg-white/20 hover:bg-white/40'}`} />
          ))}
        </div>

        <button onClick={next} disabled={current === total - 1}
          className="p-3 rounded-full bg-white/5 border border-white/10 text-white hover:bg-white/10 disabled:opacity-30 transition-all">
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Slide counter + keyboard hint */}
      <p className="mt-3 text-slate-600 text-xs">
        {current + 1} / {total} &nbsp;·&nbsp; Use ← → keys to navigate
      </p>
    </div>
  );
}
