import React, { useState } from 'react';
import { Satellite, Upload, Sparkles, AlertCircle, CheckCircle2, Eye, Wind, Gauge, Layers } from 'lucide-react';
import api from '../services/api';
import SatelliteViewer from '../components/SatelliteViewer';
import HeatmapViewer from '../components/HeatmapViewer';

export default function Detection() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const loadingSteps = [
    "Processing satellite image...",
    "Detecting cyclone patterns...",
    "Classifying cyclone...",
    "Estimating cyclone center...",
    "Generating forecast track...",
    "Creating AI heatmap..."
  ];

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      setSelectedFile(f);
      setPreviewUrl(URL.createObjectURL(f));
      setError(null);
      setResult(null);
    }
  };

  const handleAnalyze = async (useDemo = false) => {
    setLoading(true);
    setError(null);

    // Simulated step indicator for smooth SIH judging presentation
    let stepIdx = 0;
    const interval = setInterval(() => {
      if (stepIdx < loadingSteps.length) {
        setLoadingStep(loadingSteps[stepIdx]);
        stepIdx++;
      }
    }, 450);

    const formData = new FormData();
    if (!useDemo && selectedFile) {
      formData.append('file', selectedFile);
    } else {
      formData.append('is_demo', 'true');
    }

    try {
      const data = await api.analyzeCyclone(formData);
      clearInterval(interval);
      setResult(data);
    } catch (err) {
      clearInterval(interval);
      setError(err.response?.data?.detail || "Unable to read this satellite file. Please upload JPG, PNG, TIFF or NetCDF data.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Page Header */}
      <div className="text-center max-w-2xl mx-auto">
        <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          AI Cyclone Detection & Eyewall Classification
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 font-sans mt-1">
          Upload multi-spectral satellite imagery to detect tropical cyclone presence, localize the center of circulation, and generate neural explainability heatmaps.
        </p>
      </div>

      {/* Upload / Test Section */}
      <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-6 shadow-2xl backdrop-blur-md">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
          
          {/* File Picker */}
          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-slate-300 font-bold mb-2">
              Select Satellite Observation
            </label>
            <div className="relative border-2 border-dashed border-navy-700 hover:border-cyan-500/50 rounded-xl p-6 text-center bg-navy-950/60 cursor-pointer">
              <input
                type="file"
                accept=".png,.jpg,.jpeg,.tif,.tiff,.nc"
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
              <Upload className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
              <p className="text-xs text-slate-300 font-semibold">
                {selectedFile ? selectedFile.name : "Click or drag satellite image (.png, .jpg, .tif, .nc)"}
              </p>
              <p className="text-[11px] text-slate-400 font-mono mt-1">
                Supports INSAT-3D, GOES, Himawari and NetCDF channels
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={() => handleAnalyze(false)}
              disabled={loading || !selectedFile}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 text-navy-950 font-bold text-xs uppercase tracking-wider shadow-glow-cyan flex items-center justify-center gap-2 transition-all"
            >
              <Sparkles className="w-4 h-4" />
              <span>{loading ? loadingStep : "Analyze Uploaded Satellite Image"}</span>
            </button>

            <button
              onClick={() => handleAnalyze(true)}
              disabled={loading}
              className="w-full py-2.5 rounded-xl bg-navy-850 hover:bg-navy-800 border border-navy-700 text-slate-200 font-mono text-xs flex items-center justify-center gap-2 transition-colors"
            >
              <span>Load Calibrated Sample (Demo Cyclone 01)</span>
            </button>

            <p className="text-[11px] text-slate-400 text-center font-mono">
              Note: Ordinary JPG/PNG images estimate pixel vortex center. Georeferenced coordinates require NetCDF/GeoTIFF metadata.
            </p>
          </div>

        </div>

        {error && (
          <div className="mt-4 p-3 rounded-xl bg-red-950/50 border border-red-800/60 text-xs text-red-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Results View */}
      {result && (
        <div className="space-y-6">
          {/* Quick Metrics Header */}
          <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-6 shadow-2xl backdrop-blur-md">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-navy-800 pb-4 mb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-400">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white tracking-tight">
                    Cyclone Pattern Detected: {result.cyclone_detected ? "YES" : "NO"}
                  </h3>
                  <p className="text-xs text-slate-400 font-mono">
                    Model: {result.model_version} • Execution Time: {result.execution_time_ms} ms
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className="text-xs font-mono px-3 py-1 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800 font-semibold">
                  AI Confidence: {Math.round(result.detection_confidence * 100)}%
                </span>
                <span className="text-xs font-mono px-3 py-1 rounded-full bg-orange-950 text-orange-400 border border-orange-800 font-semibold">
                  {result.classification}
                </span>
              </div>
            </div>

            {/* Parameter Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
              <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
                <span className="text-slate-400 block text-[10px]">Estimated Eye Location</span>
                <span className="text-slate-200 font-bold">
                  {result.current_position.lat?.toFixed(1)}°N, {result.current_position.lon?.toFixed(1)}°E
                </span>
              </div>
              <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
                <span className="text-slate-400 block text-[10px]">Estimated Wind Speed</span>
                <span className="text-slate-200 font-bold">{result.wind_speed} km/h</span>
              </div>
              <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
                <span className="text-slate-400 block text-[10px]">Central Pressure</span>
                <span className="text-slate-200 font-bold">{result.pressure} hPa</span>
              </div>
              <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
                <span className="text-slate-400 block text-[10px]">Dataset Source</span>
                <span className="text-cyan-300 font-bold">{result.dataset_label}</span>
              </div>
            </div>
          </div>

          {/* Side by side Satellite & Heatmap */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <SatelliteViewer
              imageUrl={result.original_image_url}
              timestamp="Analyzed Satellite Frame"
              channel="IR Convective Banding"
            />

            <HeatmapViewer
              heatmapUrl={result.heatmap_url}
              method="Grad-CAM Deep Attention"
            />
          </div>
        </div>
      )}
    </div>
  );
}
