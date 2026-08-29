import React from 'react';
import { motion } from 'framer-motion';

export const RoleSelectCard = ({
  roleKey = 'inspector',
  title = 'Field Inspector',
  badge = 'On-Ground Enforcement',
  description = 'Conduct live retail label audits, slack-fill volumetrics, and instant challan issuance.',
  icon: Icon,
  colorScheme = 'blue', // 'blue', 'violet', 'amber', 'emerald'
  isSelected = false,
  onClick,
}) => {
  const schemes = {
    blue: {
      border: isSelected ? 'border-blue-500 ring-2 ring-blue-400/40 shadow-tinted-blue' : 'border-slate-100 hover:border-blue-200',
      iconBg: 'bg-blue-50 text-blue-600',
      badgeBg: 'bg-blue-50 text-blue-700 border-blue-200',
    },
    violet: {
      border: isSelected ? 'border-purple-500 ring-2 ring-purple-400/40 shadow-tinted-violet' : 'border-slate-100 hover:border-purple-200',
      iconBg: 'bg-purple-50 text-purple-600',
      badgeBg: 'bg-purple-50 text-purple-700 border-purple-200',
    },
    amber: {
      border: isSelected ? 'border-amber-500 ring-2 ring-amber-400/40 shadow-tinted-amber' : 'border-slate-100 hover:border-amber-200',
      iconBg: 'bg-amber-50 text-amber-600',
      badgeBg: 'bg-amber-50 text-amber-700 border-amber-200',
    },
    emerald: {
      border: isSelected ? 'border-emerald-500 ring-2 ring-emerald-400/40 shadow-tinted-emerald' : 'border-slate-100 hover:border-emerald-200',
      iconBg: 'bg-emerald-50 text-emerald-600',
      badgeBg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
  };

  const current = schemes[colorScheme] || schemes.blue;

  return (
    <motion.button
      type="button"
      whileHover={{ y: -4, scale: 1.01 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`relative w-full text-left rounded-3xl border bg-white p-5 transition-all duration-200 shadow-soft ${current.border}`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ${current.iconBg} shadow-sm`}>
          {Icon && <Icon className="h-6 w-6" />}
        </div>
        <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${current.badgeBg}`}>
          {badge}
        </span>
      </div>

      <h4 className="text-base font-bold font-display text-slate-900 mb-1">{title}</h4>
      <p className="text-xs text-slate-500 leading-relaxed">{description}</p>
    </motion.button>
  );
};
export default RoleSelectCard;
