import React, { useState, useEffect } from 'react';
import { Database, FolderGit2, FileText, CheckCircle2, RefreshCw } from 'lucide-react';
import DatasetUploader from '../components/DatasetUploader';
import api from '../services/api';

export default function Datasets() {
  const [datasetsList, setDatasetsList] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchDatasets = async () => {
    setLoading(true);
    try {
      const data = await api.getDatasets();
      setDatasetsList(data);
    } catch (err) {
      console.error("Failed to load datasets:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Page Header */}
      <div className="text-center max-w-2xl mx-auto">
        <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          Dataset Manager & Data Ingestion Hub
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 font-sans mt-1">
          Seamlessly ingest satellite imagery, NetCDF files, and cyclone track records without modifying application source code.
        </p>
      </div>

      {/* Dataset Uploader Component */}
      <DatasetUploader onAnalysisComplete={() => fetchDatasets()} />

      {/* Existing / Uploaded Datasets Table */}
      <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-6 shadow-2xl backdrop-blur-md">
        <div className="flex items-center justify-between border-b border-navy-800 pb-3 mb-4">
          <div className="flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-cyan-400" />
            <h3 className="text-base font-bold text-white tracking-tight">
              Ingested Observation Datasets ({datasetsList.length})
            </h3>
          </div>

          <button
            onClick={fetchDatasets}
            disabled={loading}
            className="p-1.5 text-slate-400 hover:text-cyan-300 hover:bg-navy-800 rounded-lg transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {datasetsList.length === 0 ? (
          <div className="p-8 text-center text-slate-400 font-mono text-xs">
            No custom datasets uploaded yet. Ingest your first file using the uploader above.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-navy-800 text-slate-400 uppercase text-[10px]">
                  <th className="py-2.5 px-3">Dataset Name</th>
                  <th className="py-2.5 px-3">Format</th>
                  <th className="py-2.5 px-3">Purpose</th>
                  <th className="py-2.5 px-3">Records / Size</th>
                  <th className="py-2.5 px-3">Date Ingested</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-800/60">
                {datasetsList.map((ds) => (
                  <tr key={ds.id} className="hover:bg-navy-850/50">
                    <td className="py-3 px-3 font-semibold text-slate-200 flex items-center gap-2">
                      <FileText className="w-3.5 h-3.5 text-cyan-400" />
                      {ds.name}
                    </td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded bg-navy-950 text-cyan-300 border border-navy-800 text-[10px]">
                        {ds.file_type}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-300">{ds.purpose}</td>
                    <td className="py-3 px-3 text-slate-400">
                      {ds.records_count} rows • {ds.file_size_kb} KB
                    </td>
                    <td className="py-3 px-3 text-slate-400">{ds.date_uploaded.substring(0, 16)}</td>
                    <td className="py-3 px-3">
                      <span className="text-emerald-400 flex items-center gap-1 font-semibold text-[11px]">
                        <CheckCircle2 className="w-3 h-3" /> Ready
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Directory Placement Guidance Card */}
      <div className="rounded-2xl bg-navy-950/70 border border-navy-800 p-5 text-xs text-slate-400 space-y-2 font-mono">
        <h4 className="text-slate-200 font-bold flex items-center gap-2">
          <Database className="w-4 h-4 text-cyan-400" />
          Where to place persistent raw files locally:
        </h4>
        <ul className="list-disc list-inside space-y-1 text-[11px]">
          <li><code className="text-cyan-300">data/satellite/</code> — High-resolution INSAT-3D/GOES GeoTIFF, PNG, NetCDF files</li>
          <li><code className="text-cyan-300">data/tracks/</code> — Historical IBTrACS or IMD cyclone best track CSV files</li>
          <li><code className="text-cyan-300">data/demo/</code> — Calibrated reference scenario files (Demo Cyclone 01)</li>
        </ul>
      </div>
    </div>
  );
}
