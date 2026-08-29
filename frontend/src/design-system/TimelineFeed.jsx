import React from 'react';
import { motion } from 'framer-motion';

export const TimelineFeed = ({ items = [], className = '' }) => {
  return (
    <div className={`relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-gradient-to-b before:from-blue-500 before:via-purple-500 before:to-emerald-400 ${className}`}>
      {items.map((item, index) => (
        <motion.div
          key={item.id || index}
          initial={{ opacity: 0, x: -16 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.08, duration: 0.3 }}
          className="relative group"
        >
          {/* Timeline Dot */}
          <div className="absolute -left-6 top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-white border-2 border-primary-600 shadow-sm group-hover:scale-125 transition-transform duration-200">
            <div className="h-2 w-2 rounded-full bg-primary-600" />
          </div>

          <div className="rounded-2xl border border-slate-100 bg-white p-4 shadow-soft hover:shadow-soft-lg transition-all duration-200">
            <div className="flex items-center justify-between gap-2 mb-1">
              <span className="font-semibold text-sm text-slate-800">{item.title}</span>
              <span className="text-xs text-slate-400">{item.timestamp}</span>
            </div>
            {item.description && (
              <p className="text-xs text-slate-600 leading-relaxed">{item.description}</p>
            )}
            {item.badge && <div className="mt-2">{item.badge}</div>}
          </div>
        </motion.div>
      ))}
    </div>
  );
};
export default TimelineFeed;
