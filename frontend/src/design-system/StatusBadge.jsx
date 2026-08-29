import React from 'react';
import { motion } from 'framer-motion';

export const StatusBadge = ({
  status = 'COMPLIANT',
  label,
  size = 'md', // 'sm', 'md', 'lg'
  pulse = true,
  className = '',
}) => {
  const norm = String(status).toUpperCase();

  const configs = {
    COMPLIANT: {
      bg: 'bg-emerald-50 text-emerald-700 border-emerald-200 shadow-sm',
      dot: 'bg-emerald-500',
      label: label || 'COMPLIANT',
    },
    SETTLED: {
      bg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      dot: 'bg-emerald-500',
      label: label || 'SETTLED',
    },
    NON_COMPLIANT: {
      bg: 'bg-rose-50 text-rose-700 border-rose-200 shadow-sm',
      dot: 'bg-rose-500',
      label: label || 'VIOLATION FLAGGED',
    },
    VIOLATION: {
      bg: 'bg-rose-50 text-rose-700 border-rose-200',
      dot: 'bg-rose-500',
      label: label || 'VIOLATION',
    },
    SUSPECT: {
      bg: 'bg-amber-50 text-amber-800 border-amber-200 shadow-sm',
      dot: 'bg-amber-500',
      label: label || 'UNDER REVIEW',
    },
    UNDER_REVIEW: {
      bg: 'bg-amber-50 text-amber-800 border-amber-200',
      dot: 'bg-amber-500',
      label: label || 'UNDER REVIEW',
    },
    PENDING: {
      bg: 'bg-sky-50 text-sky-700 border-sky-200',
      dot: 'bg-sky-500',
      label: label || 'PENDING',
    },
    AI_VERIFIED: {
      bg: 'bg-purple-50 text-purple-700 border-purple-200 shadow-sm',
      dot: 'bg-purple-500',
      label: label || 'AI VERIFIED',
    },
  };

  const config = configs[norm] || {
    bg: 'bg-slate-100 text-slate-700 border-slate-200',
    dot: 'bg-slate-400',
    label: label || status,
  };

  const sizeClasses = {
    sm: 'text-xs px-2.5 py-0.5 space-x-1.5 font-medium',
    md: 'text-xs px-3 py-1 space-x-2 font-semibold',
    lg: 'text-sm px-4 py-1.5 space-x-2.5 font-semibold',
  };

  return (
    <motion.span
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className={`inline-flex items-center rounded-full border transition-colors ${config.bg} ${sizeClasses[size] || sizeClasses.md} ${className}`}
    >
      <span className="relative flex h-2 w-2">
        {pulse && (
          <span
            className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 ${config.dot}`}
          />
        )}
        <span className={`relative inline-flex h-2 w-2 rounded-full ${config.dot}`} />
      </span>
      <span>{config.label}</span>
    </motion.span>
  );
};
export default StatusBadge;
