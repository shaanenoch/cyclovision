import React from 'react';
import { Info, ShieldAlert, Satellite, Layers, Cpu, Compass, BookOpen, AlertTriangle } from 'lucide-react';

export default function About() {
  return (
    <div className="space-y-8 max-w-4xl mx-auto pb-16 font-sans">
      
      {/* Title */}
      <div className="text-center">
        <span className="text-xs font-mono px-3 py-1 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800 uppercase tracking-wider font-semibold">
          Smart India Hackathon (SIH) Project
        </span>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mt-3">
          CycloneAI — Tropical Cyclone Intelligence System
        </h2>
        <p className="text-sm text-slate-400 mt-2 leading-relaxed">
          AI-Based Tropical Cyclone Identification, Classification and Prediction System Using Multi-Source Satellite Observations.
        </p>
      </div>

      {/* Mandatory Disclaimer Box */}
      <div className="p-4 rounded-2xl bg-amber-950/40 border border-amber-700/60 shadow-lg text-xs text-amber-200/90 flex items-start gap-3 leading-relaxed">
        <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <strong className="text-amber-300 block mb-0.5 text-sm">Academic Research Disclaimer</strong>
          Research prototype for cyclone analysis. Forecast outputs must not replace official meteorological warnings from the India Meteorological Department (IMD) or national disaster management authorities.
        </div>
      </div>

      {/* Problem Statement Card */}
      <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-6 shadow-xl space-y-3">
        <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-cyan-400" />
          <span>Problem Statement</span>
        </h3>
        <blockquote className="p-3.5 rounded-xl bg-navy-950/80 border-l-4 border-cyan-400 text-xs font-mono text-slate-300 italic">
          "To develop an Artificial Intelligence (AI) / Machine Learning (ML) based system for identification, classification, and prediction of different tropical cyclone patterns using multi-source satellite data."
        </blockquote>
        <p className="text-xs text-slate-300 leading-relaxed">
          Tropical cyclones in the North Indian Ocean (Bay of Bengal and Arabian Sea) present catastrophic hazards to coastal lives, infrastructure, and maritime navigation. CycloneAI provides an end-to-end intelligent pipeline integrating multi-sensor satellite imagery (INSAT-3D, GOES, Himawari) with deep neural networks for automated detection, Dvorak-aligned intensity classification, eyewall localization, explainability heatmaps, and forward track regression.
        </p>
      </div>

      {/* System Architecture Grid */}
      <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-6 shadow-xl space-y-4">
        <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span>End-to-End Operational Pipeline</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
          <div className="p-3.5 rounded-xl bg-navy-950 border border-navy-800">
            <span className="text-cyan-400 font-bold block mb-1">1. Ingestion Layer</span>
            <p className="text-slate-400 text-[11px]">
              Multi-source adapters for NetCDF (.nc), GeoTIFF, PNG/JPG, and IBTrACS track CSVs.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-navy-950 border border-navy-800">
            <span className="text-cyan-400 font-bold block mb-1">2. Vision & XAI Engine</span>
            <p className="text-slate-400 text-[11px]">
              Lightweight MobileNetV3 backbone for vortex detection, IMD classification, and Grad-CAM saliency.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-navy-950 border border-navy-800">
            <span className="text-cyan-400 font-bold block mb-1">3. Trajectory Forecaster</span>
            <p className="text-slate-400 text-[11px]">
              Multi-output regression predicting +6h, +12h, +24h, +36h, and +48h coordinates and wind speed.
            </p>
          </div>
        </div>
      </div>

      {/* IMD Intensity Scale Reference */}
      <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-6 shadow-xl space-y-3">
        <h3 className="text-base font-bold text-white tracking-tight">
          Supported IMD Cyclone Intensity Scale
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
          <div className="p-2.5 rounded-lg bg-navy-950 border border-sky-800/40 text-sky-300">
            <strong>Low Pressure Area</strong>
            <div className="text-[10px] text-slate-400">&lt; 31 km/h</div>
          </div>
          <div className="p-2.5 rounded-lg bg-navy-950 border border-emerald-800/40 text-emerald-300">
            <strong>Depression</strong>
            <div className="text-[10px] text-slate-400">31 - 49 km/h</div>
          </div>
          <div className="p-2.5 rounded-lg bg-navy-950 border border-yellow-800/40 text-yellow-300">
            <strong>Deep Depression</strong>
            <div className="text-[10px] text-slate-400">50 - 61 km/h</div>
          </div>
          <div className="p-2.5 rounded-lg bg-navy-950 border border-orange-800/40 text-orange-300">
            <strong>Cyclonic Storm</strong>
            <div className="text-[10px] text-slate-400">62 - 88 km/h</div>
          </div>
          <div className="p-2.5 rounded-lg bg-navy-950 border border-orange-700/60 text-orange-400">
            <strong>Severe CS</strong>
            <div className="text-[10px] text-slate-400">89 - 117 km/h</div>
          </div>
          <div className="p-2.5 rounded-lg bg-navy-950 border border-red-800/40 text-red-300">
            <strong>Very Severe CS</strong>
            <div className="text-[10px] text-slate-400">118 - 166 km/h</div>
          </div>
          <div className="p-2.5 rounded-lg bg-navy-950 border border-red-700/60 text-red-400">
            <strong>Extremely Severe CS</strong>
            <div className="text-[10px] text-slate-400">167 - 221 km/h</div>
          </div>
          <div className="p-2.5 rounded-lg bg-navy-950 border border-red-900 text-rose-300">
            <strong>Super Cyclone</strong>
            <div className="text-[10px] text-slate-400">&ge; 222 km/h</div>
          </div>
        </div>
      </div>

    </div>
  );
}
