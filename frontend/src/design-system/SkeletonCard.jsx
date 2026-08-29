import React from 'react';

export const SkeletonCard = ({
  className = '',
  variant = 'blue', // 'blue', 'violet', 'default'
  lines = 3,
}) => {
  const shimmerGradients = {
    default: 'from-slate-100 via-slate-200/70 to-slate-100',
    blue: 'from-blue-50/50 via-blue-100/60 to-blue-50/50',
    violet: 'from-purple-50/50 via-purple-100/60 to-purple-50/50',
  };

  const grad = shimmerGradients[variant] || shimmerGradients.default;

  return (
    <div className={`rounded-3xl border border-slate-100 bg-white p-6 shadow-soft overflow-hidden ${className}`}>
      {/* Header shimmer */}
      <div className="flex items-center space-x-4 mb-4">
        <div className={`h-12 w-12 rounded-2xl bg-gradient-to-r ${grad} animate-shimmer bg-[length:200%_100%]`} />
        <div className="space-y-2 flex-1">
          <div className={`h-4 w-3/4 rounded-md bg-gradient-to-r ${grad} animate-shimmer bg-[length:200%_100%]`} />
          <div className={`h-3 w-1/2 rounded-md bg-gradient-to-r ${grad} animate-shimmer bg-[length:200%_100%]`} />
        </div>
      </div>

      {/* Lines shimmer */}
      <div className="space-y-2.5 pt-2">
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={`h-3 rounded-md bg-gradient-to-r ${grad} animate-shimmer bg-[length:200%_100%]`}
            style={{ width: `${85 - i * 15}%` }}
          />
        ))}
      </div>
    </div>
  );
};
export default SkeletonCard;
