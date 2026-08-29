import React, { useState, useRef, useEffect } from 'react';
import { Eye, EyeOff, Layers, Zap } from 'lucide-react';

export const BoundingBoxOverlay = ({
  imageUrl,
  boxes = [],
  highlightText = '',
  selectedSide = 'front',
  onSelectBox,
}) => {
  const [showBoxes, setShowBoxes] = useState(true);
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const [imgNaturalDim, setImgNaturalDim] = useState({ width: 1, height: 1 });
  const imgRef = useRef(null);

  const handleImageLoad = (e) => {
    setImgNaturalDim({
      width: e.target.naturalWidth || 800,
      height: e.target.naturalHeight || 600,
    });
  };

  // Check if box text matches highlighted declaration
  const isHighlighted = (boxText) => {
    if (!highlightText || !boxText) return false;
    const cleanHighlight = String(highlightText).toLowerCase().replace(/[^a-z0-9]/g, '');
    const cleanBox = String(boxText).toLowerCase().replace(/[^a-z0-9]/g, '');
    return cleanBox.includes(cleanHighlight) || cleanHighlight.includes(cleanBox);
  };

  return (
    <div className="relative rounded-2xl overflow-hidden border border-slate-200 bg-slate-950 shadow-inner group">
      {/* Controls Bar */}
      <div className="absolute top-3 right-3 z-20 flex items-center gap-2 bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-700/60 text-xs text-slate-300 shadow-lg">
        <button
          onClick={() => setShowBoxes(!showBoxes)}
          className="flex items-center gap-1.5 hover:text-amber-400 transition-colors font-medium"
          title="Toggle OCR Bounding Boxes"
        >
          {showBoxes ? <Eye className="w-3.5 h-3.5 text-amber-400" /> : <EyeOff className="w-3.5 h-3.5 text-slate-400" />}
          <span>{showBoxes ? 'OCR Spatial Grid ON' : 'Image Only'}</span>
        </button>
        <span className="text-slate-600">|</span>
        <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
          <Layers className="w-3 h-3 text-amber-500" />
          {boxes.length} Regions
        </span>
      </div>

      {/* Package Image Container */}
      <div className="relative w-full flex items-center justify-center p-2 min-h-[320px]">
        {imageUrl ? (
          <div className="relative inline-block max-w-full">
            <img
              ref={imgRef}
              src={imageUrl}
              alt={`Packaging ${selectedSide} side`}
              onLoad={handleImageLoad}
              className="max-h-[480px] w-auto object-contain rounded-lg block shadow-md"
            />

            {/* SVG Overlay for spatial bounding boxes */}
            {showBoxes && boxes.length > 0 && (
              <svg
                viewBox={`0 0 ${imgNaturalDim.width} ${imgNaturalDim.height}`}
                className="absolute inset-0 w-full h-full pointer-events-auto"
                style={{ shapeRendering: 'geometricPrecision' }}
              >
                {boxes.map((item, idx) => {
                  const pts = item.box;
                  if (!pts || pts.length < 4) return null;

                  const pointsString = pts.map((p) => `${p[0]},${p[1]}`).join(' ');
                  const highlighted = isHighlighted(item.text);
                  const isHovered = hoveredIndex === idx;

                  // Styling logic
                  const strokeColor = highlighted
                    ? '#f59e0b' // Amber for highlighted declaration
                    : isHovered
                    ? '#10b981' // Emerald on hover
                    : '#3b82f6'; // Blue default

                  const fillColor = highlighted
                    ? 'rgba(245, 158, 11, 0.28)'
                    : isHovered
                    ? 'rgba(16, 185, 129, 0.20)'
                    : 'rgba(59, 130, 246, 0.08)';

                  const strokeWidth = highlighted || isHovered ? 3 : 1.5;

                  return (
                    <g
                      key={idx}
                      className="cursor-pointer transition-all duration-150"
                      onMouseEnter={() => setHoveredIndex(idx)}
                      onMouseLeave={() => setHoveredIndex(null)}
                      onClick={() => onSelectBox && onSelectBox(item)}
                    >
                      <polygon
                        points={pointsString}
                        fill={fillColor}
                        stroke={strokeColor}
                        strokeWidth={strokeWidth}
                        strokeDasharray={highlighted ? 'none' : '4,2'}
                      />
                      {/* Floating tooltip on hover or highlight */}
                      {(isHovered || highlighted) && (
                        <g>
                          <rect
                            x={pts[0][0]}
                            y={Math.max(0, pts[0][1] - 22)}
                            width={Math.max(80, (item.text?.length || 5) * 8.5 + 40)}
                            height={18}
                            rx={4}
                            fill="#0f172a"
                            stroke={strokeColor}
                            strokeWidth={1}
                          />
                          <text
                            x={pts[0][0] + 5}
                            y={Math.max(13, pts[0][1] - 8)}
                            fill="#ffffff"
                            fontSize="11"
                            fontFamily="monospace"
                            fontWeight="bold"
                          >
                            {item.text?.slice(0, 24)} ({Math.round((item.confidence || 0.9) * 100)}%)
                          </text>
                        </g>
                      )}
                    </g>
                  );
                })}
              </svg>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center text-slate-500 py-16">
            <Zap className="w-8 h-8 text-slate-600 mb-2" />
            <p className="text-xs">No processed image available for this inspection side.</p>
          </div>
        )}
      </div>

      {/* Footer Info Ribbon */}
      <div className="bg-slate-900 px-4 py-2 text-[11px] font-mono text-slate-400 border-t border-slate-800 flex items-center justify-between">
        <span>Image Resolution: {imgNaturalDim.width} x {imgNaturalDim.height} px</span>
        <span className="text-amber-400 font-medium">Click any field in Declarations Matrix to locate pixel region</span>
      </div>
    </div>
  );
};
