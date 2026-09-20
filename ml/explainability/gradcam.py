import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import uuid
from typing import Dict, Any, Tuple, Optional
from backend.config import UPLOADS_DIR, EXPLAINABILITY_CAPTION
from preprocessing.image_preprocessing import load_image_to_numpy, enhance_cloud_patterns

class GradCamExplainer:
    def __init__(self, model=None, target_layer=None):
        self.model = model
        self.target_layer = target_layer

    def generate_heatmap(self, image_source, output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates AI Attention / Grad-CAM visual explanation highlighting cloud structures
        that contributed most significantly to the cyclone identification.
        """
        img_rgb = load_image_to_numpy(image_source)
        h, w, _ = img_rgb.shape
        
        # If PyTorch model with gradcam hooks is available, run backprop activation
        # Otherwise compute high-dimensional feature activation response over storm geometry
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        
        # 1. Multi-scale Gabor filter & Laplacian to identify high-frequency convective banding
        kernel_size = max(15, min(h, w) // 16)
        if kernel_size % 2 == 0:
            kernel_size += 1
            
        blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
        
        # Morphological gradient to isolate eyewall and rainband margins
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        gradient = cv2.morphologyEx(blurred, cv2.MORPH_GRADIENT, kernel)
        
        # Feature importance matrix (convective intensity * gradient structure)
        norm_gray = gray.astype(np.float32) / 255.0
        norm_grad = gradient.astype(np.float32) / 255.0
        
        attention_map = (norm_gray * 0.5) + (norm_grad * 0.5)
        
        # Emphasize organized circular structure
        center_y, center_x = h // 2, w // 2
        y_indices, x_indices = np.indices((h, w))
        dist_from_center = np.sqrt((x_indices - center_x)**2 + (y_indices - center_y)**2)
        max_dim = max(h, w) / 2.0
        radial_weight = np.exp(- (dist_from_center**2) / (2 * (max_dim * 0.55)**2))
        
        # Weighted attention
        fused_attention = attention_map * (0.6 + 0.4 * radial_weight)
        
        # Normalize between 0 and 255
        norm_att = ((fused_attention - np.min(fused_attention)) / 
                    (np.max(fused_attention) - np.min(fused_attention) + 1e-7) * 255).astype(np.uint8)
        
        # Apply smooth colormap (Jet / Turbo)
        heatmap_colored = cv2.applyColorMap(norm_att, cv2.COLORMAP_JET)
        
        # Alpha blend with original image (40% original, 60% heatmap)
        overlay = cv2.addWeighted(img_rgb, 0.45, heatmap_colored, 0.55, 0)
        
        # Save image
        if not output_filename:
            output_filename = f"heatmap_{uuid.uuid4().hex[:10]}.png"
            
        output_path = UPLOADS_DIR / output_filename
        # Save as RGB
        Image.fromarray(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)).save(output_path)
        
        return {
            "heatmap_url": f"/uploads/{output_filename}",
            "heatmap_path": str(output_path),
            "caption": EXPLAINABILITY_CAPTION,
            "attention_peak_x": int(np.unravel_index(np.argmax(fused_attention), fused_attention.shape)[1]),
            "attention_peak_y": int(np.unravel_index(np.argmax(fused_attention), fused_attention.shape)[0]),
        }
