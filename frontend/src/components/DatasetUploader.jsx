import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Play, Database, FileSpreadsheet, Image as ImageIcon } from 'lucide-react';
import api from '../services/api';

export default function DatasetUploader({ onAnalysisComplete }) {
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState(null);
  const [purpose, setPurpose] = useState('Live/New Cyclone Observation');
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadedDataset, setUploadedDataset] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const supportedFormats = [".csv", ".json", ".nc", ".png", ".jpg", ".jpeg", ".tif"];

  const purposes = [
    "Satellite Images",
    "Historical Cyclone Tracks",
    "Live/New Cyclone Observation",
    "Training Dataset",
    "Validation Dataset"
  ];

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setUploadedDataset(null);
      setAnalysisResult(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError(null);
      setUploadedDataset(null);
      setAnalysisResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('purpose', purpose);

    try {
      const data = await api.uploadDataset(formData);
      setUploadedDataset(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to process dataset file.");
    } finally {
      setUploading(false);
    }
  };

  const handleRunAnalysis = async () => {
    if (!uploadedDataset?.id) return;
    setAnalyzing(true);
    setError(null);

    try {
      const res = await api.analyzeDataset(uploadedDataset.id);
      setAnalysisResult(res);
      if (onAnalysisComplete) {
        onAnalysisComplete(res);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis execution failed.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Box */}
      <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-6 shadow-2xl backdrop-blur-md">
        <div className="flex items-center justify-between border-b border-navy-800 pb-3 mb-5">
          <div className="flex items-center gap-2.5">
            <Database className="w-5 h-5 text-cyan-400" />
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">
                Dataset Ingestion Manager
              </h3>
              <p className="text-xs text-slate-400">
                Upload raw satellite feeds, NetCDF variables, or IBTrACS track observations without altering code.
              </p>
            </div>
          </div>

          <span className="text-[11px] font-mono text-slate-400">
            Supported: .csv, .json, .nc, .png, .jpg, .tif
          </span>
        </div>

        {/* Drag and Drop Zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center ${
            dragOver 
              ? 'border-cyan-400 bg-cyan-950/30' 
              : 'border-navy-700 bg-navy-950/60 hover:border-cyan-500/50 hover:bg-navy-950/90'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".csv,.json,.nc,.png,.jpg,.jpeg,.tif,.tiff"
            className="hidden"
          />

          <div className="p-3.5 rounded-2xl bg-navy-850 border border-navy-750 text-cyan-400 mb-3 shadow-glow-cyan">
            <UploadCloud className="w-7 h-7" />
          </div>

          <h4 className="text-sm font-semibold text-slate-200 mb-1">
            {file ? file.name : "Drag & drop files here, or click to browse"}
          </h4>
          <p className="text-xs text-slate-400 font-mono">
            {file ? `${(file.size / 1024).toFixed(1)} KB • Ready for Validation` : "Multi-source satellite images or historical track records"}
          </p>
        </div>

        {/* Purpose Selector & Upload Button */}
        <div className="mt-5 grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
          <div className="sm:col-span-2">
            <label className="block text-xs font-semibold uppercase font-mono tracking-wider text-slate-400 mb-1.5">
              Select Dataset Purpose
            </label>
            <select
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              className="w-full py-2.5 px-3 rounded-xl bg-navy-950 border border-navy-750 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
            >
              {purposes.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 text-navy-950 font-bold text-xs tracking-wider uppercase shadow-glow-cyan flex items-center justify-center gap-2 transition-all h-[42px]"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>{uploading ? "Ingesting..." : "Validate & Ingest"}</span>
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 rounded-xl bg-red-950/40 border border-red-800/60 text-xs text-red-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Dataset Metadata Inspection Box */}
      {uploadedDataset && (
        <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-6 shadow-2xl backdrop-blur-md">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-navy-800 pb-4 mb-4">
            <div>
              <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider font-semibold">
                Validated Metadata Inspector
              </span>
              <h4 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                <span>{uploadedDataset.name}</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono">
                  {uploadedDataset.file_type}
                </span>
              </h4>
            </div>

            <button
              onClick={handleRunAnalysis}
              disabled={analyzing}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-navy-950 font-bold text-xs tracking-wider uppercase shadow-lg flex items-center justify-center gap-2 transition-all"
            >
              <Play className="w-4 h-4 fill-navy-950" />
              <span>{analyzing ? "Running Neural Pipeline..." : "Run Analysis"}</span>
            </button>
          </div>

          {/* Metadata Cards Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs mb-5">
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
              <span className="text-slate-400 block text-[10px]">File Size</span>
              <span className="text-slate-200 font-bold">{uploadedDataset.file_size_kb} KB</span>
            </div>
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
              <span className="text-slate-400 block text-[10px]">Records / Shape</span>
              <span className="text-slate-200 font-bold">{uploadedDataset.records_count}</span>
            </div>
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
              <span className="text-slate-400 block text-[10px]">Purpose</span>
              <span className="text-cyan-300 font-semibold truncate block">{uploadedDataset.purpose}</span>
            </div>
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
              <span className="text-slate-400 block text-[10px]">Status</span>
              <span className="text-emerald-400 font-semibold">{uploadedDataset.status}</span>
            </div>
          </div>

          {/* Columns Preview */}
          {uploadedDataset.columns && uploadedDataset.columns.length > 0 && (
            <div className="mb-4">
              <span className="text-[11px] font-mono text-slate-400 block mb-2">Detected Channels / Fields:</span>
              <div className="flex flex-wrap gap-1.5 font-mono text-xs">
                {uploadedDataset.columns.map((col, i) => (
                  <span key={i} className="px-2 py-1 rounded bg-navy-850 border border-navy-800 text-slate-300">
                    {col}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Records Table Preview */}
          {uploadedDataset.preview && uploadedDataset.preview.length > 0 && (
            <div>
              <span className="text-[11px] font-mono text-slate-400 block mb-2">Sample Records Preview:</span>
              <div className="overflow-x-auto rounded-xl border border-navy-800 bg-navy-950 p-2">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-navy-800 text-slate-400 text-[10px]">
                      {Object.keys(uploadedDataset.preview[0]).map((k) => (
                        <th key={k} className="p-2">{k}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-navy-850">
                    {uploadedDataset.preview.map((row, idx) => (
                      <tr key={idx} className="hover:bg-navy-900/50">
                        {Object.values(row).map((v, i) => (
                          <td key={i} className="p-2 text-slate-300">
                            {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Analysis Feedback Alert */}
          {analysisResult && (
            <div className="mt-5 p-4 rounded-xl bg-cyan-950/40 border border-cyan-700/60 space-y-2">
              <div className="flex items-center gap-2 text-cyan-300 font-bold text-xs font-mono">
                <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                <span>Automated Pipeline Output: {analysisResult.analysis_type}</span>
              </div>
              <p className="text-xs text-slate-300">
                Processed records successfully. Results assimilated into active trajectory models.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
