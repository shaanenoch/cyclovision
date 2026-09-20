import React from 'react';
import { HelpCircle, Clock, MapPin, Wind, Gauge, Compass } from 'lucide-react';

export default function ForecastTable({ forecastPoints = [], onSelectPoint }) {
  return (
    <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-5 shadow-2xl backdrop-blur-md">
      {/* Table Header with Tooltip */}
      <div className="flex items-center justify-between border-b border-navy-800 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-cyan-400" />
          <h3 className="text-base font-bold text-white tracking-tight">
            Numerical Track & Intensity Projection
          </h3>

          {/* Tooltip */}
          <div className="relative group/tooltip">
            <HelpCircle className="w-3.5 h-3.5 text-slate-400 hover:text-cyan-300 cursor-help" />
            <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 hidden group-hover/tooltip:block w-64 p-2 rounded-lg bg-navy-950 border border-navy-750 text-[11px] font-normal text-slate-200 shadow-2xl z-50 text-center">
              Estimated future movement based on previous cyclone observations.
              <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-navy-950" />
            </div>
          </div>
        </div>

        <span className="text-xs font-mono text-cyan-400 bg-cyan-950/80 px-2.5 py-1 rounded-lg border border-cyan-800/50">
          5 Synoptic Fixes (+48h Horizon)
        </span>
      </div>

      {/* Responsive Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-navy-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <th className="py-2.5 px-3">Horizon</th>
              <th className="py-2.5 px-3">Forecast Fix</th>
              <th className="py-2.5 px-3">Intensity Category</th>
              <th className="py-2.5 px-3">Wind Speed</th>
              <th className="py-2.5 px-3">Central Pressure</th>
              <th className="py-2.5 px-3">Uncertainty Metric</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-navy-800/60">
            {forecastPoints.map((pt, idx) => {
              const windKts = Math.round(pt.wind_speed_kmph / 1.852);
              return (
                <tr
                  key={idx}
                  onClick={() => onSelectPoint && onSelectPoint({ lat: pt.latitude, lon: pt.longitude })}
                  className="hover:bg-navy-800/50 transition-colors cursor-pointer group"
                >
                  <td className="py-3 px-3 font-bold text-cyan-400 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-orange-500" />
                    +{pt.forecast_hour} hr
                  </td>
                  <td className="py-3 px-3 text-slate-200 font-semibold">
                    {pt.latitude.toFixed(2)}°N, {pt.longitude.toFixed(2)}°E
                  </td>
                  <td className="py-3 px-3">
                    <span 
                      className="px-2 py-0.5 rounded-full text-[11px] font-semibold"
                      style={{ 
                        backgroundColor: `${pt.category_color || '#f97316'}20`, 
                        color: pt.category_color || '#f97316',
                        border: `1px solid ${pt.category_color || '#f97316'}40`
                      }}
                    >
                      {pt.classification}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-200">
                    <strong>{pt.wind_speed_kmph} km/h</strong> <span className="text-slate-400">({windKts} kts)</span>
                  </td>
                  <td className="py-3 px-3 text-slate-200">
                    {pt.pressure_hpa} hPa
                  </td>
                  <td className="py-3 px-3">
                    <span className="px-2 py-0.5 rounded bg-navy-950 text-slate-400 border border-navy-800 text-[10px]">
                      {pt.confidence_label || 'model estimate'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-3 pt-2 text-[11px] text-slate-400 text-right font-mono">
        * Click any forecast row to zoom to the projected coordinate on the map.
      </div>
    </div>
  );
}
