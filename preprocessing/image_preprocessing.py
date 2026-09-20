import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple, Optional, Dict, Any

def load_image_to_numpy(image_source) -> np.ndarray:
    """
    Loads an image from filepath, bytes, or PIL Image into a NumPy array (RGB).
    """
    if isinstance(image_source, (str, bytes, bytearray)):
        if isinstance(image_source, str):
            image = Image.open(image_source).convert('RGB')
        else:
            image = Image.open(io.BytesIO(image_source)).convert('RGB')
        return np.array(image)
    elif isinstance(image_source, Image.Image):
        return np.array(image_source.convert('RGB'))
    elif isinstance(image_source, np.ndarray):
        if len(image_source.shape) == 2:
            return cv2.cvtColor(image_source, cv2.COLOR_GRAY2RGB)
        elif image_source.shape[2] == 4:
            return cv2.cvtColor(image_source, cv2.COLOR_RGBA2RGB)
        return image_source
    else:
        raise ValueError("Unsupported image source type")

def apply_clahe_contrast(img_rgb: np.ndarray, clip_limit: float = 2.5, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """
    Applies Contrast Limited Adaptive Histogram Equalization (CLAHE) on the L-channel (LAB color space)
    to enhance faint spiral rainbands and eye definition in satellite imagery.
    """
    lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    l_enhanced = clahe.apply(l)
    lab_enhanced = cv2.merge((l_enhanced, a, b))
    return cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)

def reduce_noise(img_rgb: np.ndarray) -> np.ndarray:
    """
    Reduces high-frequency sensor noise using bilateral filtering which preserves sharp storm edge boundaries.
    """
    return cv2.bilateralFilter(img_rgb, d=5, sigmaColor=50, sigmaSpace=50)

def enhance_cloud_patterns(img_rgb: np.ndarray) -> np.ndarray:
    """
    Preprocesses cloud patterns by combining bilateral noise reduction and CLAHE contrast enhancement.
    """
    denoised = reduce_noise(img_rgb)
    enhanced = apply_clahe_contrast(denoised)
    return enhanced

def resize_and_normalize(img_rgb: np.ndarray, target_size: Tuple[int, int] = (224, 224)) -> Tuple[np.ndarray, np.ndarray]:
    """
    Resizes image to target dimensions and produces:
    1. Display-ready uint8 array (0-255)
    2. Model-ready float32 array normalized with ImageNet stats (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    """
    resized = cv2.resize(img_rgb, target_size, interpolation=cv2.INTER_AREA)
    display_ready = resized.copy()
    
    # Normalized for PyTorch backbone
    float_img = resized.astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    normalized = (float_img - mean) / std
    
    # Transpose to (Channels, Height, Width)
    chw_normalized = np.transpose(normalized, (2, 0, 1))
    return display_ready, chw_normalized

def estimate_vortex_center(img_rgb: np.ndarray) -> Dict[str, Any]:
    """
    Estimates pixel coordinates of the cyclone center/eye based on cloud density gradient and circular symmetry.
    Returns pixel_x, pixel_y, and a bounding region.
    """
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape
    
    # Gaussian blur to smooth convective cloud tops
    blurred = cv2.GaussianBlur(gray, (15, 15), 0)
    
    # Minimum intensity inside the eyewall or center of highest convective mass
    # In IR imagery, the eyewall is often warmest in the center eye or surrounded by the coldest tops
    # We find the center of mass of the high-vorticity convective cluster
    _, thresh = cv2.threshold(blurred, 140, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = w // 2, h // 2
        x, y, bw, bh = cv2.boundingRect(largest_contour)
    else:
        cx, cy = w // 2, h // 2
        x, y, bw, bh = w // 4, h // 4, w // 2, h // 2
        
    return {
        "pixel_x": cx,
        "pixel_y": cy,
        "norm_x": round(cx / w, 3),
        "norm_y": round(cy / h, 3),
        "bounding_box": {"x": int(x), "y": int(y), "width": int(bw), "height": int(bh)}
    }
