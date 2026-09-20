import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, BarChart3, CheckCircle2, RefreshCw, Target } from 'lucide-react';
import api from '../services/api';

const value = (number, suffix = '') => number == null ? 'N/A' : `${Number(number).toFixed(1)}${suffix}`;

export default function ModelMetrics() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchMetrics = async () => {
    setLoading(true);
    try { setMetrics(await api.getModelMetrics()); }
    finally { setLoading(false); }
  };
  useEffect(() => { fetchMetrics(); }, []);

  const refresh = async () => {
    setRefreshing(true);
    try {
      const response = await api.trainModel();
      setMetrics(response.metrics);
    } finally { setRefreshing(false); }
  };

  if (loading) return (
    <div className="p-12 text-center text-slate-400 font-mono text-xs">
      <Activity className="w-6 h-6 text-cyan-400 animate-spin mx-auto mb-2" />
      Reading trained model artifacts...
    </div>
  );
  if (!metrics?.model_trained) return (
    <div className="p-8 rounded-2xl bg-navy-900 border border-navy-750 text-center">
      <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto mb-2" />
      <h4 className="font-bold text-white">No trained artifacts found</h4>
    </div>
  );

  const track = metrics.track_prediction_metrics || {};
  const horizons = track.horizons || {};
  const hours = [6, 12, 24, 36, 48];
  const matrix = metrics.confusion_matrix || { labels: [], matrix: [] };

  return <div className="space-y-6">
    <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-6 shadow-2xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-navy-800 pb-4 mb-5">
        <div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-cyan-400" />
            <h3 className="text-lg font-bold text-white">Verified Model Evaluation</h3>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Held-out cyclone evaluation • no same-storm train/test leakage
          </p>
        </div>
        <button onClick={refresh} disabled={refreshing}
          className="px-3 py-2 rounded-xl bg-navy-850 border border-navy-750 text-cyan-300 text-xs font-mono flex items-center gap-2">
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh artifact metrics
        </button>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
        <Metric label="Model" display={metrics.model_name} />
        <Metric label="Test observations" display={metrics.dataset_size} />
        <Metric label="Unseen test cyclones" display={track.test_storms} />
        <Metric label="Data source" display={track.data_source || 'N/A'} />
      </div>
    </div>

    <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-6 shadow-2xl">
      <div className="flex items-center gap-2 border-b border-navy-800 pb-3 mb-4">
        <Target className="w-4 h-4 text-cyan-400" />
        <h4 className="text-sm font-bold text-white">Track and intensity validation</h4>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {hours.map(hour => {
          const item = horizons[String(hour)] || {};
          return <div key={hour} className="p-4 rounded-xl bg-navy-950 border border-navy-800 font-mono">
            <span className="text-[10px] uppercase text-slate-400">+{hour}h track error</span>
            <div className="text-lg font-bold text-cyan-300">{value(item.mean_error_km, ' km')}</div>
            <div className="text-[10px] text-slate-400 mt-1">67% radius: {value(item.p67_error_km, ' km')}</div>
            <div className="text-[10px] text-slate-400">Wind MAE: {value(item.wind_mae_kmph, ' km/h')}</div>
          </div>;
        })}
      </div>
      <p className="text-[11px] font-mono text-slate-400 mt-4">
        Split: {track.split_method || 'N/A'} • Overall mean track error: {value(track.mean_geographic_error_km, ' km')}
      </p>
    </div>

    {!metrics.classification_model_trained ? (
      <div className="rounded-2xl bg-amber-950/20 border border-amber-700/50 p-6 flex gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0" />
        <div>
          <h4 className="text-sm font-bold text-amber-300">Satellite classifier awaiting real labelled imagery</h4>
          <p className="text-xs text-slate-300 mt-1">{metrics.classification_status}</p>
          <p className="text-xs text-slate-400 mt-1">Until trained, image classification and heatmaps are clearly marked as heuristic fallbacks.</p>
        </div>
      </div>
    ) : (
      <div className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Metric label="Accuracy" display={value(metrics.validation_accuracy * 100, '%')} />
          <Metric label="Precision" display={value(metrics.precision * 100, '%')} />
          <Metric label="Recall" display={value(metrics.recall * 100, '%')} />
          <Metric label="F1 score" display={value(metrics.f1_score * 100, '%')} />
        </div>
        <div className="rounded-2xl bg-navy-900/80 border border-navy-750 p-6 overflow-x-auto">
          <div className="flex items-center gap-2 mb-4"><CheckCircle2 className="w-4 h-4 text-emerald-400" /><h4 className="text-sm font-bold text-white">Classifier confusion matrix</h4></div>
          <table className="w-full text-center text-xs font-mono">
            <thead><tr><th>Actual / predicted</th>{matrix.labels.map(label => <th key={label} className="p-2 text-cyan-300">{label}</th>)}</tr></thead>
            <tbody>{matrix.matrix.map((row, i) => <tr key={matrix.labels[i]}><th className="p-2 text-left">{matrix.labels[i]}</th>{row.map((cell, j) => <td key={j} className="p-2 border border-navy-800">{cell}</td>)}</tr>)}</tbody>
          </table>
        </div>
      </div>
    )}
  </div>;
}

function Metric({ label, display }) {
  return <div className="p-3 rounded-xl bg-navy-950 border border-navy-800 font-mono min-w-0">
    <span className="text-slate-400 block text-[10px] uppercase">{label}</span>
    <span className="text-slate-200 font-bold text-xs break-words">{display ?? 'N/A'}</span>
  </div>;
}
