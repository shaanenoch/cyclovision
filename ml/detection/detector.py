import numpy as np
import cv2
from typing import Dict, Any, Optional
from preprocessing.image_preprocessing import load_image_to_numpy, enhance_cloud_patterns, estimate_vortex_center, resize_and_normalize

class CycloneDetector:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        """
        Loads trained PyTorch detection model if available.
        """
        try:
            import torch
            import torchvision.models as models
            # We can use MobileNetV3-Small backbone
            if self.model_path and Path(self.model_path).exists():
                self.model = torch.load(self.model_path, map_location='cpu')
                self.model.eval()
        except Exception:
            self.model = None

    def detect(self, image_source, metadata_bounds: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Analyzes satellite image for tropical cyclone signature:
        - Detects cyclonic spiral structure and central dense overcast (CDO).
        - Estimates center of circulation / eye.
        - Calculates confidence score based on structural vorticity and convective symmetry.
        """
        img_rgb = load_image_to_numpy(image_source)
        h, w, _ = img_rgb.shape
        
        # Preprocess cloud patterns
        enhanced = enhance_cloud_patterns(img_rgb)
        
        # Estimate vortex center in pixel coordinates
        vortex_info = estimate_vortex_center(enhanced)
        cx = vortex_info["pixel_x"]
        cy = vortex_info["pixel_y"]
        bbox = vortex_info["bounding_box"]
        
        # Analyze spiral banding curvature and central dense overcast
        gray = cv2.cvtColor(enhanced, cv2.COLOR_RGB2GRAY)
        
        # Gradient orientation circularity check
        sobelx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=5)
        magnitude, angle = cv2.cartToPolar(sobelx, sobely, angleInDegrees=True)
        
        # Calculate angular symmetry around center (cx, cy)
        # Strong cyclones exhibit high tangential gradients around the eye
        y_coords, x_coords = np.indices((h, w))
        dx = x_coords - cx
        dy = y_coords - cy
        dist = np.sqrt(dx**2 + dy**2)
        
        # Sample eye-wall zone (radius between 20 and 80 pixels)
        eyewall_mask = (dist > 15) & (dist < min(w, h) * 0.35)
        tangential_alignment = 0.0
        
        if np.sum(eyewall_mask) > 100:
            rad_angle = np.degrees(np.arctan2(dy, dx)) % 360
            grad_tangent_diff = np.abs((angle[eyewall_mask] - rad_angle[eyewall_mask] - 90) % 180)
            tangential_alignment = float(np.mean(grad_tangent_diff < 35))
            
        # Convective cloud mass ratio
        convective_fraction = float(np.mean(gray > 160))
        
        # Calculate genuine structural confidence score
        base_confidence = 0.60 + (tangential_alignment * 0.25) + (min(convective_fraction * 1.5, 0.14))
        confidence = float(np.clip(round(base_confidence, 2), 0.55, 0.98))
        
        cyclone_detected = confidence >= 0.65
        
        # Coordinate calculation: Only map to geographic coordinates if geo-bounds metadata is present!
        geo_lat = None
        geo_lon = None
        coord_note = "Coordinates require georeferenced satellite metadata or user input; pixel coordinates estimated."
        
        if metadata_bounds:
            min_lat = metadata_bounds.get("min_lat")
            max_lat = metadata_bounds.get("max_lat")
            min_lon = metadata_bounds.get("min_lon")
            max_lon = metadata_bounds.get("max_lon")
            if min_lat is not None and max_lat is not None and min_lon is not None and max_lon is not None:
                # Linear interpolation from pixel grid to geographic grid
                geo_lat = round(max_lat - (cy / h) * (max_lat - min_lat), 2)
                geo_lon = round(min_lon + (cx / w) * (max_lon - min_lon), 2)
                coord_note = "Geographic coordinates mapped from satellite georeferenced boundary metadata."

        pattern = "Organized Eyewall & Convective Spiral Bands" if confidence > 0.85 else "Curved Cloud Band Formation"

        return {
            "cyclone_detected": cyclone_detected,
            "confidence": confidence,
            "center": {
                "pixel_x": cx,
                "pixel_y": cy,
                "norm_x": vortex_info["norm_x"],
                "norm_y": vortex_info["norm_y"],
                "latitude": geo_lat,
                "longitude": geo_lon,
                "method": "Vorticity & Convective Mass Centroid",
                "note": coord_note
            },
            "bounding_box": bbox,
            "pattern_type": pattern,
            "convective_coverage_pct": round(convective_fraction * 100, 1)
        }
