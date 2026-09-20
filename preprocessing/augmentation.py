import cv2
import numpy as np
import random
from typing import Tuple

def rotate_image(img: np.ndarray, angle_deg: int) -> np.ndarray:
    """
    Rotates image by 90, 180, or 270 degrees without clipping.
    """
    if angle_deg == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif angle_deg == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    elif angle_deg == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img

def flip_image(img: np.ndarray, mode: str = 'horizontal') -> np.ndarray:
    """
    Flips image horizontally or vertically.
    """
    if mode == 'horizontal':
        return cv2.flip(img, 1)
    elif mode == 'vertical':
        return cv2.flip(img, 0)
    elif mode == 'both':
        return cv2.flip(img, -1)
    return img

def adjust_brightness_contrast(img: np.ndarray, alpha: float = 1.0, beta: int = 0) -> np.ndarray:
    """
    Adjusts brightness (beta) and contrast (alpha).
    """
    adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    return adjusted

def add_satellite_sensor_noise(img: np.ndarray, noise_sigma: float = 8.0) -> np.ndarray:
    """
    Simulates satellite scanline / radiometric noise.
    """
    h, w, c = img.shape
    noise = np.random.normal(0, noise_sigma, (h, w, c)).astype(np.float32)
    noisy = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return noisy

def random_satellite_augmentation(img: np.ndarray) -> np.ndarray:
    """
    Applies a randomized pipeline of meteorological-safe transformations.
    """
    augmented = img.copy()
    
    # Random 90 deg rotation
    angle = random.choice([0, 90, 180, 270])
    if angle > 0:
        augmented = rotate_image(augmented, angle)
        
    # Random flip
    flip_choice = random.choice(['none', 'horizontal', 'vertical'])
    if flip_choice != 'none':
        augmented = flip_image(augmented, flip_choice)
        
    # Slight brightness/contrast shift
    alpha = random.uniform(0.85, 1.15)
    beta = random.randint(-15, 15)
    augmented = adjust_brightness_contrast(augmented, alpha, beta)
    
    return augmented
