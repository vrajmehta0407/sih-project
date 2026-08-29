import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, Sparkles, ArrowRight } from 'lucide-react';
import ScrambleText from './ScrambleText';

export const WelcomeInterstitial = ({
  user,
  onComplete,
  duration = 2200,
}) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      if (onComplete) onComplete();
    }, duration);
    return () => clearTimeout(timer);
  }, [duration, onComplete]);

  const roleLabels = {
    INSPECTOR: 'Field Enforcement Officer',
    SUPERVISOR: 'Zonal Controller',
    DIRECTOR: 'Enforcement Director',
    ADMIN: 'System Administrator',
    CITIZEN: 'Consumer Rights Advocate',
  };

  const roleTitle = roleLabels[user?.role] || user?.role || 'Enforcement Officer';
  const name = user?.full_name || user?.email || 'Officer';

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0, scale: 0.98, transition: { duration: 0.4 } }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-md p-4"
      >
        <motion.div
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.95, opacity: 0 }}
          transition={{ ease: [0.16, 1, 0.3, 1], duration: 0.5 }}
          className="relative w-full max-w-lg rounded-3xl border border-white/40 bg-gradient-to-br from-white via-white to-blue-50/90 p-8 shadow-2xl text-center overflow-hidden"
        >
          {/* Decorative background glow */}
          <div className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-purple-500/15 blur-3xl" />
          <div className="absolute -left-16 -bottom-16 h-48 w-48 rounded-full bg-blue-500/15 blur-3xl" />

          {/* Animated Shield / Icon */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', damping: 12, stiffness: 200, delay: 0.1 }}
            className="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-tr from-blue-600 to-purple-600 text-white shadow-tinted-blue"
          >
            <ShieldCheck className="h-10 w-10 stroke-[2.2]" />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center space-x-1.5 rounded-full bg-blue-50 border border-blue-200 px-3.5 py-1 text-xs font-semibold text-blue-700 mb-3"
          >
            <Sparkles className="h-3.5 w-3.5 text-blue-600" />
            <span>Identity Authenticated · Legal Metrology Act, 2009</span>
          </motion.div>

          <h2 className="text-2xl font-bold font-display text-slate-900 mb-1">
            Welcome back, {name}
          </h2>

          <div className="text-sm font-medium text-purple-700 mb-6">
            <ScrambleText text={`Role: ${roleTitle} · Jurisdiction: Western Zone`} duration={0.8} />
          </div>

          {/* Mini Summary Card */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="rounded-2xl border border-slate-100 bg-white/80 p-4 shadow-sm mb-6 flex items-center justify-around text-center"
          >
            <div>
              <p className="text-xs text-slate-500 font-medium">Pending Dockets</p>
              <p className="text-lg font-bold font-display text-blue-600">3 Active</p>
            </div>
            <div className="h-8 w-px bg-slate-200" />
            <div>
              <p className="text-xs text-slate-500 font-medium">Notices Due</p>
              <p className="text-lg font-bold font-display text-amber-600">1 Today</p>
            </div>
            <div className="h-8 w-px bg-slate-200" />
            <div>
              <p className="text-xs text-slate-500 font-medium">Compliance Rate</p>
              <p className="text-lg font-bold font-display text-emerald-600">94.2%</p>
            </div>
          </motion.div>

          <button
            onClick={onComplete}
            className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-500 hover:text-slate-800 transition-colors"
          >
            <span>Entering Command Center</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
export default WelcomeInterstitial;
