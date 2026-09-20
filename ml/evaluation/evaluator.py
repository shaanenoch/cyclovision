"""Read metrics emitted by real training/evaluation runs.

This module intentionally does not manufacture predictions or learning curves.
If a model has not been trained, its metrics are reported as unavailable.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from backend.config import DEMO_DATA_DIR, DISCLAIMER_TEXT, MODELS_DIR


class ModelEvaluator:
    def __init__(self, metrics_file: Optional[Path] = None):
        self.metrics_file = metrics_file or (DEMO_DATA_DIR / "demo_metrics.json")
        self.track_metrics_file = DEMO_DATA_DIR / "track_metrics.json"
        self.classifier_file = MODELS_DIR / "classification" / "cyclone_classifier_v2.pt"

    def _classifier_metrics(self) -> Dict[str, Any]:
        if not self.classifier_file.exists():
            return {"trained": False, "status": "Awaiting labelled satellite train/validation dataset"}
        try:
            import torch
            checkpoint = torch.load(self.classifier_file, map_location="cpu", weights_only=False)
            return {"trained": True, **checkpoint.get("metadata", {})}
        except Exception as exc:
            return {"trained": False, "status": f"Checkpoint could not be read: {exc}"}

    def run_evaluation(self) -> Dict[str, Any]:
        track = {}
        if self.track_metrics_file.exists():
            track = json.loads(self.track_metrics_file.read_text(encoding="utf-8"))
        classifier = self._classifier_metrics()
        horizon_metrics = track.get("evaluation", {}).get("horizons", {})
        track_summary = {
            "mean_geographic_error_km": track.get("evaluation", {}).get("mean_geographic_error_km"),
            "test_samples": track.get("evaluation", {}).get("test_samples", 0),
            "test_storms": track.get("test_storms", 0),
            "data_source": track.get("data_source"),
            "split_method": track.get("split_method"),
            "horizons": horizon_metrics,
        }
        for hour in [6, 12, 24, 36, 48]:
            track_summary[f"error_{hour}h_km"] = horizon_metrics.get(str(hour), {}).get("mean_error_km")

        metrics = {
            "model_trained": bool(track) or classifier.get("trained", False),
            "model_name": track.get("model_name", "No trained track model"),
            "model_version": track.get("model_version", "untrained"),
            "training_date": track.get("trained_at", "Not available")[:10],
            "dataset_size": track.get("evaluation", {}).get("test_samples", 0),
            "data_source": track.get("data_source"),
            "classification_model_trained": classifier.get("trained", False),
            "classification_status": classifier.get("status", "Trained checkpoint loaded"),
            "training_accuracy": classifier.get("training_accuracy"),
            "validation_accuracy": classifier.get("validation_accuracy"),
            "precision": classifier.get("precision"),
            "recall": classifier.get("recall"),
            "f1_score": classifier.get("f1_score"),
            "confusion_matrix": classifier.get("confusion_matrix", {"labels": [], "matrix": []}),
            "training_loss_history": classifier.get("training_loss_history", []),
            "accuracy_history": classifier.get("accuracy_history", []),
            "track_prediction_metrics": track_summary,
            "disclaimer": DISCLAIMER_TEXT,
        }
        self.metrics_file.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        return metrics

    def load_metrics(self) -> Dict[str, Any]:
        # Rebuild from source artifacts so stale demonstration numbers are never served.
        return self.run_evaluation()
