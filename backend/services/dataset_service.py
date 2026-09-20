import csv
import json
import uuid
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image
from backend.config import UPLOADS_DIR, RAW_DATA_DIR, TRACKS_DATA_DIR, SATELLITE_DATA_DIR
from backend.database.db import get_db_connection
from preprocessing.netcdf_preprocessing import parse_netcdf_file
from preprocessing.track_preprocessing import clean_and_sort_track_csv, extract_track_features
from ml.detection.detector import CycloneDetector
from ml.classification.classifier import CycloneClassifier
from ml.explainability.gradcam import GradCamExplainer
from ml.prediction.track_predictor import TrackPredictor

def process_uploaded_dataset(
    file_bytes: bytes,
    original_filename: str,
    purpose: str = "Live/New Cyclone Observation"
) -> Dict[str, Any]:
    """
    Ingests and validates uploaded dataset files (.csv, .json, .nc, .png, .jpg, .jpeg, .tif)
    without requiring source code modification.
    """
    file_id = f"ds_{uuid.uuid4().hex[:10]}"
    ext = Path(original_filename).suffix.lower()
    
    # Store in uploads
    saved_filename = f"{file_id}_{original_filename}"
    saved_path = UPLOADS_DIR / saved_filename
    with open(saved_path, 'wb') as f:
        f.write(file_bytes)
        
    file_size_kb = round(len(file_bytes) / 1024.0, 2)
    records_count = 0
    columns: List[str] = []
    preview: List[Dict[str, Any]] = []
    status = "Validated & Ready"

    if ext == '.csv':
        try:
            records = clean_and_sort_track_csv(str(saved_path))
            records_count = len(records)
            if records:
                columns = list(records[0].keys())
                preview = records[:8]
            else:
                # Read raw CSV headers if specific cyclone columns missing
                with open(saved_path, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.DictReader(f)
                    columns = reader.fieldnames or []
                    preview = [row for i, row in enumerate(reader) if i < 8]
                    records_count = len(preview)
        except Exception as e:
            status = f"Warning: {str(e)[:40]}"

    elif ext == '.json':
        try:
            data = json.loads(file_bytes.decode('utf-8', errors='ignore'))
            if isinstance(data, list):
                records_count = len(data)
                if data and isinstance(data[0], dict):
                    columns = list(data[0].keys())
                    preview = data[:8]
            elif isinstance(data, dict):
                records_count = 1
                columns = list(data.keys())
                preview = [data]
        except Exception as e:
            status = f"Invalid JSON: {str(e)[:40]}"

    elif ext == '.nc':
        try:
            nc_info = parse_netcdf_file(str(saved_path))
            columns = nc_info.get("variables", [])
            records_count = nc_info.get("dimensions", {}).get("lat", 100)
            preview = [{
                "variable_count": len(columns),
                "grid_bounds": str(nc_info.get("bounds", "N/A")),
                "primary_sensor": nc_info.get("selected_variable", "Brightness Temp")
            }]
        except Exception as e:
            status = f"NetCDF Note: {str(e)[:40]}"

    elif ext in ['.png', '.jpg', '.jpeg', '.tif', '.tiff']:
        try:
            img = Image.open(saved_path)
            columns = ["width_px", "height_px", "color_mode", "format"]
            records_count = 1
            preview = [{
                "width_px": img.width,
                "height_px": img.height,
                "color_mode": img.mode,
                "format": img.format or ext[1:].upper()
            }]
        except Exception as e:
            status = f"Image error: {str(e)[:40]}"
    else:
        status = "Unsupported format"

    # Insert into database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO datasets (
        id, name, file_path, file_type, purpose, records_count,
        file_size_kb, columns_json, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        file_id,
        original_filename,
        f"/uploads/{saved_filename}",
        ext.replace('.', '').upper(),
        purpose,
        records_count,
        file_size_kb,
        json.dumps(columns),
        status
    ))
    conn.commit()
    conn.close()

    return {
        "id": file_id,
        "name": original_filename,
        "file_type": ext.replace('.', '').upper(),
        "purpose": purpose,
        "records_count": records_count,
        "file_size_kb": file_size_kb,
        "columns": columns,
        "date_uploaded": "Just now",
        "status": status,
        "preview": preview,
        "file_url": f"/uploads/{saved_filename}"
    }

def get_all_datasets() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM datasets ORDER BY date_uploaded DESC")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        cols = []
        try: cols = json.loads(r["columns_json"])
        except Exception: pass
        
        result.append({
            "id": r["id"],
            "name": r["name"],
            "file_type": r["file_type"],
            "purpose": r["purpose"],
            "records_count": r["records_count"],
            "file_size_kb": r["file_size_kb"],
            "columns": cols,
            "date_uploaded": str(r["date_uploaded"]),
            "status": r["status"],
            "preview": []
        })
    return result

def run_analysis_on_dataset_id(dataset_id: str) -> Dict[str, Any]:
    """
    Executes automated end-to-end pipeline on an uploaded dataset without altering code.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise ValueError(f"Dataset {dataset_id} not found")

    file_type = row["file_type"]
    file_path = UPLOADS_DIR / Path(row["file_path"]).name
    
    detector = CycloneDetector()
    classifier = CycloneClassifier()
    explainer = GradCamExplainer()
    predictor = TrackPredictor()

    if file_type in ['PNG', 'JPG', 'JPEG', 'TIF', 'TIFF']:
        # Full Vision Pipeline
        det = detector.detect(str(file_path))
        cls = classifier.classify_image(str(file_path), detection_confidence=det["confidence"])
        heat = explainer.generate_heatmap(str(file_path))
        
        # Track prediction from estimated or default position
        curr_lat = det["center"]["latitude"] or 15.2
        curr_lon = det["center"]["longitude"] or 84.7
        forecast = predictor.predict_track(
            current_lat=curr_lat,
            current_lon=curr_lon,
            wind_speed_kmph=cls["estimated_wind_speed_kmph"],
            pressure_hpa=cls["estimated_pressure_hpa"]
        )

        return {
            "dataset_id": dataset_id,
            "dataset_name": row["name"],
            "analysis_type": "Satellite Vision & Forward Trajectory",
            "detection": det,
            "classification": cls,
            "heatmap": heat,
            "forecast": forecast
        }

    elif file_type == 'CSV':
        records = clean_and_sort_track_csv(str(file_path))
        features = extract_track_features(records)
        forecast = predictor.predict_track(
            current_lat=features["current_lat"],
            current_lon=features["current_lon"],
            wind_speed_kmph=features["wind_speed_kmph"],
            pressure_hpa=features["pressure_hpa"],
            movement_bearing_deg=features["bearing_deg"],
            movement_speed_kmph=features["speed_kmph"]
        )
        return {
            "dataset_id": dataset_id,
            "dataset_name": row["name"],
            "analysis_type": "Historical Track Assimilation & Forecast",
            "extracted_features": features,
            "forecast": forecast
        }
    else:
        return {
            "dataset_id": dataset_id,
            "dataset_name": row["name"],
            "analysis_type": "Metadata Validation",
            "status": "Analyzed successfully",
            "message": f"Processed {file_type} dataset records."
        }
