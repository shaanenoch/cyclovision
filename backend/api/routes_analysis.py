import time
import uuid
from io import BytesIO
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List, Dict, Any
from PIL import Image, ImageOps, UnidentifiedImageError

from backend.config import UPLOADS_DIR, DEMO_DATA_DIR, DISCLAIMER_TEXT, EXPLAINABILITY_CAPTION
from backend.schemas.schemas import TrackPredictionRequest, TrackPredictionResponse, AnalysisResponse
from ml.detection.detector import CycloneDetector
from ml.classification.classifier import CycloneClassifier
from ml.explainability.gradcam import GradCamExplainer
from ml.prediction.track_predictor import TrackPredictor
from preprocessing.image_preprocessing import load_image_to_numpy
from preprocessing.netcdf_preprocessing import parse_netcdf_file

router = APIRouter()

detector = CycloneDetector()
classifier = CycloneClassifier()
explainer = GradCamExplainer(classifier.model)
predictor = TrackPredictor()

ALLOWED_UPLOAD_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.nc'}
MAX_UPLOAD_BYTES = 50 * 1024 * 1024


async def save_validated_upload(file: UploadFile, prefix: str):
    """Validate an upload and return a model-ready local path and public URL."""
    file_ext = Path(file.filename or '').suffix.lower()
    if file_ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload JPG, PNG, TIFF or NetCDF data.",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="The uploaded file is larger than 50 MB.")

    unique_id = uuid.uuid4().hex[:8]
    if file_ext == '.nc':
        save_name = f"{prefix}_{unique_id}.nc"
        save_path = UPLOADS_DIR / save_name
        save_path.write_bytes(contents)
        return str(save_path), f"/uploads/{save_name}", file_ext

    # Decode first, apply EXIF orientation, and normalize every supported image
    # to RGB PNG. This safely handles grayscale, CMYK, palette and TIFF inputs.
    try:
        with Image.open(BytesIO(contents)) as uploaded_image:
            uploaded_image.load()
            image_rgb = ImageOps.exif_transpose(uploaded_image).convert('RGB')
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise HTTPException(
            status_code=422,
            detail="The selected file has an image extension but its contents are not a readable JPG, PNG or TIFF image.",
        ) from exc

    save_name = f"{prefix}_{unique_id}.png"
    save_path = UPLOADS_DIR / save_name
    image_rgb.save(save_path, format='PNG')
    return str(save_path), f"/uploads/{save_name}", file_ext

@router.post("/detect")
async def detect_cyclone(
    file: Optional[UploadFile] = File(None),
    is_demo: bool = Form(False)
):
    """
    Detects whether a cyclone signature is present in the satellite image,
    returns confidence and estimated circulation center.
    """
    if file and file.filename:
        target_path, _public_url, file_ext = await save_validated_upload(file, 'det')
        if file_ext == '.nc':
            raise HTTPException(status_code=400, detail="Use the full analysis endpoint for NetCDF data.")
    else:
        target_path = str(DEMO_DATA_DIR / "demo_satellite_ir.png")
        is_demo = True

    result = detector.detect(target_path)
    result["is_demo"] = is_demo
    return result

@router.post("/classify")
async def classify_cyclone(
    file: Optional[UploadFile] = File(None),
    is_demo: bool = Form(False)
):
    """
    Classifies cyclone intensity into IMD categories.
    """
    if file and file.filename:
        target_path, _public_url, file_ext = await save_validated_upload(file, 'cls')
        if file_ext == '.nc':
            raise HTTPException(status_code=400, detail="Use the full analysis endpoint for NetCDF data.")
    else:
        target_path = str(DEMO_DATA_DIR / "demo_satellite_ir.png")
        is_demo = True

    result = classifier.classify_image(target_path)
    result["is_demo"] = is_demo
    return result

@router.post("/predict-track", response_model=TrackPredictionResponse)
def predict_track_endpoint(payload: TrackPredictionRequest):
    """
    Predicts +6h, +12h, +24h, +36h, +48h trajectory and intensity.
    """
    forecast_points = predictor.predict_track(
        current_lat=payload.current_lat,
        current_lon=payload.current_lon,
        wind_speed_kmph=payload.wind_speed_kmph or 95.0,
        pressure_hpa=payload.pressure_hpa or 985.0,
        movement_bearing_deg=payload.movement_bearing_deg or 315.0,
        movement_speed_kmph=payload.movement_speed_kmph or 16.0,
        track_history=payload.historical_points
    )
    return {
        "cyclone_name": payload.cyclone_name or "Target System",
        "current_position": {
            "latitude": payload.current_lat,
            "longitude": payload.current_lon
        },
        "forecast": forecast_points,
        "model_name": predictor.model_name,
        "disclaimer": DISCLAIMER_TEXT
    }

@router.post("/predict-intensity")
def predict_intensity_endpoint(
    current_wind_kmph: float = 95.0,
    current_pressure_hpa: float = 985.0
):
    """
    Returns forward intensity projections (+6h to +48h).
    """
    # Sample from standard 15.2, 84.7 baseline
    forecast_points = predictor.predict_track(
        current_lat=15.2,
        current_lon=84.7,
        wind_speed_kmph=current_wind_kmph,
        pressure_hpa=current_pressure_hpa
    )
    return {
        "intensity_trend": [
            {
                "hour": pt["forecast_hour"],
                "wind_speed_kmph": pt["wind_speed_kmph"],
                "pressure_hpa": pt["pressure_hpa"],
                "category": pt["classification"]
            }
            for pt in forecast_points
        ]
    }

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_full_pipeline(
    file: Optional[UploadFile] = File(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    is_demo: bool = Form(False)
):
    """
    End-to-end operational pipeline:
    Satellite Ingestion -> Detection -> Classification -> Center Estimation -> Grad-CAM Heatmap -> Track Prediction
    """
    t_start = time.time()
    
    if file and file.filename:
        target_path, original_img_url, file_ext = await save_validated_upload(file, 'sat')
        is_demo_used = False
        dataset_label = "User Uploaded Satellite Observation"

        # Convert the selected radiance/brightness-temperature channel to a
        # display/model array before passing a NetCDF file into vision code.
        if file_ext == '.nc':
            try:
                nc_info = parse_netcdf_file(target_path)
            except (RuntimeError, ValueError, OSError) as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
            extracted = nc_info.get("extracted_image_rgb")
            if extracted is None:
                raise HTTPException(status_code=422, detail="No usable 2D satellite channel found in NetCDF file.")
            converted_name = f"sat_{uuid.uuid4().hex[:8]}_netcdf.png"
            converted_path = UPLOADS_DIR / converted_name
            Image.fromarray(extracted).save(converted_path)
            target_path = str(converted_path)
            original_img_url = f"/uploads/{converted_name}"
            dataset_label = f"NetCDF: {nc_info.get('selected_variable', 'satellite channel')}"
            metadata_bounds = nc_info.get("bounds")
        else:
            metadata_bounds = None
    else:
        # Load demo satellite image
        target_path = str(DEMO_DATA_DIR / "demo_satellite_ir.png")
        original_img_url = "/uploads/demo_cyclone_01_sat.png"
        is_demo_used = True
        dataset_label = "Demonstration Dataset (Demo Cyclone 01)"

    # 1. Detection & Eye Location
    metadata_bounds = locals().get("metadata_bounds")
    if latitude is not None and longitude is not None:
        metadata_bounds = {
            "min_lat": latitude - 4.0,
            "max_lat": latitude + 4.0,
            "min_lon": longitude - 4.0,
            "max_lon": longitude + 4.0
        }
    try:
        det = detector.detect(target_path, metadata_bounds=metadata_bounds)

        # 2. Classification & Intensity
        cls = classifier.classify_image(target_path, detection_confidence=det["confidence"])

        # 3. Grad-CAM Heatmap
        heat_filename = f"heat_{uuid.uuid4().hex[:8]}.png"
        heat_res = explainer.generate_heatmap(target_path, output_filename=heat_filename)
    except (OSError, ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"The image was uploaded, but cyclone analysis could not process it: {exc}",
        ) from exc

    # 4. Center coordinates
    curr_lat = det["center"]["latitude"] or (latitude if latitude is not None else 15.2)
    curr_lon = det["center"]["longitude"] or (longitude if longitude is not None else 84.7)

    # 5. Track Prediction
    forecast_points = predictor.predict_track(
        current_lat=curr_lat,
        current_lon=curr_lon,
        wind_speed_kmph=cls["estimated_wind_speed_kmph"],
        pressure_hpa=cls["estimated_pressure_hpa"]
    )

    t_elapsed = round((time.time() - t_start) * 1000, 1)

    return {
        "cyclone_detected": det["cyclone_detected"],
        "classification": cls["classification"],
        "detection_confidence": det["confidence"],
        "current_position": {
            "lat": curr_lat,
            "lon": curr_lon
        },
        "wind_speed": cls["estimated_wind_speed_kmph"],
        "pressure": cls["estimated_pressure_hpa"],
        "movement_direction": "North-West",
        "movement_speed_kmph": 18.5,
        "forecast": forecast_points,
        "heatmap_url": heat_res["heatmap_url"],
        "original_image_url": original_img_url,
        "model_version": (
            f"Classifier: {cls['model_mode']} | Track: "
            f"{predictor.metadata.get('model_version', 'physical-fallback')}"
        ),
        "is_demo": is_demo_used,
        "dataset_label": dataset_label,
        "disclaimer": DISCLAIMER_TEXT,
        "explainability_caption": heat_res["caption"],
        "execution_time_ms": t_elapsed
    }
