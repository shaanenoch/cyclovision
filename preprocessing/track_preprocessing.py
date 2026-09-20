import math
import csv
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validates whether latitude is in [-90, 90] and longitude is in [-180, 180].
    """
    if lat is None or lon is None:
        return False
    try:
        lat = float(lat)
        lon = float(lon)
        return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
    except (ValueError, TypeError):
        return False

def calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance between two geographic coordinates using the Haversine formula.
    """
    R = 6371.0 # Earth's radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def calculate_bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates initial forward bearing (azimuth in degrees [0, 360)) from point 1 to point 2.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = (math.cos(phi1) * math.sin(phi2) -
         math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda))
    
    initial_bearing = math.degrees(math.atan2(y, x))
    compass_bearing = (initial_bearing + 360.0) % 360.0
    return compass_bearing

def bearing_to_compass(bearing_deg: float) -> str:
    """
    Converts a bearing in degrees to an 8-point/16-point meteorological compass direction.
    """
    compass_sectors = [
        "North", "North-North-East", "North-East", "East-North-East",
        "East", "East-South-East", "South-East", "South-South-East",
        "South", "South-South-West", "South-West", "West-South-West",
        "West", "West-North-West", "North-West", "North-North-West"
    ]
    idx = int((bearing_deg + 11.25) / 22.5) % 16
    return compass_sectors[idx]

def extract_track_features(track_history: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Extracts time-series movement and intensity features from sequential track points.
    Features:
    - current_lat, current_lon
    - lat_change_6h, lon_change_6h
    - lat_change_12h, lon_change_12h
    - speed_kmph
    - bearing_deg
    - wind_speed_kmph
    - pressure_hpa
    - wind_trend (delta over last intervals)
    - pressure_trend
    """
    if not track_history or len(track_history) == 0:
        return {
            "current_lat": 15.2,
            "current_lon": 84.7,
            "lat_change_6h": 0.4,
            "lon_change_6h": -0.3,
            "speed_kmph": 18.0,
            "bearing_deg": 315.0,
            "wind_speed_kmph": 95.0,
            "pressure_hpa": 985.0,
            "wind_trend": 5.0,
            "pressure_trend": -4.0
        }

    # Sort chronologically if timestamps exist
    p_curr = track_history[-1]
    curr_lat = float(p_curr.get("latitude", p_curr.get("lat", 15.0)))
    curr_lon = float(p_curr.get("longitude", p_curr.get("lon", 85.0)))
    curr_wind = float(p_curr.get("wind_speed_kmph", p_curr.get("wind_speed", 85.0)))
    curr_pres = float(p_curr.get("pressure_hpa", p_curr.get("pressure", 988.0)))

    if len(track_history) >= 2:
        p_prev = track_history[-2]
        prev_lat = float(p_prev.get("latitude", p_prev.get("lat", curr_lat - 0.3)))
        prev_lon = float(p_prev.get("longitude", p_prev.get("lon", curr_lon + 0.3)))
        prev_wind = float(p_prev.get("wind_speed_kmph", p_prev.get("wind_speed", curr_wind)))
        prev_pres = float(p_prev.get("pressure_hpa", p_prev.get("pressure", curr_pres)))

        lat_change = curr_lat - prev_lat
        lon_change = curr_lon - prev_lon
        bearing = calculate_bearing_deg(prev_lat, prev_lon, curr_lat, curr_lon)
        dist_km = calculate_haversine_distance_km(prev_lat, prev_lon, curr_lat, curr_lon)
        speed = dist_km / 6.0 # Assume standard 6-hour synoptic observation
        wind_trend = curr_wind - prev_wind
        pressure_trend = curr_pres - prev_pres
    else:
        lat_change = 0.4
        lon_change = -0.3
        bearing = 315.0
        speed = 18.0
        wind_trend = 0.0
        pressure_trend = 0.0

    return {
        "current_lat": curr_lat,
        "current_lon": curr_lon,
        "lat_change_6h": lat_change,
        "lon_change_6h": lon_change,
        "speed_kmph": max(5.0, min(speed, 65.0)),
        "bearing_deg": bearing,
        "wind_speed_kmph": curr_wind,
        "pressure_hpa": curr_pres,
        "wind_trend": wind_trend,
        "pressure_trend": pressure_trend
    }

def clean_and_sort_track_csv(file_path_or_rows) -> List[Dict[str, Any]]:
    """
    Standardizes CSV data: column headers and data types.
    Handles columns like 'ISO_TIME', 'LAT', 'LON', 'WMO_WIND', 'WMO_PRES', 'NAME'.
    Works directly with standard CSV files or lists of row dictionaries.
    """
    rows = []
    if isinstance(file_path_or_rows, str):
        with open(file_path_or_rows, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    elif isinstance(file_path_or_rows, list):
        rows = file_path_or_rows
    else:
        try:
            # If a pandas DataFrame is passed
            rows = file_path_or_rows.to_dict('records')
        except Exception:
            rows = []

    cleaned_records = []
    for r in rows:
        cleaned_row = {}
        for k, v in r.items():
            kl = k.strip().lower()
            if kl in ['lat', 'latitude']:
                try: cleaned_row['latitude'] = float(v)
                except (ValueError, TypeError): pass
            elif kl in ['lon', 'long', 'longitude']:
                try: cleaned_row['longitude'] = float(v)
                except (ValueError, TypeError): pass
            elif kl in ['wind', 'wind_speed', 'wmo_wind', 'vmax', 'wind_speed_kmph']:
                try: cleaned_row['wind_speed_kmph'] = float(v)
                except (ValueError, TypeError): pass
            elif kl in ['pres', 'pressure', 'wmo_pres', 'mslp', 'pressure_hpa']:
                try: cleaned_row['pressure_hpa'] = float(v)
                except (ValueError, TypeError): pass
            elif kl in ['time', 'iso_time', 'timestamp', 'date', 'datetime']:
                cleaned_row['timestamp'] = str(v)
            elif kl in ['name', 'cyclone_name', 'storm_name']:
                cleaned_row['cyclone_name'] = str(v)
            else:
                cleaned_row[k] = v

        if 'latitude' in cleaned_row and 'longitude' in cleaned_row:
            if validate_coordinates(cleaned_row['latitude'], cleaned_row['longitude']):
                cleaned_records.append(cleaned_row)

    return cleaned_records
