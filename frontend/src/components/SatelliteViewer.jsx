import React, { useState } from 'react';
import { Satellite, ZoomIn, Eye, Sparkles } from 'lucide-react';

export default function SatelliteViewer({ imageUrl, timestamp = 'Live Synoptic Frame', channel = 'IR (TIR-1)' }) {
  const [filter, setFilter] = useState('normal'); // 'normal', 'contrast', 'invert'

  const getFilterClass = () => {
    if (filter === 'contrast') return 'contrast-125 brightness-110';
    if (filter === 'invert') return 'invert';
    return '';
  };

  return (
    <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-4 shadow-xl backdrop-blur-md flex flex-col justify-between">
      <div>
        {/* Card Header */}
        <div className="flex items-center justify-between border-b border-navy-800 pb-2.5 mb-3">
          <div className="flex items-center gap-2">
            <Satellite className="w-4 h-4 text-cyan-400" />
            <h4 className="text-sm font-semibold text-slate-100">Original Satellite Image</h4>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-navy-950 text-cyan-300 border border-navy-800">
            {channel}
          </span>
        </div>

        {/* Image Display */}
        <div className="relative w-full aspect-square rounded-xl overflow-hidden bg-navy-950 border border-navy-800 flex items-center justify-center group">
          <img
            src={imageUrl || '/uploads/demo_cyclone_01_sat.png'}
            alt="Original Satellite Imagery"
            className={`w-full h-full object-cover transition-all duration-300 ${getFilterClass()}`}
          />

          {/* Timestamp overlay */}
          <div className="absolute bottom-2 left-2 px-2 py-1 rounded bg-navy-950/80 backdrop-blur-sm border border-navy-800 text-[10px] font-mono text-slate-300">
            {timestamp}
          </div>

          {/* Eye Reticle overlay on hover */}
          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
            <div className="w-16 h-16 rounded-full border border-dashed border-cyan-400/80 animate-spin-slow flex items-center justify-center">
              <div className="w-2 h-2 rounded-full bg-cyan-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Filter and enhancement controls */}
      <div className="mt-3 pt-2.5 border-t border-navy-800/80 flex items-center justify-between text-xs">
        <span className="text-slate-400 text-[11px]">Filter Mode:</span>
        <div className="flex items-center gap-1 bg-navy-950 p-0.5 rounded-lg border border-navy-800">
          <button
            onClick={() => setFilter('normal')}
            className={`px-2 py-0.5 rounded text-[11px] font-mono ${filter === 'normal' ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400'}`}
          >
            Raw
          </button>
          <button
            onClick={() => setFilter('contrast')}
            className={`px-2 py-0.5 rounded text-[11px] font-mono ${filter === 'contrast' ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400'}`}
          >
            CLAHE
          </button>
        </div>
      </div>
    </div>
  );
}
