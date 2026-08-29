import React from 'react';
import { motion } from 'framer-motion';

export const GlassCard = ({
  children,
  className = '',
  variant = 'default', // 'default', 'blue', 'violet', 'emerald', 'amber', 'rose'
  hoverEffect = true,
  onClick,
  ...props
}) => {
  const variantStyles = {
    default: 'bg-white border-slate-100 shadow-soft hover:shadow-soft-lg',
    blue: 'bg-gradient-to-br from-white via-blue-50/40 to-blue-100/30 border-blue-200/80 shadow-tinted-blue',
    violet: 'bg-gradient-to-br from-white via-purple-50/40 to-purple-100/30 border-purple-200/80 shadow-tinted-violet',
    emerald: 'bg-gradient-to-br from-white via-emerald-50/40 to-emerald-100/30 border-emerald-200/80 shadow-tinted-emerald',
    amber: 'bg-gradient-to-br from-white via-amber-50/40 to-amber-100/30 border-amber-200/80 shadow-tinted-amber',
    rose: 'bg-gradient-to-br from-white via-rose-50/40 to-rose-100/30 border-rose-200/80 shadow-tinted-red',
    frosted: 'glass-panel border-white/70 shadow-soft',
  };

  const selectedVariant = variantStyles[variant] || variantStyles.default;

  return (
    <motion.div
      whileHover={hoverEffect ? { y: -4, transition: { duration: 0.2, ease: [0.16, 1, 0.3, 1] } } : undefined}
      whileTap={onClick ? { scale: 0.985 } : undefined}
      onClick={onClick}
      className={`relative rounded-3xl border p-6 transition-all duration-300 ${selectedVariant} ${className}`}
      {...props}
    >
      {children}
    </motion.div>
  );
};
export default GlassCard;
