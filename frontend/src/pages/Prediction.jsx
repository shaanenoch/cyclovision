import React, { useState } from 'react';
import { Compass, Play, RotateCcw, MapPin, Wind, Gauge, ShieldAlert, Sparkles } from 'lucide-react';
import api from '../services/api';
import CycloneMap from '../components/CycloneMap';
import ForecastTable from '../components/ForecastTable';
import ForecastChart from '../components/ForecastChart';

export default function Prediction() {
  const [lat, setLat] = useState(15.2);
  const [lon, setLon] = useState(84.7);
  const [wind, setWind] = useState(115.0);
  const [pressure, setPressure] = useState(978.0);
  const [bearing, setBearing] = useState(315.0);
  const [speed, setSpeed] = useState(18.5);
  const [loading, setLoading] = useState(false);
  const [predictionData, setPredictionData] = useState(null);

  const handlePredict = async () => {
    setLoading(true);
    try {
      const res = await api.predictTrack({
        cyclone_name: "Trajectory Simulation Target",
        current_lat: parseFloat(lat),
        current_lon: parseFloat(lon),
        wind_speed_kmph: parseFloat(wind),
        pressure_hpa: parseFloat(pressure),
        movement_bearing_deg: parseFloat(bearing),
        movement_speed_kmph: parseFloat(speed)
      });
      setPredictionData(res);
    } catch (err) {
      console.error("Prediction error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Convert bearing degrees to human-readable compass
  const getCompassDir = (deg) => {
    const directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
    const idx = Math.round(deg / 22.5) % 16;
    return directions[idx];
  };

  // Build synthetic cyclone object for the map
  const activeMapCyclone = {
    name: "Simulation Target",
    status: wind >= 118 ? "Very Severe Cyclonic Storm" : "Severe Cyclonic Storm",
    current_lat: parseFloat(lat),
    current_lon: parseFloat(lon),
    wind_speed_kmph: parseFloat(wind),
    pressure_hpa: parseFloat(pressure),
    movement_direction: getCompassDir(bearing),
    movement_speed_kmph: parseFloat(speed),
    track_points: predictionData?.forecast?.map(p => ({
      ...p,
      point_type: 'forecast'
    })) || []
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Page Header */}
      <div className="text-center max-w-2xl mx-auto">
        <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          Numerical Track & Intensity Simulator
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 font-sans mt-1">
          Generate 48-hour forecasts using a model trained on NOAA IBTrACS North Indian Ocean tracks, with validation-derived uncertainty radii.
        </p>
      </div>

      {/* Interactive Controls & Parameters Grid */}
      <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-6 shadow-2xl backdrop-blur-md">
        <div className="flex items-center justify-between border-b border-navy-800 pb-3 mb-5">
          <div className="flex items-center gap-2">
            <Compass className="w-5 h-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider">
              Synoptic Boundary Conditions
            </h3>
          </div>
          <span className="text-[11px] font-mono text-cyan-400">
            Bearing: {bearing}° ({getCompassDir(bearing)})
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 font-mono text-xs">
          {/* Latitude & Longitude */}
          <div>
            <label className="block text-slate-400 mb-1">Current Latitude (°N)</label>
            <input
              type="number"
              step="0.1"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              className="w-full py-2 px-3 rounded-xl bg-navy-950 border border-navy-750 text-slate-100 font-bold focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1">Current Longitude (°E)</label>
            <input
              type="number"
              step="0.1"
              value={lon}
              onChange={(e) => setLon(e.target.value)}
              className="w-full py-2 px-3 rounded-xl bg-navy-950 border border-navy-750 text-slate-100 font-bold focus:border-cyan-500"
            />
          </div>

          {/* Movement Speed */}
          <div>
            <label className="block text-slate-400 mb-1">Translation Speed (km/h)</label>
            <input
              type="number"
              step="0.5"
              value={speed}
              onChange={(e) => setSpeed(e.target.value)}
              className="w-full py-2 px-3 rounded-xl bg-navy-950 border border-navy-750 text-slate-100 font-bold focus:border-cyan-500"
            />
          </div>

          {/* Wind Speed */}
          <div>
            <label className="block text-slate-400 mb-1">Sustained Wind (km/h)</label>
            <input
              type="number"
              step="5"
              value={wind}
              onChange={(e) => setWind(e.target.value)}
              className="w-full py-2 px-3 rounded-xl bg-navy-950 border border-navy-750 text-slate-100 font-bold focus:border-cyan-500"
            />
          </div>

          {/* Pressure */}
          <div>
            <label className="block text-slate-400 mb-1">Central Pressure (hPa)</label>
            <input
              type="number"
              step="1"
              value={pressure}
              onChange={(e) => setPressure(e.target.value)}
              className="w-full py-2 px-3 rounded-xl bg-navy-950 border border-navy-750 text-slate-100 font-bold focus:border-cyan-500"
            />
          </div>

          {/* Bearing Angle Slider */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-slate-400">Movement Azimuth</label>
              <span className="text-cyan-300 font-bold">{bearing}°</span>
            </div>
            <input
              type="range"
              min="0"
              max="359"
              value={bearing}
              onChange={(e) => setBearing(e.target.value)}
              className="w-full accent-cyan-400 cursor-pointer"
            />
          </div>
        </div>

        {/* Action Button */}
        <div className="mt-6 flex items-center justify-between gap-4 pt-4 border-t border-navy-800">
          <p className="text-[11px] text-slate-400 font-mono hidden sm:block">
            * Forward numerical integration predicts trajectory for +6, +12, +24, +36, and +48 hours.
          </p>

          <button
            onClick={handlePredict}
            disabled={loading}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-navy-950 font-bold text-xs uppercase tracking-wider shadow-glow-cyan flex items-center justify-center gap-2 transition-all ml-auto"
          >
            <Play className="w-4 h-4 fill-navy-950" />
            <span>{loading ? "Computing Trajectory..." : "Run 48-Hour Forecast"}</span>
          </button>
        </div>
      </div>

      {/* Map Display */}
      <CycloneMap cyclone={activeMapCyclone} />

      {/* Output Schedule & Curves */}
      {predictionData && (
        <div className="space-y-6">
          <ForecastTable forecastPoints={predictionData.forecast} />
          <ForecastChart forecastPoints={predictionData.forecast} />
        </div>
      )}
    </div>
  );
}
