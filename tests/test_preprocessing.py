import pytest
import numpy as np
from preprocessing.track_preprocessing import validate_coordinates, calculate_haversine_distance_km, calculate_bearing_deg, bearing_to_compass
from preprocessing.image_preprocessing import apply_clahe_contrast, resize_and_normalize, estimate_vortex_center

def test_validate_coordinates():
    assert validate_coordinates(15.2, 84.7) is True
    assert validate_coordinates(-90.0, 180.0) is True
    assert validate_coordinates(95.0, 50.0) is False # Invalid latitude
    assert validate_coordinates(10.0, 190.0) is False # Invalid longitude
    assert validate_coordinates(None, 80.0) is False

def test_haversine_distance():
    # Distance between Puri (19.81, 85.83) and Visakhapatnam (17.68, 83.21) ~ 350-360 km
    dist = calculate_haversine_distance_km(19.81, 85.83, 17.68, 83.21)
    assert 340.0 < dist < 370.0

def test_bearing_calculation():
    # Moving due North
    b_north = calculate_bearing_deg(10.0, 80.0, 12.0, 80.0)
    assert abs(b_north - 0.0) < 1.0 or abs(b_north - 360.0) < 1.0
    assert "North" in bearing_to_compass(b_north)
    
    # Moving North-West typical for Bay of Bengal cyclones
    b_nw = calculate_bearing_deg(14.0, 86.0, 16.0, 84.0)
    assert 300.0 < b_nw < 330.0
    assert "North-West" in bearing_to_compass(b_nw)

def test_image_preprocessing():
    dummy_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
    enhanced = apply_clahe_contrast(dummy_img)
    assert enhanced.shape == (100, 100, 3)
    
    display, normalized = resize_and_normalize(dummy_img, (224, 224))
    assert display.shape == (224, 224, 3)
    assert normalized.shape == (3, 224, 224)
    
    vortex = estimate_vortex_center(dummy_img)
    assert "pixel_x" in vortex
    assert "pixel_y" in vortex
    assert "bounding_box" in vortex
