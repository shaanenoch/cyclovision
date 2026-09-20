import React from 'react';
import { Sparkles, HelpCircle, Eye, Info } from 'lucide-react';

export default function HeatmapViewer({ heatmapUrl, method = 'Cloud-pattern saliency', caption }) {
  return (
    <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-4 shadow-xl backdrop-blur-md flex flex-col justify-between">
      <div>
        {/* Card Header with Explainability Tooltip */}
        <div className="flex items-center justify-between border-b border-navy-800 pb-2.5 mb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <h4 className="text-sm font-semibold text-slate-100">AI Detection Heatmap</h4>
            
            {/* Tooltip */}
            <div className="relative group/tooltip">
              <HelpCircle className="w-3.5 h-3.5 text-slate-400 hover:text-cyan-300 cursor-help" />
              <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 hidden group-hover/tooltip:block w-56 p-2 rounded-lg bg-navy-950 border border-navy-750 text-[11px] font-normal text-slate-200 shadow-2xl z-50 text-center">
                Highlights image regions used by the active analysis method.
                <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-navy-950" />
              </div>
            </div>
          </div>

          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/50">
            {method}
          </span>
        </div>

        {/* Heatmap Image Container */}
        <div className="relative w-full aspect-square rounded-xl overflow-hidden bg-navy-950 border border-navy-800 flex items-center justify-center">
          <img
            src={heatmapUrl || '/uploads/demo_cyclone_01_heat.png'}
            alt="AI Attention Heatmap"
            className="w-full h-full object-cover"
          />

          {/* Color Gradient Legend Bar */}
          <div className="absolute top-2 right-2 flex items-center gap-1.5 px-2 py-1 rounded bg-navy-950/80 backdrop-blur-sm border border-navy-800 text-[10px] font-mono text-slate-300">
            <span>Low</span>
            <div className="w-16 h-2 rounded-full bg-gradient-to-r from-blue-600 via-cyan-400 via-yellow-400 to-red-600" />
            <span>Peak</span>
          </div>
        </div>
      </div>

      {/* Mandatory Required Explainability Caption */}
      <div className="mt-3 pt-2.5 border-t border-navy-800/80 space-y-1.5">
        <p className="text-xs text-cyan-300/90 font-medium leading-relaxed">
          {caption || 'Highlighted regions indicate cloud structures used by the active analysis method.'}
        </p>
        <p className="text-[10px] text-slate-400 leading-tight">
          Grad-CAM is shown only when a trained neural checkpoint is loaded; otherwise this card is labelled as a computer-vision saliency fallback.
        </p>
      </div>
    </div>
  );
}
