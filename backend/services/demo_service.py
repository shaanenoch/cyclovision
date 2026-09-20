import cv2
import csv
import numpy as np
from PIL import Image
from pathlib import Path
import json
from backend.config import DEMO_DATA_DIR, UPLOADS_DIR, DATA_DIR, TRACKS_DATA_DIR, SATELLITE_DATA_DIR
from backend.database.db import get_db_connection, init_db
from ml.explainability.gradcam import GradCamExplainer
from ml.evaluation.evaluator import ModelEvaluator

def generate_synthetic_cyclone_satellite_image(output_path: Path) -> Path:
    """
    Generates a realistic multi-spectral infrared (TIR1) satellite image of a mature tropical cyclone.
    Features:
    - Eye with distinct minimum / wall gradient
    - Logarithmic spiral convective rainbands (Curved Banding)
    - High-altitude cirrus outflow shield
    - Atmospheric noise
    """
    width, height = 512, 512
    img = np.zeros((height, width), dtype=np.float32)
    center_x, center_y = width // 2, height // 2
    
    # 1. Background ocean thermal temperature (warm ~ 295 K)
    background = np.random.normal(50, 5, (height, width))
    img += background
    
    # 2. Central Dense Overcast (CDO) mass
    y_grid, x_grid = np.ogrid[:height, :width]
    r = np.sqrt((x_grid - center_x)**2 + (y_grid - center_y)**2)
    cdo = 190.0 * np.exp(-(r**2) / (2 * (110.0**2)))
    img += cdo
    
    # 3. Logarithmic spiral rainbands
    theta = np.arctan2(y_grid - center_y, x_grid - center_x)
    num_arms = 3
    for arm in range(num_arms):
        arm_offset = arm * (2 * np.pi / num_arms)
        # Spiral equation: r = a * exp(b * theta)
        spiral_phase = (theta + arm_offset - 0.45 * np.log(np.maximum(r, 1.0) / 15.0)) % (2 * np.pi)
        band_intensity = np.exp(-((spiral_phase - np.pi)**2) / 0.35)
        radial_envelope = (r / 200.0) * np.exp(-r / 140.0) * 350.0
        img += band_intensity * radial_envelope
        
    # 4. Cyclone Eye (warmer cloud-free center surrounded by deep eyewall)
    eye_radius = 18.0
    eye_mask = np.exp(-(r**2) / (2 * (eye_radius**2)))
    # Eyewall peak at r ~ 25px
    eyewall_ring = np.exp(-((r - 28.0)**2) / (2 * (8.0**2))) * 110.0
    img = img * (1.0 - 0.75 * eye_mask) + eyewall_ring
    
    # Clip and convert to uint8
    normalized = np.clip(img, 0, 255).astype(np.uint8)
    
    # False-color infrared meteorological palette (IR enhancement)
    ir_colored = cv2.applyColorMap(normalized, cv2.COLORMAP_VIRIDIS)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(cv2.cvtColor(ir_colored, cv2.COLOR_BGR2RGB)).save(output_path)
    return output_path

def init_demo_data():
    """
    Initializes all demo assets, database entries, and files for instant SIH demonstration.
    """
    init_db()
    
    demo_image_path = DEMO_DATA_DIR / "demo_satellite_ir.png"
    demo_heatmap_path = DEMO_DATA_DIR / "demo_heatmap.png"
    demo_track_csv = DEMO_DATA_DIR / "demo_cyclone_01_track.csv"
    
    # Copy to uploads so frontend can serve them directly
    upload_img_path = UPLOADS_DIR / "demo_cyclone_01_sat.png"
    upload_heat_path = UPLOADS_DIR / "demo_cyclone_01_heat.png"
    
    # 1. Generate Satellite Image if needed
    if not demo_image_path.exists():
        generate_synthetic_cyclone_satellite_image(demo_image_path)
        
    # Always ensure copy in uploads
    Image.open(demo_image_path).save(upload_img_path)
    
    # 2. Generate Grad-CAM Heatmap
    explainer = GradCamExplainer()
    res = explainer.generate_heatmap(str(demo_image_path), output_filename="demo_cyclone_01_heat.png")
    Image.open(UPLOADS_DIR / "demo_cyclone_01_heat.png").save(demo_heatmap_path)
    
    # 3. Create Demo Track CSV
    track_records = [
        {"timestamp": "2026-09-19 00:00:00", "point_type": "historical", "latitude": 13.8, "longitude": 86.8, "wind_speed_kmph": 65.0, "pressure_hpa": 994.0, "classification": "Cyclonic Storm"},
        {"timestamp": "2026-09-19 06:00:00", "point_type": "historical", "latitude": 14.2, "longitude": 86.1, "wind_speed_kmph": 78.0, "pressure_hpa": 990.0, "classification": "Cyclonic Storm"},
        {"timestamp": "2026-09-19 12:00:00", "point_type": "historical", "latitude": 14.6, "longitude": 85.5, "wind_speed_kmph": 90.0, "pressure_hpa": 986.0, "classification": "Severe Cyclonic Storm"},
        {"timestamp": "2026-09-19 18:00:00", "point_type": "historical", "latitude": 14.9, "longitude": 85.0, "wind_speed_kmph": 105.0, "pressure_hpa": 982.0, "classification": "Severe Cyclonic Storm"},
        {"timestamp": "2026-09-20 00:00:00", "point_type": "current", "latitude": 15.2, "longitude": 84.7, "wind_speed_kmph": 115.0, "pressure_hpa": 978.0, "classification": "Severe Cyclonic Storm"},
        {"timestamp": "2026-09-20 06:00:00", "point_type": "forecast", "forecast_hour": 6, "latitude": 15.8, "longitude": 84.2, "wind_speed_kmph": 125.0, "pressure_hpa": 972.0, "classification": "Very Severe Cyclonic Storm"},
        {"timestamp": "2026-09-20 12:00:00", "point_type": "forecast", "forecast_hour": 12, "latitude": 16.3, "longitude": 83.7, "wind_speed_kmph": 135.0, "pressure_hpa": 968.0, "classification": "Very Severe Cyclonic Storm"},
        {"timestamp": "2026-09-21 00:00:00", "point_type": "forecast", "forecast_hour": 24, "latitude": 17.1, "longitude": 82.9, "wind_speed_kmph": 145.0, "pressure_hpa": 962.0, "classification": "Very Severe Cyclonic Storm"},
        {"timestamp": "2026-09-21 12:00:00", "point_type": "forecast", "forecast_hour": 36, "latitude": 18.0, "longitude": 82.3, "wind_speed_kmph": 120.0, "pressure_hpa": 974.0, "classification": "Very Severe Cyclonic Storm"},
        {"timestamp": "2026-09-22 00:00:00", "point_type": "forecast", "forecast_hour": 48, "latitude": 19.1, "longitude": 81.9, "wind_speed_kmph": 85.0, "pressure_hpa": 988.0, "classification": "Cyclonic Storm"},
    ]
    fieldnames = ['timestamp', 'point_type', 'forecast_hour', 'latitude', 'longitude', 'wind_speed_kmph', 'pressure_hpa', 'classification']
    for rec in track_records:
        if 'forecast_hour' not in rec:
            rec['forecast_hour'] = 0
    with open(demo_track_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(track_records)
    
    # 4. Insert into database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM cyclones WHERE id = 'demo-cyclone-01'")
    cursor.execute("DELETE FROM track_points WHERE cyclone_id = 'demo-cyclone-01'")
    
    cursor.execute("""
    INSERT INTO cyclones (
        id, name, status, is_active, basin, current_lat, current_lon,
        wind_speed_kmph, pressure_hpa, movement_direction, movement_speed_kmph,
        nearest_coastal_point, estimated_trajectory_summary, is_demo,
        satellite_image_url, heatmap_url
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'demo-cyclone-01',
        'Demo Cyclone 01',
        'Severe Cyclonic Storm',
        1,
        'Bay of Bengal (North Indian Ocean)',
        15.2,
        84.7,
        115.0,
        978.0,
        'North-West',
        18.5,
        'Visakhapatnam (approx. 270 km NW)',
        'Expected track towards the north-western Bay of Bengal, approaching Andhra Pradesh and South Odisha coast.',
        1,
        '/uploads/demo_cyclone_01_sat.png',
        '/uploads/demo_cyclone_01_heat.png'
    ))
    
    for pt in track_records:
        cursor.execute("""
        INSERT INTO track_points (
            cyclone_id, point_type, forecast_hour, latitude, longitude,
            wind_speed_kmph, pressure_hpa, classification, timestamp_str
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'demo-cyclone-01',
            pt.get("point_type", "historical"),
            pt.get("forecast_hour", 0),
            pt["latitude"],
            pt["longitude"],
            pt["wind_speed_kmph"],
            pt["pressure_hpa"],
            pt["classification"],
            pt["timestamp"]
        ))
        
    conn.commit()
    conn.close()
    
    # 5. Run real evaluation to populate demo_metrics.json
    evaluator = ModelEvaluator()
    evaluator.run_evaluation()

if __name__ == "__main__":
    init_demo_data()
    print("Demo dataset initialized successfully.")
