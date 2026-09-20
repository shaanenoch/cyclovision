import React from 'react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend 
} from 'recharts';
import { TrendingUp, Wind, Gauge } from 'lucide-react';

export default function ForecastChart({ forecastPoints = [] }) {
  // Transform points for Recharts
  const data = forecastPoints.map(pt => ({
    hour: `+${pt.forecast_hour}h`,
    wind_kmph: pt.wind_speed_kmph,
    pressure_hpa: pt.pressure_hpa,
    category: pt.classification
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const pData = payload[0].payload;
      return (
        <div className="p-3 bg-navy-950 border border-navy-750 rounded-xl shadow-2xl text-xs font-mono space-y-1">
          <div className="font-bold text-white border-b border-navy-800 pb-1">
            Forecast Horizon: {label}
          </div>
          <div className="text-cyan-400 font-semibold">
            Category: {pData.category}
          </div>
          <div className="text-cyan-300">
            Wind Speed: <strong>{pData.wind_kmph} km/h</strong>
          </div>
          <div className="text-orange-400">
            Central Pressure: <strong>{pData.pressure_hpa} hPa</strong>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-5 shadow-2xl backdrop-blur-md">
      {/* Chart Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-navy-800 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-cyan-400" />
          <h3 className="text-base font-bold text-white tracking-tight">
            Wind Speed & Pressure Evolution Curves
          </h3>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-cyan-400 inline-block" />
            <span className="text-cyan-300">Wind Speed (km/h)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-orange-400 inline-block" />
            <span className="text-orange-300">Pressure (hPa)</span>
          </div>
        </div>
      </div>

      {/* Chart Area */}
      <div className="w-full h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />
            <XAxis 
              dataKey="hour" 
              stroke="#64748b" 
              tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'monospace' }} 
            />
            {/* Left YAxis: Wind Speed */}
            <YAxis 
              yAxisId="left"
              domain={['auto', 'auto']}
              stroke="#06b6d4" 
              tick={{ fill: '#06b6d4', fontSize: 11, fontFamily: 'monospace' }}
              label={{ value: 'Wind (km/h)', angle: -90, position: 'insideLeft', fill: '#06b6d4', fontSize: 10 }}
            />
            {/* Right YAxis: Pressure */}
            <YAxis 
              yAxisId="right"
              orientation="right"
              domain={['auto', 'auto']}
              stroke="#f97316" 
              tick={{ fill: '#f97316', fontSize: 11, fontFamily: 'monospace' }}
              label={{ value: 'Pressure (hPa)', angle: 90, position: 'insideRight', fill: '#f97316', fontSize: 10 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="wind_kmph" 
              stroke="#06b6d4" 
              strokeWidth={3} 
              dot={{ r: 5, fill: '#06b6d4', stroke: '#ffffff', strokeWidth: 1.5 }}
              activeDot={{ r: 7 }}
            />
            <Line 
              yAxisId="right"
              type="monotone" 
              dataKey="pressure_hpa" 
              stroke="#f97316" 
              strokeWidth={3} 
              dot={{ r: 5, fill: '#f97316', stroke: '#ffffff', strokeWidth: 1.5 }}
              activeDot={{ r: 7 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
