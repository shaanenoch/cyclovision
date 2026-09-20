import React, { useState, useEffect } from 'react';
import { 
  Radio, 
  Wind, 
  Gauge, 
  ShieldAlert, 
  Activity, 
  Satellite, 
  Eye, 
  Clock, 
  TrendingUp,
  AlertTriangle
} from 'lucide-react';
import SearchBar from '../components/SearchBar';
import StatusCard from '../components/StatusCard';
import CycloneMap from '../components/CycloneMap';
import CycloneInfoPanel from '../components/CycloneInfoPanel';
import SatelliteViewer from '../components/SatelliteViewer';
import HeatmapViewer from '../components/HeatmapViewer';
import ForecastTable from '../components/ForecastTable';
import ForecastChart from '../components/ForecastChart';
import api from '../services/api';

export default function Dashboard({ onNavigateToTab }) {
  const [cyclone, setCyclone] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedMapPoint, setSelectedMapPoint] = useState(null);
  const [liveAnalysis, setLiveAnalysis] = useState(null);

  const fetchCycloneData = async () => {
    setLoading(true);
    try {
      const data = await api.getCycloneDetails('demo-cyclone-01');
      setCyclone(data);
    } catch (err) {
      console.error("Failed to load cyclone details:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCycloneData();
  }, []);

  const handleRunPipeline = async () => {
    setAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('is_demo', 'true');
      formData.append('latitude', cyclone?.current_lat || 15.2);
      formData.append('longitude', cyclone?.current_lon || 84.7);
      
      const result = await api.analyzeCyclone(formData);
      setLiveAnalysis(result);

      // Refresh cyclone state
      fetchCycloneData();
    } catch (err) {
      console.error("Pipeline analysis failed:", err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSelectLocation = (loc) => {
    if (loc.lat && loc.lon) {
      setSelectedMapPoint({ lat: loc.lat, lon: loc.lon });
    }
  };

  const forecastPoints = cyclone?.track_points?.filter(p => p.point_type === 'forecast') || [];
  const windKmph = cyclone?.wind_speed_kmph || 115;
  const windKts = Math.round(windKmph / 1.852);
  const pressure = cyclone?.pressure_hpa || 978;

  return (
    <div className="space-y-6 pb-12">
      
      {/* Top Heading Section */}
      <div className="text-center max-w-3xl mx-auto pt-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-navy-900 border border-navy-750 text-cyan-300 text-xs font-mono mb-3">
          <Radio className="w-3.5 h-3.5 animate-pulse text-cyan-400" />
          <span>Multi-Source Satellite Observation Pipeline</span>
        </div>
        <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
          Tropical Cyclone Intelligence Dashboard
        </h1>
        <p className="mt-2 text-xs sm:text-sm text-slate-400 font-sans leading-relaxed">
          AI-powered satellite analysis for cyclone identification, classification and track prediction.
        </p>
      </div>

      {/* Global Search Bar */}
      <SearchBar 
        onSelectLocation={handleSelectLocation} 
        activeCyclone={cyclone} 
      />

      {/* 4 Status Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatusCard
          title="Active / Detected Cyclone"
          value={cyclone?.name || "Demo Cyclone 01"}
          subtitle={`${cyclone?.basin || "Bay of Bengal"} • ${cyclone?.movement_direction || "North-West"}`}
          icon={Radio}
          badge="LIVE"
          badgeColor="bg-cyan-500/20 text-cyan-300 border-cyan-500/30"
          tooltip="Tropical cyclone currently tracked in active dataset"
          highlightColor="border-cyan-500/40"
        />

        <StatusCard
          title="Classification"
          value={cyclone?.status || "Severe Cyclonic Storm"}
          subtitle="IMD Intensity Scale"
          icon={ShieldAlert}
          badge="SCS"
          badgeColor="bg-orange-500/20 text-orange-400 border-orange-500/30"
          tooltip="Estimated cyclone intensity category according to IMD / WMO criteria"
          highlightColor="border-orange-500/30"
        />

        <StatusCard
          title="Model Confidence"
          value={liveAnalysis?.detection_confidence ? `${Math.round(liveAnalysis.detection_confidence * 100)}%` : "94%"}
          subtitle="Vorticity & Pattern Match"
          icon={Activity}
          badge="High"
          badgeColor="bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
          tooltip="The AI model estimates a 94% probability for this classification."
          highlightColor="border-emerald-500/30"
        />

        <StatusCard
          title="Maximum Wind Speed"
          value={`${windKmph} km/h`}
          subtitle={`Pressure: ${pressure} hPa • ${windKts} kts`}
          icon={Wind}
          badge="Level 5"
          badgeColor="bg-blue-500/20 text-blue-300 border-blue-500/30"
          tooltip="Maximum sustained surface wind estimated by convective density model"
          highlightColor="border-blue-500/30"
        />
      </div>

      {/* Main Grid: Interactive Map (Left) + Cyclone Information Panel (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        <div className="lg:col-span-8">
          <CycloneMap 
            cyclone={cyclone} 
            selectedPoint={selectedMapPoint}
            onPointClick={(pt) => setSelectedMapPoint({ lat: pt.latitude, lon: pt.longitude })}
          />
        </div>

        <div className="lg:col-span-4">
          <CycloneInfoPanel 
            cyclone={cyclone}
            onTriggerAnalyze={handleRunPipeline}
            loading={analyzing}
          />
        </div>
      </div>

      {/* Side-by-side Satellite Image & AI Attention Heatmap */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <SatelliteViewer
          imageUrl={liveAnalysis?.original_image_url || cyclone?.satellite_image_url}
          timestamp="2026-09-20 00:00 UTC (INSAT-3D TIR-1)"
          channel="Thermal Infrared (10.8 µm)"
        />

        <HeatmapViewer
          heatmapUrl={liveAnalysis?.heatmap_url || cyclone?.heatmap_url}
          method="Grad-CAM Deep Attention"
        />
      </div>

      {/* Forecast Track Table */}
      <ForecastTable 
        forecastPoints={forecastPoints}
        onSelectPoint={(coord) => setSelectedMapPoint(coord)}
      />

      {/* Forecast Evolution Charts */}
      <ForecastChart 
        forecastPoints={forecastPoints} 
      />

      {/* Quick Navigation Footer Banner */}
      <div className="rounded-2xl bg-gradient-to-r from-navy-900 via-navy-850 to-navy-900 border border-navy-750 p-6 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xl">
        <div>
          <h4 className="text-sm font-bold text-white tracking-tight">
            Ready to test with your custom satellite imagery or IBTrACS track datasets?
          </h4>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Ingest .csv, .json, .nc, or satellite photos in the Dataset Manager without restarting the server.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigateToTab('datasets')}
            className="px-4 py-2 rounded-xl bg-navy-800 hover:bg-navy-750 border border-navy-700 text-cyan-300 font-mono text-xs font-semibold transition-colors"
          >
            Open Dataset Manager
          </button>
          <button
            onClick={() => onNavigateToTab('analytics')}
            className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-navy-950 font-bold text-xs transition-colors"
          >
            View Model Analytics
          </button>
        </div>
      </div>

    </div>
  );
}
