import sqlite3
import json
from pathlib import Path
from backend.config import BASE_DIR

DB_PATH = BASE_DIR / "cyclone_ai.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table: Cyclones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cyclones (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        status TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        basin TEXT NOT NULL,
        current_lat REAL NOT NULL,
        current_lon REAL NOT NULL,
        wind_speed_kmph REAL NOT NULL,
        pressure_hpa REAL NOT NULL,
        movement_direction TEXT NOT NULL,
        movement_speed_kmph REAL NOT NULL,
        nearest_coastal_point TEXT,
        estimated_trajectory_summary TEXT,
        is_demo INTEGER DEFAULT 1,
        satellite_image_url TEXT,
        heatmap_url TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table: Track Points (historical and forecast)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS track_points (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cyclone_id TEXT NOT NULL,
        point_type TEXT NOT NULL, -- 'historical', 'current', 'forecast'
        forecast_hour INTEGER DEFAULT 0,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        wind_speed_kmph REAL NOT NULL,
        pressure_hpa REAL NOT NULL,
        classification TEXT,
        timestamp_str TEXT,
        FOREIGN KEY (cyclone_id) REFERENCES cyclones (id)
    );
    """)

    # Table: Datasets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS datasets (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT NOT NULL,
        purpose TEXT NOT NULL,
        records_count INTEGER NOT NULL,
        file_size_kb REAL NOT NULL,
        columns_json TEXT NOT NULL,
        date_uploaded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL
    );
    """)

    # Table: Model Metrics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        model_version TEXT NOT NULL,
        training_date TEXT NOT NULL,
        dataset_size INTEGER NOT NULL,
        training_accuracy REAL NOT NULL,
        validation_accuracy REAL NOT NULL,
        precision REAL NOT NULL,
        recall REAL REAL NOT NULL,
        f1_score REAL NOT NULL,
        metrics_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
