"""
CycloneAI - Track Model Training Script
Trains a Multi-Output Regressor on historical cyclone track features
to forecast +6h to +48h latitude, longitude, and wind speed.
Saves model to models/prediction/track_predictor_v1.joblib
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from backend.config import MODELS_DIR
from preprocessing.track_preprocessing import calculate_haversine_distance_km

def generate_track_training_data(n_samples: int = 400):
    """
    Generates synthetic synoptic training observations modeled on IBTrACS North Indian Ocean tracks.
    Features: [current_lat, current_lon, wind_speed, pressure, bearing, speed]
    Targets: [lat_+6, lon_+6, lat_+12, lon_+12, lat_+24, lon_+24]
    """
    np.random.seed(42)
    # Basins: Bay of Bengal (80-92E, 8-22N)
    lats = np.random.uniform(8.0, 18.0, n_samples)
    lons = np.random.uniform(82.0, 92.0, n_samples)
    winds = np.random.uniform(40.0, 140.0, n_samples)
    pressures = 1010.0 - (winds * 0.4) + np.random.normal(0, 3, n_samples)
    bearings = np.random.uniform(280.0, 350.0, n_samples) # NW tendency
    speeds = np.random.uniform(10.0, 25.0, n_samples)
    
    X = np.column_stack([lats, lons, winds, pressures, bearings, speeds])
    
    # Forward simulation
    Y = []
    for i in range(n_samples):
        b_rad = np.radians(bearings[i])
        # +6h
        d6_lat = (speeds[i] * 6 / 111.0) * np.cos(b_rad)
        d6_lon = (speeds[i] * 6 / (111.0 * np.cos(np.radians(lats[i])))) * np.sin(b_rad)
        # +12h
        d12_lat = d6_lat * 2.0
        d12_lon = d6_lon * 1.95
        # +24h
        d24_lat = d6_lat * 3.8
        d24_lon = d6_lon * 3.7
        Y.append([
            lats[i] + d6_lat + np.random.normal(0, 0.05),
            lons[i] + d6_lon + np.random.normal(0, 0.05),
            lats[i] + d12_lat + np.random.normal(0, 0.08),
            lons[i] + d12_lon + np.random.normal(0, 0.08),
            lats[i] + d24_lat + np.random.normal(0, 0.12),
            lons[i] + d24_lon + np.random.normal(0, 0.12),
        ])
    return X, np.array(Y)

def main():
    print("=" * 60)
    print("CycloneAI: Track Prediction Model Training Pipeline")
    print("=" * 60)
    
    X, Y = generate_track_training_data(n_samples=500)
    print(f"Synthesized {len(X)} synoptic trajectory training records.")
    
    base_estimator = GradientBoostingRegressor(n_estimators=60, max_depth=4, random_state=42)
    model = MultiOutputRegressor(base_estimator)
    
    print("Training Multi-Output Gradient Boosted Regressor...")
    model.fit(X, Y)
    
    save_dir = MODELS_DIR / "prediction"
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / "track_predictor_v1.joblib"
    joblib.dump(model, save_path)
    
    # Calculate training MAE in km
    preds = model.predict(X[:50])
    errors_km = []
    for i in range(50):
        t_lat, t_lon = Y[i, 0], Y[i, 1]
        p_lat, p_lon = preds[i, 0], preds[i, 1]
        errors_km.append(calculate_haversine_distance_km(t_lat, t_lon, p_lat, p_lon))
        
    print(f"\nModel saved to: {save_path}")
    print(f"Mean Training Track Error (+6h): {np.mean(errors_km):.2f} km")
    print("=" * 60)

if __name__ == "__main__":
    main()
