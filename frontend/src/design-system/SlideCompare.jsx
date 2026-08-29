import React, { useState, useRef, useCallback } from 'react';

export const SlideCompare = ({
  beforeImage,
  afterImage,
  beforeLabel = 'Original Evidence',
  afterLabel = 'Forensic ELA Heatmap',
  className = '',
}) => {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef(null);

  const handleMove = useCallback((clientX) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
    const percent = Math.max(0, Math.min((x / rect.width) * 100, 100));
    setSliderPosition(percent);
  }, []);

  const handleTouchMove = (e) => {
    if (!isDragging) return;
    handleMove(e.touches[0].clientX);
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    handleMove(e.clientX);
  };

  return (
    <div
      ref={containerRef}
      className={`relative select-none overflow-hidden rounded-2xl border border-slate-200 bg-slate-100 ${className}`}
      onMouseDown={() => setIsDragging(true)}
      onMouseUp={() => setIsDragging(false)}
      onMouseLeave={() => setIsDragging(false)}
      onMouseMove={handleMouseMove}
      onTouchStart={() => setIsDragging(true)}
      onTouchEnd={() => setIsDragging(false)}
      onTouchMove={handleTouchMove}
    >
      {/* After image (Forensic/Processed) - Full width */}
      <img
        src={afterImage}
        alt={afterLabel}
        className="w-full h-auto object-contain block max-h-[500px] pointer-events-none"
      />
      <div className="absolute top-3 right-3 rounded-full bg-purple-900/80 backdrop-blur-sm px-3 py-1 text-xs font-semibold text-white shadow">
        {afterLabel}
      </div>

      {/* Before image (Original) - Clipped by slider */}
      <div
        className="absolute inset-0 overflow-hidden pointer-events-none"
        style={{ width: `${sliderPosition}%` }}
      >
        <img
          src={beforeImage}
          alt={beforeLabel}
          className="w-full h-auto object-contain block max-h-[500px] pointer-events-none"
          style={{ width: containerRef.current ? `${containerRef.current.clientWidth}px` : '100%', maxWidth: 'none' }}
        />
        <div className="absolute top-3 left-3 rounded-full bg-slate-900/80 backdrop-blur-sm px-3 py-1 text-xs font-semibold text-white shadow">
          {beforeLabel}
        </div>
      </div>

      {/* Slider divider line and handle */}
      <div
        className="absolute top-0 bottom-0 w-1 bg-white shadow-xl cursor-ew-resize flex items-center justify-center -ml-0.5"
        style={{ left: `${sliderPosition}%` }}
      >
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white shadow-lg border-2 border-primary-600 text-primary-600 font-bold text-xs">
          ↔
        </div>
      </div>
    </div>
  );
};
export default SlideCompare;
