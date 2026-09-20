import React from 'react';
import { Wind, Compass, Gauge, AlertTriangle, ShieldCheck, MapPin, Clock, ArrowUpRight } from 'lucide-react';

export default function CycloneInfoPanel({ cyclone, onTriggerAnalyze, loading }) {
  const currentLat = cyclone?.current_lat || 15.2;
  const currentLon = cyclone?.current_lon || 84.7;
  const windKmph = cyclone?.wind_speed_kmph || 115;
  const windKts = Math.round(windKmph / 1.852);
  const pressure = cyclone?.pressure_hpa || 978;
  const status = cyclone?.status || 'Severe Cyclonic Storm';

  return (
    <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-5 shadow-2xl backdrop-blur-md flex flex-col justify-between h-full">
      <div>
        {/* Header Tag */}
        <div className="flex items-center justify-between border-b border-navy-800 pb-3">
          <div>
            <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 font-semibold">
              Tropical Cyclone Bulletin
            </span>
            <h3 className="text-xl font-bold text-white tracking-tight flex items-center gap-2 mt-0.5">
              <span>{cyclone?.name || 'Demo Cyclone 01'}</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-orange-950 text-orange-400 border border-orange-800 font-medium">
                Active
              </span>
            </h3>
          </div>

          <div className="text-right">
            <span className="text-[10px] text-slate-400 block font-mono">Basin</span>
            <span className="text-xs text-slate-200 font-semibold">North Indian Ocean</span>
          </div>
        </div>

        {/* Meteorological Parameters Grid */}
        <div className="grid grid-cols-2 gap-3 my-4">
          <div className="p-3 rounded-xl bg-navy-950/70 border border-navy-800">
            <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
              <MapPin className="w-3.5 h-3.5 text-cyan-400" />
              <span>Center Coordinates</span>
            </div>
            <div className="text-sm font-bold font-mono text-slate-100">
              {currentLat.toFixed(1)}°N, {currentLon.toFixed(1)}°E
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-0.5">
              Bay of Bengal
            </div>
          </div>

          <div className="p-3 rounded-xl bg-navy-950/70 border border-navy-800">
            <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
              <Wind className="w-3.5 h-3.5 text-cyan-400" />
              <span>Max Sustained Wind</span>
            </div>
            <div className="text-sm font-bold font-mono text-slate-100">
              {windKmph} km/h
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-0.5">
              {windKts} knots • 3-min avg
            </div>
          </div>

          <div className="p-3 rounded-xl bg-navy-950/70 border border-navy-800">
            <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
              <Gauge className="w-3.5 h-3.5 text-cyan-400" />
              <span>Central Pressure</span>
            </div>
            <div className="text-sm font-bold font-mono text-slate-100">
              {pressure} hPa
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-0.5">
              Estimated eye minimum
            </div>
          </div>

          <div className="p-3 rounded-xl bg-navy-950/70 border border-navy-800">
            <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
              <Compass className="w-3.5 h-3.5 text-cyan-400" />
              <span>Current Movement</span>
            </div>
            <div className="text-sm font-bold font-mono text-slate-100">
              {cyclone?.movement_direction || 'North-West'}
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-0.5">
              Translation: {cyclone?.movement_speed_kmph || 18.5} km/h
            </div>
          </div>
        </div>

        {/* Nearest Landfall Risk & Advisory Note */}
        <div className="p-3.5 rounded-xl bg-navy-950/80 border border-navy-800 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 font-mono">Nearest Coastal Hub:</span>
            <span className="text-cyan-300 font-semibold font-mono">
              {cyclone?.nearest_coastal_point || 'Visakhapatnam (~270 km NW)'}
            </span>
          </div>

          <div className="text-xs text-slate-300 leading-relaxed pt-2 border-t border-navy-850">
            <strong className="text-amber-400 font-semibold">Estimated Trajectory: </strong>
            <span>
              {cyclone?.estimated_trajectory_summary || 
                'Expected track towards the north-western Bay of Bengal, approaching Andhra Pradesh and South Odisha coast.'}
            </span>
          </div>
        </div>
      </div>

      {/* Footer Disclaimer & Trigger Button */}
      <div className="mt-4 pt-3 border-t border-navy-800 space-y-3">
        {/* Strict Mandatory Disclaimer */}
        <div className="p-2.5 rounded-lg bg-amber-950/30 border border-amber-800/40 text-[11px] text-amber-300/90 flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Disclaimer:</strong> Research prototype for cyclone analysis. 
            Forecast outputs must not replace official meteorological warnings.
          </span>
        </div>

        <button
          onClick={onTriggerAnalyze}
          disabled={loading}
          className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-navy-950 font-bold text-xs tracking-wider uppercase shadow-glow-cyan flex items-center justify-center gap-2 transition-all"
        >
          <ArrowUpRight className="w-4 h-4" />
          <span>{loading ? 'Processing Satellite Neural Pass...' : 'Run Full AI Diagnostic Pipeline'}</span>
        </button>
      </div>
    </div>
  );
}
