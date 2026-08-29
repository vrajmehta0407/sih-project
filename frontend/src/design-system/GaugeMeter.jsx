import React from 'react';
import { motion } from 'framer-motion';

export const GaugeMeter = ({
  value = 85,
  max = 100,
  label = 'Quality Index',
  size = 180,
  strokeWidth = 14,
  variant = 'blue', // 'blue', 'emerald', 'amber', 'rose'
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  const radius = (size - strokeWidth * 2) / 2;
  const circumference = Math.PI * radius; // Half circle
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const colors = {
    blue: {
      gradientId: 'gaugeBlueGrad',
      start: '#3B82F6',
      end: '#8B5CF6',
      track: '#E2E8F0',
      text: 'text-blue-600',
    },
    emerald: {
      gradientId: 'gaugeEmeraldGrad',
      start: '#10B981',
      end: '#059669',
      track: '#E2E8F0',
      text: 'text-emerald-600',
    },
    amber: {
      gradientId: 'gaugeAmberGrad',
      start: '#F59E0B',
      end: '#D97706',
      track: '#E2E8F0',
      text: 'text-amber-600',
    },
    rose: {
      gradientId: 'gaugeRoseGrad',
      start: '#EF4444',
      end: '#B91C1C',
      track: '#E2E8F0',
      text: 'text-rose-600',
    },
  };

  const c = colors[variant] || colors.blue;

  return (
    <div className="relative flex flex-col items-center justify-center">
      <svg width={size} height={size / 1.7} viewBox={`0 0 ${size} ${size / 1.7}`}>
        <defs>
          <linearGradient id={c.gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={c.start} />
            <stop offset="100%" stopColor={c.end} />
          </linearGradient>
        </defs>

        {/* Background track (semi-circle) */}
        <path
          d={`M ${strokeWidth},${size / 1.7 - 5} A ${radius},${radius} 0 0,1 ${size - strokeWidth},${size / 1.7 - 5}`}
          fill="none"
          stroke={c.track}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Animated fill stroke */}
        <motion.path
          d={`M ${strokeWidth},${size / 1.7 - 5} A ${radius},${radius} 0 0,1 ${size - strokeWidth},${size / 1.7 - 5}`}
          fill="none"
          stroke={`url(#${c.gradientId})`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.4, ease: [0.16, 1, 0.3, 1] }}
        />
      </svg>

      {/* Center value overlay */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/4 text-center">
        <span className={`text-2xl font-bold font-display tracking-tight ${c.text}`}>
          {Math.round(percentage)}%
        </span>
        {label && <p className="text-xs text-slate-500 font-medium">{label}</p>}
      </div>
    </div>
  );
};
export default GaugeMeter;
