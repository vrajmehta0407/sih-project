import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, Loader2 } from 'lucide-react';

export const ButtonLoader = ({
  children,
  loading = false,
  success = false,
  variant = 'primary', // 'primary', 'secondary', 'danger', 'emerald'
  size = 'md',
  className = '',
  disabled,
  onClick,
  ...props
}) => {
  const variantStyles = {
    primary: 'bg-primary-600 hover:bg-primary-700 text-white shadow-tinted-blue',
    secondary: 'bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 shadow-soft',
    gradient: 'bg-gradient-to-r from-blue-600 via-purple-600 to-pink-500 hover:opacity-95 text-white shadow-tinted-violet',
    emerald: 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-tinted-emerald',
    danger: 'bg-rose-600 hover:bg-rose-700 text-white shadow-tinted-red',
  };

  const sizeStyles = {
    sm: 'text-xs px-3.5 py-1.5 rounded-xl font-medium',
    md: 'text-sm px-5 py-2.5 rounded-2xl font-semibold',
    lg: 'text-base px-6 py-3 rounded-2xl font-bold',
  };

  return (
    <motion.button
      whileHover={!disabled && !loading ? { scale: 1.02 } : undefined}
      whileTap={!disabled && !loading ? { scale: 0.97 } : undefined}
      disabled={disabled || loading}
      onClick={onClick}
      className={`relative inline-flex items-center justify-center transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed ${variantStyles[variant] || variantStyles.primary} ${sizeStyles[size] || sizeStyles.md} ${className}`}
      {...props}
    >
      <AnimatePresence mode="wait" initial={false}>
        {success ? (
          <motion.span
            key="success"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.5, opacity: 0 }}
            className="flex items-center space-x-1.5"
          >
            <Check className="h-4 w-4 stroke-[3]" />
            <span>Done</span>
          </motion.span>
        ) : loading ? (
          <motion.span
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center space-x-2"
          >
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Processing...</span>
          </motion.span>
        ) : (
          <motion.span
            key="content"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center space-x-2"
          >
            {children}
          </motion.span>
        )}
      </AnimatePresence>
    </motion.button>
  );
};
export default ButtonLoader;
