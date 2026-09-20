import re
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.database.db import get_db_connection
from preprocessing.track_preprocessing import calculate_haversine_distance_km

router = APIRouter()

# Meteorological reference points in the North Indian Ocean & coastal regions
KNOWN_GEO_POINTS = {
    "bay of bengal": {"name": "Bay of Bengal Basin", "lat": 15.0, "lon": 87.0, "type": "Basin"},
    "odisha": {"name": "Odisha Coast, India", "lat": 19.8, "lon": 85.8, "type": "Coastal State"},
    "puri": {"name": "Puri, Odisha", "lat": 19.81, "lon": 85.83, "type": "Coastal City"},
    "paradip": {"name": "Paradip Port, Odisha", "lat": 20.31, "lon": 86.61, "type": "Port"},
    "visakhapatnam": {"name": "Visakhapatnam, Andhra Pradesh", "lat": 17.68, "lon": 83.21, "type": "Major Port / City"},
    "vizag": {"name": "Visakhapatnam, Andhra Pradesh", "lat": 17.68, "lon": 83.21, "type": "Major Port / City"},
    "chennai": {"name": "Chennai, Tamil Nadu", "lat": 13.08, "lon": 80.27, "type": "Coastal City"},
    "andhra pradesh": {"name": "Andhra Pradesh Coast", "lat": 16.5, "lon": 81.5, "type": "Coastal State"},
    "kolkata": {"name": "Kolkata, West Bengal", "lat": 22.57, "lon": 88.36, "type": "Coastal Megacity"},
    "bhubaneswar": {"name": "Bhubaneswar, Odisha", "lat": 20.29, "lon": 85.82, "type": "Capital City"},
    "arabian sea": {"name": "Arabian Sea Basin", "lat": 16.0, "lon": 67.0, "type": "Basin"},
    "gopalpur": {"name": "Gopalpur Port, Odisha", "lat": 19.26, "lon": 84.91, "type": "Port"}
}

@router.get("/cyclones")
def get_all_cyclones():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cyclones")
    cyclones = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return cyclones

@router.get("/cyclones/{cyclone_id}")
def get_cyclone_details(cyclone_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cyclones WHERE id = ?", (cyclone_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Cyclone {cyclone_id} not found")
        
    cyclone = dict(row)
    
    # Fetch track points
    cursor.execute("""
    SELECT * FROM track_points 
    WHERE cyclone_id = ? 
    ORDER BY forecast_hour ASC, id ASC
    """, (cyclone_id,))
    track_points = [dict(r) for r in cursor.fetchall()]
    conn.close()

    cyclone["track_points"] = track_points
    return cyclone

@router.get("/search")
def search_cyclone_or_location(q: str = Query(..., min_length=1)):
    """
    Unified search supporting:
    - Cyclone Name (e.g. 'Demo Cyclone 01')
    - Geographic Regions / Coastal Cities (e.g. 'Bay of Bengal', 'Odisha', 'Visakhapatnam', 'Chennai')
    - Coordinates (e.g. '15.2, 84.7')
    """
    query = q.strip().lower()
    results = []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cyclones WHERE is_active = 1 LIMIT 1")
    active_cyclone_row = cursor.fetchone()
    active_cyclone = dict(active_cyclone_row) if active_cyclone_row else None
    conn.close()

    # 1. Coordinate search (e.g. "15.2, 84.7" or "15.2 84.7")
    coord_match = re.match(r'^([-+]?\d*\.?\d+)[,\s]+([-+]?\d*\.?\d+)$', query)
    if coord_match:
        lat = float(coord_match.group(1))
        lon = float(coord_match.group(2))
        dist_str = "Distance to active system: N/A"
        if active_cyclone:
            d_km = calculate_haversine_distance_km(lat, lon, active_cyclone["current_lat"], active_cyclone["current_lon"])
            dist_str = f"Approx. {round(d_km, 1)} km from {active_cyclone['name']}"
            
        results.append({
            "type": "coordinate",
            "title": f"Coordinates: {lat}°N, {lon}°E",
            "subtitle": dist_str,
            "lat": lat,
            "lon": lon,
            "related_cyclone": active_cyclone,
            "estimated_path_note": f"Estimated track of {active_cyclone['name']}: {active_cyclone['estimated_trajectory_summary']}" if active_cyclone else None
        })

    # 2. Known location matches
    for key, info in KNOWN_GEO_POINTS.items():
        if query in key or key in query:
            dist_str = ""
            if active_cyclone:
                d_km = calculate_haversine_distance_km(info["lat"], info["lon"], active_cyclone["current_lat"], active_cyclone["current_lon"])
                dist_str = f"{round(d_km, 1)} km from {active_cyclone['name']}"

            results.append({
                "type": "location",
                "title": info["name"],
                "subtitle": f"{info['type']} • {dist_str}",
                "lat": info["lat"],
                "lon": info["lon"],
                "related_cyclone": active_cyclone,
                "estimated_path_note": (
                    f"Estimated path for {active_cyclone['name']}: moving {active_cyclone['movement_direction']}. "
                    f"Expected track towards coastal areas — not an official landfall alert."
                ) if active_cyclone else None
            })

    # 3. Cyclone name search
    if active_cyclone and (query in active_cyclone["name"].lower() or query in "cyclone"):
        results.append({
            "type": "cyclone",
            "title": active_cyclone["name"],
            "subtitle": f"{active_cyclone['status']} • Current: {active_cyclone['current_lat']}°N, {active_cyclone['current_lon']}°E",
            "lat": active_cyclone["current_lat"],
            "lon": active_cyclone["current_lon"],
            "related_cyclone": active_cyclone,
            "estimated_path_note": active_cyclone["estimated_trajectory_summary"]
        })

    # Default fallback if nothing specific matched
    if not results and active_cyclone:
        results.append({
            "type": "info",
            "title": f"Query: '{q}'",
            "subtitle": f"Showing nearest active system: {active_cyclone['name']}",
            "lat": active_cyclone["current_lat"],
            "lon": active_cyclone["current_lon"],
            "related_cyclone": active_cyclone,
            "estimated_path_note": active_cyclone["estimated_trajectory_summary"]
        })

    return results
