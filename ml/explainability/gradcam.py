from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import cv2
import numpy as np
from PIL import Image

from backend.config import UPLOADS_DIR
from preprocessing.image_preprocessing import load_image_to_numpy, resize_and_normalize


class GradCamExplainer:
    """Generate true Grad-CAM when a CNN is loaded, otherwise labelled saliency."""

    def __init__(self, model=None, target_layer=None):
        self.model = model
        self.target_layer = target_layer or (
            model.features[-1] if model is not None and hasattr(model, "features") else None
        )

    def _gradcam(self, image_rgb: np.ndarray) -> np.ndarray:
        import torch

        activations, gradients = [], []
        forward_hook = self.target_layer.register_forward_hook(
            lambda _module, _inputs, output: activations.append(output)
        )
        backward_hook = self.target_layer.register_full_backward_hook(
            lambda _module, _grad_input, grad_output: gradients.append(grad_output[0])
        )
        try:
            _, normalized = resize_and_normalize(image_rgb, (224, 224))
            tensor = torch.from_numpy(normalized).unsqueeze(0).float()
            self.model.zero_grad(set_to_none=True)
            logits = self.model(tensor)
            logits[0, int(logits.argmax(dim=1).item())].backward()
            weights = gradients[0].mean(dim=(2, 3), keepdim=True)
            cam = (weights * activations[0]).sum(dim=1).relu()[0]
            cam = cam.detach().cpu().numpy()
            cam -= cam.min()
            cam /= cam.max() + 1e-8
            return cv2.resize(cam, (image_rgb.shape[1], image_rgb.shape[0]))
        finally:
            forward_hook.remove()
            backward_hook.remove()

    @staticmethod
    def _saliency(image_rgb: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        size = max(15, min(gray.shape) // 16)
        size += 1 - size % 2
        blurred = cv2.GaussianBlur(gray, (size, size), 0)
        gradient = cv2.morphologyEx(
            blurred, cv2.MORPH_GRADIENT,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)),
        )
        attention = 0.5 * gray.astype(np.float32) / 255.0 + 0.5 * gradient.astype(np.float32) / 255.0
        attention -= attention.min()
        return attention / (attention.max() + 1e-8)

    def generate_heatmap(self, image_source, output_filename: Optional[str] = None) -> Dict[str, Any]:
        image_rgb = load_image_to_numpy(image_source)
        true_gradcam = self.model is not None and self.target_layer is not None
        attention = self._gradcam(image_rgb) if true_gradcam else self._saliency(image_rgb)
        colored_bgr = cv2.applyColorMap((attention * 255).astype(np.uint8), cv2.COLORMAP_TURBO)
        colored_rgb = cv2.cvtColor(colored_bgr, cv2.COLOR_BGR2RGB)
        overlay = cv2.addWeighted(image_rgb, 0.5, colored_rgb, 0.5, 0)
        output_filename = output_filename or f"heatmap_{uuid.uuid4().hex[:10]}.png"
        output_path = UPLOADS_DIR / output_filename
        Image.fromarray(overlay).save(output_path)
        peak_y, peak_x = np.unravel_index(np.argmax(attention), attention.shape)
        method = "Grad-CAM" if true_gradcam else "cloud-pattern saliency fallback"
        return {
            "heatmap_url": f"/uploads/{output_filename}", "heatmap_path": str(output_path),
            "caption": f"{method}: highlighted regions contributed most to this analysis.",
            "method": method, "is_model_explanation": true_gradcam,
            "attention_peak_x": int(peak_x), "attention_peak_y": int(peak_y),
        }
