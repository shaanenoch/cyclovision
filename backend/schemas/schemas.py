from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class GeoCoordinate(BaseModel):
    latitude: float
    longitude: float

class CenterEstimate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    pixel_x: Optional[int] = None
    pixel_y: Optional[int] = None
    method: str = "AI Eye/Vorticity Localization"
    note: Optional[str] = None

class ForecastPoint(BaseModel):
    forecast_hour: int
    latitude: float
    longitude: float
    wind_speed_kmph: float
    pressure_hpa: float
    classification: str
    category_color: str
    confidence_label: str = "model estimate"

class TrackPredictionRequest(BaseModel):
    cyclone_name: Optional[str] = "Cyclone Target"
    current_lat: float
    current_lon: float
    wind_speed_kmph: Optional[float] = 95.0
    pressure_hpa: Optional[float] = 985.0
    movement_bearing_deg: Optional[float] = 315.0 # NW
    movement_speed_kmph: Optional[float] = 18.0
    historical_points: Optional[List[Dict[str, Any]]] = None

class DetectionResponse(BaseModel):
    cyclone_detected: bool
    confidence: float
    center: CenterEstimate
    bounding_box: Optional[Dict[str, int]] = None
    heatmap_url: Optional[str] = None
    pattern_type: str = "Curved Band / Eye Wall"
    is_demo: bool = False
    note: str

class ClassificationResponse(BaseModel):
    classification: str
    short_code: str
    confidence: float
    estimated_wind_speed_kmph: float
    estimated_pressure_hpa: float
    severity: str
    color: str
    is_demo: bool = False

class TrackPredictionResponse(BaseModel):
    cyclone_name: str
    current_position: GeoCoordinate
    forecast: List[ForecastPoint]
    model_name: str = "Gradient Boosted Multi-Output Regressor"
    disclaimer: str

class AnalysisResponse(BaseModel):
    cyclone_detected: bool
    classification: str
    detection_confidence: float
    current_position: Dict[str, Optional[float]]
    wind_speed: float
    pressure: float
    movement_direction: str
    movement_speed_kmph: float
    forecast: List[ForecastPoint]
    heatmap_url: Optional[str] = None
    original_image_url: Optional[str] = None
    model_version: str = "CycloneAI-v1.0"
    is_demo: bool = False
    dataset_label: str = "Live Operational / Demo Mode"
    disclaimer: str
    explainability_caption: str
    execution_time_ms: float

class CycloneInfo(BaseModel):
    id: str
    name: str
    status: str
    is_active: bool
    basin: str
    current_lat: float
    current_lon: float
    wind_speed_kmph: float
    pressure_hpa: float
    movement_direction: str
    movement_speed_kmph: float
    nearest_coastal_point: str
    estimated_trajectory_summary: str
    is_demo: bool
    satellite_image_url: str
    heatmap_url: str
    updated_at: str

class DatasetMetadata(BaseModel):
    id: str
    name: str
    file_type: str
    purpose: str
    records_count: int
    file_size_kb: float
    columns: List[str]
    date_uploaded: str
    status: str
    preview: List[Dict[str, Any]]

class ConfusionMatrixData(BaseModel):
    labels: List[str]
    matrix: List[List[int]]

class ModelMetricsResponse(BaseModel):
    model_trained: bool
    model_name: str
    model_version: str
    training_date: str
    dataset_size: int
    training_accuracy: float
    validation_accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: ConfusionMatrixData
    training_loss_history: List[Dict[str, Any]]
    accuracy_history: List[Dict[str, Any]]
    track_prediction_metrics: Dict[str, Any]
    disclaimer: str

class SearchResultItem(BaseModel):
    type: str # 'cyclone', 'region', 'coordinate'
    title: str
    subtitle: str
    lat: float
    lon: float
    related_cyclone: Optional[CycloneInfo] = None
