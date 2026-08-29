import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

export const TopProgressBar = () => {
  const location = useLocation();
  const [progress, setProgress] = useState(0);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setVisible(true);
    setProgress(30);

    const timer1 = setTimeout(() => setProgress(75), 100);
    const timer2 = setTimeout(() => setProgress(100), 300);
    const timer3 = setTimeout(() => {
      setVisible(false);
      setProgress(0);
    }, 550);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [location.pathname]);

  if (!visible) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 h-[3px] bg-slate-100 overflow-hidden pointer-events-none">
      <div
        className="h-full bg-gradient-to-r from-blue-600 via-purple-600 to-pink-500 transition-all duration-300 ease-out shadow-sm"
        style={{ width: `${progress}%` }}
      />
    </div>
  );
};
export default TopProgressBar;
