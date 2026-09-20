import React from 'react';
import ModelMetrics from '../components/ModelMetrics';

export default function Analytics() {
  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Page Header */}
      <div className="text-center max-w-2xl mx-auto">
        <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          Model Analytics & Validation Metrics
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 font-sans mt-1">
          Detailed meteorological performance benchmarks calculated across test data splits. All scores, confusion matrices, and track errors reflect real evaluation runs.
        </p>
      </div>

      {/* Model Metrics Component */}
      <ModelMetrics />
    </div>
  );
}
