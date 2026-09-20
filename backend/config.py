from pathlib import Path
from typing import Dict, Any

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SATELLITE_DATA_DIR = DATA_DIR / "satellite"
TRACKS_DATA_DIR = DATA_DIR / "tracks"
DEMO_DATA_DIR = DATA_DIR / "demo"
MODELS_DIR = BASE_DIR / "models"
UPLOADS_DIR = BASE_DIR / "uploads"
DATABASE_URL = f"sqlite:///{BASE_DIR / 'cyclone_ai.db'}"

# Ensure required directories exist
for folder in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, SATELLITE_DATA_DIR, 
               TRACKS_DATA_DIR, DEMO_DATA_DIR, MODELS_DIR, UPLOADS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Standard IMD (India Meteorological Department) & WMO Intensity Scale
CYCLONE_CATEGORIES = [
    {
        "name": "Low Pressure Area",
        "short": "LPA",
        "min_wind_kmph": 0,
        "max_wind_kmph": 31,
        "color": "#38bdf8",
        "severity": "Informational"
    },
    {
        "name": "Depression",
        "short": "D",
        "min_wind_kmph": 31,
        "max_wind_kmph": 49,
        "color": "#34d399",
        "severity": "Low"
    },
    {
        "name": "Deep Depression",
        "short": "DD",
        "min_wind_kmph": 50,
        "max_wind_kmph": 61,
        "color": "#facc15",
        "severity": "Moderate"
    },
    {
        "name": "Cyclonic Storm",
        "short": "CS",
        "min_wind_kmph": 62,
        "max_wind_kmph": 88,
        "color": "#fb923c",
        "severity": "High"
    },
    {
        "name": "Severe Cyclonic Storm",
        "short": "SCS",
        "min_wind_kmph": 89,
        "max_wind_kmph": 117,
        "color": "#f97316",
        "severity": "Severe"
    },
    {
        "name": "Very Severe Cyclonic Storm",
        "short": "VSCS",
        "min_wind_kmph": 118,
        "max_wind_kmph": 166,
        "color": "#ef4444",
        "severity": "Very Severe"
    },
    {
        "name": "Extremely Severe Cyclonic Storm",
        "short": "ESCS",
        "min_wind_kmph": 167,
        "max_wind_kmph": 221,
        "color": "#dc2626",
        "severity": "Extremely Severe"
    },
    {
        "name": "Super Cyclonic Storm",
        "short": "SuCS",
        "min_wind_kmph": 222,
        "max_wind_kmph": 350,
        "color": "#991b1b",
        "severity": "Catastrophic"
    }
]

def get_category_from_wind(wind_kmph: float) -> Dict[str, Any]:
    for cat in reversed(CYCLONE_CATEGORIES):
        if wind_kmph >= cat["min_wind_kmph"]:
            return cat
    return CYCLONE_CATEGORIES[0]

DISCLAIMER_TEXT = (
    "Research prototype for cyclone analysis. "
    "Forecast outputs must not replace official meteorological warnings."
)

EXPLAINABILITY_CAPTION = (
    "AI Attention Region — areas highlighted by the model as important for cyclone identification."
)
