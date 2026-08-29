import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { RotateCw, Cpu, FileCheck2, Scale, ShieldCheck } from 'lucide-react';

const STAGES = [
  {
    label: 'Deskewing & CLAHE Contrast Preprocessing',
    subtext: 'Correcting tilt ±45° and inpainting surface glare',
    icon: RotateCw,
    color: 'text-blue-600',
    bg: 'bg-blue-50 border-blue-200',
  },
  {
    label: 'Dual-OCR Consensus Engine',
    subtext: 'RapidOCR + Tesseract IoU ≥ 0.30 alignment',
    icon: Cpu,
    color: 'text-purple-600',
    bg: 'bg-purple-50 border-purple-200',
  },
  {
    label: 'Extracting Rule 6 Declarations',
    subtext: 'MRP, Net Qty, Mfg Date, Consumer Care, Origin',
    icon: FileCheck2,
    color: 'text-amber-600',
    bg: 'bg-amber-50 border-amber-200',
  },
  {
    label: 'Statutory Compliance & Recidivism Check',
    subtext: 'Validating LM Act 2009 Sec 36(1)/(2) penalties',
    icon: Scale,
    color: 'text-emerald-600',
    bg: 'bg-emerald-50 border-emerald-200',
  },
  {
    label: 'Generating Court-Ready Evidence Dossier',
    subtext: 'BSA 2023 §63 cryptographic SHA-256 certificate',
    icon: ShieldCheck,
    color: 'text-pink-600',
    bg: 'bg-pink-50 border-pink-200',
  },
];

export const PipelineLoader = ({
  currentStage = 0,
  autoProgress = true,
  intervalMs = 700,
  onComplete,
}) => {
  const [activeStage, setActiveStage] = useState(currentStage);

  useEffect(() => {
    if (!autoProgress) {
      setActiveStage(currentStage);
      return;
    }

    const timer = setInterval(() => {
      setActiveStage((prev) => {
        if (prev < STAGES.length - 1) {
          return prev + 1;
        } else {
          clearInterval(timer);
          if (onComplete) onComplete();
          return prev;
        }
      });
    }, intervalMs);

    return () => clearInterval(timer);
  }, [autoProgress, intervalMs, onComplete, currentStage]);

  return (
    <div className="w-full max-w-xl mx-auto rounded-3xl bg-white/95 backdrop-blur-xl border border-slate-100 p-8 shadow-soft-lg">
      <div className="text-center mb-6">
        <span className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-purple-50 text-purple-700 border border-purple-200 mb-2">
          <span className="h-2 w-2 rounded-full bg-purple-600 animate-ping" />
          <span>Statutory AI Enforcement Pipeline</span>
        </span>
        <h3 className="text-xl font-bold font-display text-slate-800">
          Autonomous Label Verification Active
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          Executing multi-stage forensic analysis according to Legal Metrology Rules, 2011
        </p>
      </div>

      {/* Progress Bar */}
      <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden mb-8">
        <motion.div
          className="h-full bg-gradient-to-r from-blue-600 via-purple-600 to-pink-500"
          initial={{ width: '0%' }}
          animate={{ width: `${((activeStage + 1) / STAGES.length) * 100}%` }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>

      {/* Step items */}
      <div className="space-y-3.5">
        {STAGES.map((stage, idx) => {
          const Icon = stage.icon;
          const isDone = idx < activeStage;
          const isCurrent = idx === activeStage;
          const isPending = idx > activeStage;

          return (
            <motion.div
              key={stage.label}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: isPending ? 0.4 : 1, x: 0 }}
              className={`flex items-center space-x-4 p-3 rounded-2xl border transition-all duration-300 ${
                isCurrent
                  ? `${stage.bg} shadow-sm scale-[1.02]`
                  : isDone
                  ? 'bg-emerald-50/40 border-emerald-100'
                  : 'bg-slate-50/50 border-slate-100'
              }`}
            >
              <div
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-colors ${
                  isCurrent
                    ? 'bg-white shadow-sm ' + stage.color
                    : isDone
                    ? 'bg-emerald-500 text-white'
                    : 'bg-slate-200 text-slate-400'
                }`}
              >
                {isDone ? (
                  <ShieldCheck className="h-5 w-5" />
                ) : (
                  <Icon className={`h-5 w-5 ${isCurrent ? 'animate-spin-slow' : ''}`} />
                )}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p
                    className={`text-sm font-semibold truncate ${
                      isCurrent
                        ? 'text-slate-900'
                        : isDone
                        ? 'text-emerald-900'
                        : 'text-slate-500'
                    }`}
                  >
                    {stage.label}
                  </p>
                  {isCurrent && (
                    <span className="text-xs font-bold text-primary-600 animate-pulse">
                      In Progress
                    </span>
                  )}
                  {isDone && (
                    <span className="text-xs font-semibold text-emerald-600">Complete</span>
                  )}
                </div>
                <p className="text-xs text-slate-500 truncate">{stage.subtext}</p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
export default PipelineLoader;
