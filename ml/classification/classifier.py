from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import cv2
import numpy as np

from backend.config import CYCLONE_CATEGORIES, MODELS_DIR, get_category_from_wind
from preprocessing.image_preprocessing import load_image_to_numpy, resize_and_normalize


def build_mobilenet(num_classes: int):
    """Create the exact architecture used by the training script."""
    import torch.nn as nn
    from torchvision.models import mobilenet_v3_small

    model = mobilenet_v3_small(weights=None)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
    return model


class CycloneClassifier:
    def __init__(self, model_weights_path: Optional[str] = None):
        default = MODELS_DIR / "classification" / "cyclone_classifier_v2.pt"
        self.model_weights_path = Path(model_weights_path) if model_weights_path else default
        self.categories = CYCLONE_CATEGORIES
        self.model = None
        self.class_names = [item["name"] for item in self.categories]
        self.metadata: Dict[str, Any] = {}
        self._load_weights()

    @property
    def is_model_loaded(self) -> bool:
        return self.model is not None

    def _load_weights(self):
        if not self.model_weights_path.exists():
            return
        try:
            import torch
            checkpoint = torch.load(self.model_weights_path, map_location="cpu", weights_only=False)
            self.class_names = checkpoint["class_names"]
            self.model = build_mobilenet(len(self.class_names))
            self.model.load_state_dict(checkpoint["state_dict"])
            self.model.eval()
            self.metadata = checkpoint.get("metadata", {})
        except Exception as exc:
            self.model = None
            self.metadata = {"load_error": str(exc)}

    def _neural_classification(self, image_source):
        import torch
        image = load_image_to_numpy(image_source)
        _, normalized = resize_and_normalize(image, (224, 224))
        tensor = torch.from_numpy(normalized).unsqueeze(0).float()
        with torch.inference_mode():
            probabilities = torch.softmax(self.model(tensor), dim=1)[0].cpu().numpy()
        class_index = int(np.argmax(probabilities))
        class_name = self.class_names[class_index]
        cat_info = next(
            (item for item in self.categories if item["name"] == class_name),
            self.categories[0],
        )
        expected_wind = sum(
            probability * (
                (item["min_wind_kmph"] + min(item["max_wind_kmph"], 260)) / 2.0
            )
            for probability, item in zip(probabilities, self.categories)
        )
        return cat_info, float(probabilities[class_index]), float(expected_wind), probabilities

    def _heuristic_classification(self, image_source, detection_confidence):
        image = load_image_to_numpy(image_source)
        h, w, _ = image.shape
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        center = gray[h // 4: 3 * h // 4, w // 4: 3 * w // 4]
        min_value, max_value, _, _ = cv2.minMaxLoc(center)
        convection = float(np.mean(center > 180))
        wind = (45.0 + convection * 90.0 + (max_value - min_value) * 0.35)
        wind *= 0.8 + 0.3 * detection_confidence
        wind = float(np.clip(wind, 35.0, 240.0))
        return get_category_from_wind(wind), float(np.clip(0.55 + convection * 0.2, 0.55, 0.78)), wind, None

    def classify_image(self, image_source, detection_confidence: float = 0.88) -> Dict[str, Any]:
        if self.is_model_loaded:
            category, confidence, wind, probabilities = self._neural_classification(image_source)
            mode = "trained"
        else:
            category, confidence, wind, probabilities = self._heuristic_classification(
                image_source, detection_confidence
            )
            mode = "heuristic_fallback"
        pressure = float(np.clip(1012.0 - wind * 0.42, 900.0, 1010.0))
        return {
            "classification": category["name"], "short_code": category["short"],
            "confidence": round(confidence, 4),
            "estimated_wind_speed_kmph": round(wind, 1),
            "estimated_pressure_hpa": round(pressure, 1),
            "severity": category["severity"], "color": category["color"],
            "model_mode": mode,
            "class_probabilities": (
                {name: round(float(value), 4) for name, value in zip(self.class_names, probabilities)}
                if probabilities is not None else None
            ),
        }
