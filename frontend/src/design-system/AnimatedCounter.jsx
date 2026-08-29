import React, { useEffect, useState, useRef } from 'react';
import { useInView } from 'framer-motion';

export const AnimatedCounter = ({
  value = 0,
  duration = 1.6,
  prefix = '',
  suffix = '',
  decimals = 0,
  className = '',
}) => {
  const [displayValue, setDisplayValue] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-20px' });
  const startValue = useRef(0);

  useEffect(() => {
    if (!isInView) return;

    let startTime = null;
    const target = typeof value === 'number' ? value : parseFloat(value) || 0;
    const initial = startValue.current;

    const step = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / (duration * 1000), 1);
      // easeOutExpo
      const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      const current = initial + (target - initial) * ease;

      setDisplayValue(current);

      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        setDisplayValue(target);
        startValue.current = target;
      }
    };

    requestAnimationFrame(step);
  }, [value, duration, isInView]);

  const formatted = displayValue.toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  return (
    <span ref={ref} className={`tabular-nums font-display ${className}`}>
      {prefix}{formatted}{suffix}
    </span>
  );
};
export default AnimatedCounter;
