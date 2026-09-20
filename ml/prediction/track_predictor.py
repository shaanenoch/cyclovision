from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np

from backend.config import MODELS_DIR, get_category_from_wind


class TrackPredictor:
    """Multi-horizon IBTrACS forecaster with an explicit physical fallback."""

    def __init__(self, model_file: Optional[str] = None):
        default = MODELS_DIR / "prediction" / "track_predictor_v2.joblib"
        self.model_file = Path(model_file) if model_file else default
        self.model = None
        self.horizons = [6, 12, 24, 36, 48]
        self.metadata: Dict[str, Any] = {}
        self._load_model()

    @property
    def is_model_loaded(self) -> bool:
        return self.model is not None

    @property
    def model_name(self) -> str:
        if self.is_model_loaded:
            return self.metadata.get("model_name", "IBTrACS trained forecaster")
        return "Physical motion fallback (untrained)"

    def _load_model(self) -> None:
        if not self.model_file.exists():
            return
        try:
            artifact = joblib.load(self.model_file)
            self.model = artifact["model"]
            self.horizons = list(artifact["horizons"])
            self.metadata = dict(artifact.get("metadata", {}))
        except Exception as exc:
            self.metadata = {"load_error": str(exc)}
            self.model = None

    @staticmethod
    def _features(lat, lon, wind, pressure, bearing, speed, month=None):
        bearing_rad = math.radians(bearing % 360.0)
        month = month or datetime.utcnow().month
        month_angle = 2.0 * math.pi * (month - 1) / 12.0
        return np.asarray([[
            lat, lon, wind, pressure, math.sin(bearing_rad), math.cos(bearing_rad),
            speed, math.sin(month_angle), math.cos(month_angle),
        ]], dtype=float)

    def _ml_forecast(self, lat, lon, wind, pressure, bearing, speed):
        prediction = self.model.predict(
            self._features(lat, lon, wind, pressure, bearing, speed)
        )[0]
        evaluation = self.metadata.get("evaluation", {}).get("horizons", {})
        results = []
        for index, hour in enumerate(self.horizons):
            offset = index * 4
            next_lat = float(np.clip(lat + prediction[offset], -90.0, 90.0))
            next_lon = float(((lon + prediction[offset + 1] + 180.0) % 360.0) - 180.0)
            next_wind = float(np.clip(prediction[offset + 2], 0.0, 350.0))
            next_pressure = float(np.clip(prediction[offset + 3], 850.0, 1035.0))
            category = get_category_from_wind(next_wind)
            error = evaluation.get(str(hour), {})
            results.append({
                "forecast_hour": hour,
                "latitude": round(next_lat, 2),
                "longitude": round(next_lon, 2),
                "wind_speed_kmph": round(next_wind, 1),
                "pressure_hpa": round(next_pressure, 1),
                "classification": category["name"],
                "category_color": category["color"],
                "confidence_label": "IBTrACS model estimate",
                "uncertainty_km": error.get("p67_error_km"),
                "model_mode": "trained",
            })
        return results

    def _physical_fallback(self, lat, lon, wind, pressure, bearing, speed):
        results, current_lat, current_lon, last_hour = [], lat, lon, 0
        for hour in self.horizons:
            delta_hours, last_hour = hour - last_hour, hour
            bearing = (bearing + (-1.5 if current_lat < 18.0 else 3.0)) % 360.0
            distance = np.clip(speed, 8.0, 40.0) * delta_hours
            radius = 6371.0
            phi1, lambda1, theta = map(math.radians, [current_lat, current_lon, bearing])
            angular = distance / radius
            phi2 = math.asin(
                math.sin(phi1) * math.cos(angular)
                + math.cos(phi1) * math.sin(angular) * math.cos(theta)
            )
            lambda2 = lambda1 + math.atan2(
                math.sin(theta) * math.sin(angular) * math.cos(phi1),
                math.cos(angular) - math.sin(phi1) * math.sin(phi2),
            )
            current_lat, current_lon = math.degrees(phi2), math.degrees(lambda2)
            wind += (4.0 if hour <= 24 else -3.5) * delta_hours / 6.0
            pressure += (-2.5 if hour <= 24 else 2.0) * delta_hours / 6.0
            category = get_category_from_wind(wind)
            results.append({
                "forecast_hour": hour,
                "latitude": round(current_lat, 2), "longitude": round(current_lon, 2),
                "wind_speed_kmph": round(float(np.clip(wind, 0, 350)), 1),
                "pressure_hpa": round(float(np.clip(pressure, 850, 1035)), 1),
                "classification": category["name"], "category_color": category["color"],
                "confidence_label": "physical fallback estimate",
                "uncertainty_km": None, "model_mode": "fallback",
            })
        return results

    def predict_track(
        self, current_lat: float, current_lon: float,
        wind_speed_kmph: float = 95.0, pressure_hpa: float = 985.0,
        movement_bearing_deg: float = 315.0, movement_speed_kmph: float = 16.0,
        track_history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        args = (current_lat, current_lon, wind_speed_kmph, pressure_hpa,
                movement_bearing_deg, movement_speed_kmph)
        return self._ml_forecast(*args) if self.is_model_loaded else self._physical_fallback(*args)
