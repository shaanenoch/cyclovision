"""Train the CycloVision track forecaster on NOAA IBTrACS observations.

The validation split is made by cyclone SID, preventing observations from the
same storm from leaking into both training and testing.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import GroupShuffleSplit

from backend.config import DEMO_DATA_DIR, MODELS_DIR
from preprocessing.track_preprocessing import calculate_haversine_distance_km

HORIZONS = [6, 12, 24, 36, 48]
FEATURE_NAMES = [
    "latitude", "longitude", "wind_kmph", "pressure_hpa",
    "bearing_sin", "bearing_cos", "translation_speed_kmph",
    "month_sin", "month_cos",
]
IBTRACS_URL = (
    "https://www.ncei.noaa.gov/data/international-best-track-archive-for-"
    "climate-stewardship-ibtracs/v04r01/access/csv/"
    "ibtracs.NI.list.v04r01.csv"
)


def _numeric(frame: pd.DataFrame, names: list[str]) -> pd.Series:
    result = pd.Series(np.nan, index=frame.index, dtype=float)
    for name in names:
        if name in frame:
            result = result.fillna(pd.to_numeric(frame[name], errors="coerce"))
    return result


def load_ibtracs(path: Path, min_season: int = 1980) -> pd.DataFrame:
    df = pd.read_csv(path, skiprows=[1], low_memory=False)
    df = df[pd.to_numeric(df["SEASON"], errors="coerce") >= min_season].copy()
    df["time"] = pd.to_datetime(df["ISO_TIME"], errors="coerce", utc=True)
    df["lat"] = _numeric(df, ["NEWDELHI_LAT", "LAT", "USA_LAT"])
    df["lon"] = _numeric(df, ["NEWDELHI_LON", "LON", "USA_LON"])
    df["wind_kmph"] = _numeric(df, ["NEWDELHI_WIND", "WMO_WIND", "USA_WIND"]) * 1.852
    df["pressure_hpa"] = _numeric(df, ["NEWDELHI_PRES", "WMO_PRES", "USA_PRES"])
    df["speed_kmph"] = _numeric(df, ["STORM_SPEED"]) * 1.852
    df["bearing_deg"] = _numeric(df, ["STORM_DIR"])
    df = df.dropna(subset=["SID", "time", "lat", "lon"]).sort_values(["SID", "time"])
    for col in ["wind_kmph", "pressure_hpa", "speed_kmph", "bearing_deg"]:
        df[col] = df.groupby("SID")[col].transform(
            lambda s: s.interpolate(limit=4, limit_direction="both")
        )
    df["wind_kmph"] = df["wind_kmph"].fillna(65.0)
    df["pressure_hpa"] = df["pressure_hpa"].fillna(1010.0 - 0.42 * df["wind_kmph"])
    df["speed_kmph"] = df["speed_kmph"].fillna(15.0).clip(1.0, 70.0)
    df["bearing_deg"] = df["bearing_deg"].fillna(315.0) % 360.0
    return df


def build_supervised_samples(df: pd.DataFrame):
    features, targets, groups = [], [], []
    for sid, storm in df.groupby("SID", sort=False):
        storm = storm.drop_duplicates("time").set_index("time").sort_index()
        by_time = {timestamp: row for timestamp, row in storm.iterrows()}
        for timestamp, row in storm.iterrows():
            future_rows = [by_time.get(timestamp + pd.Timedelta(hours=h)) for h in HORIZONS]
            if any(future is None for future in future_rows):
                continue
            bearing_rad = math.radians(float(row["bearing_deg"]))
            month_angle = 2.0 * math.pi * (timestamp.month - 1) / 12.0
            features.append([
                float(row["lat"]), float(row["lon"]), float(row["wind_kmph"]),
                float(row["pressure_hpa"]), math.sin(bearing_rad), math.cos(bearing_rad),
                float(row["speed_kmph"]), math.sin(month_angle), math.cos(month_angle),
            ])
            target = []
            for future in future_rows:
                target.extend([
                    float(future["lat"] - row["lat"]),
                    float(future["lon"] - row["lon"]),
                    float(future["wind_kmph"]),
                    float(future["pressure_hpa"]),
                ])
            targets.append(target)
            groups.append(str(sid))
    return np.asarray(features), np.asarray(targets), np.asarray(groups)


def evaluate(model, x_test, y_test):
    pred = model.predict(x_test)
    per_horizon, all_errors = {}, []
    for index, horizon in enumerate(HORIZONS):
        offset = index * 4
        true_lat, true_lon = x_test[:, 0] + y_test[:, offset], x_test[:, 1] + y_test[:, offset + 1]
        pred_lat, pred_lon = x_test[:, 0] + pred[:, offset], x_test[:, 1] + pred[:, offset + 1]
        errors = np.asarray([
            calculate_haversine_distance_km(a, b, c, d)
            for a, b, c, d in zip(true_lat, true_lon, pred_lat, pred_lon)
        ])
        all_errors.extend(errors.tolist())
        per_horizon[str(horizon)] = {
            "mean_error_km": round(float(np.mean(errors)), 2),
            "median_error_km": round(float(np.median(errors)), 2),
            "p67_error_km": round(float(np.percentile(errors, 67)), 2),
            "p90_error_km": round(float(np.percentile(errors, 90)), 2),
            "wind_mae_kmph": round(float(np.mean(np.abs(y_test[:, offset + 2] - pred[:, offset + 2]))), 2),
            "pressure_mae_hpa": round(float(np.mean(np.abs(y_test[:, offset + 3] - pred[:, offset + 3]))), 2),
        }
    return {
        "test_samples": int(len(x_test)),
        "mean_geographic_error_km": round(float(np.mean(all_errors)), 2),
        "horizons": per_horizon,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True, help="IBTrACS North Indian Ocean CSV")
    parser.add_argument("--trees", type=int, default=180)
    parser.add_argument("--output", type=Path, default=MODELS_DIR / "prediction" / "track_predictor_v2.joblib")
    args = parser.parse_args()

    observations = load_ibtracs(args.data)
    x, y, groups = build_supervised_samples(observations)
    if len(x) < 500:
        raise RuntimeError(f"Only {len(x)} complete samples found; at least 500 are required")
    train_idx, test_idx = next(GroupShuffleSplit(
        n_splits=1, test_size=0.20, random_state=42
    ).split(x, y, groups))
    model = ExtraTreesRegressor(
        n_estimators=args.trees, min_samples_leaf=2, max_features=0.9,
        n_jobs=-1, random_state=42,
    )
    model.fit(x[train_idx], y[train_idx])
    evaluation = evaluate(model, x[test_idx], y[test_idx])
    metadata = {
        "model_name": "IBTrACS ExtraTrees Multi-Horizon Forecaster",
        "model_version": "track-v2.0",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "data_source": "NOAA IBTrACS v04r01 North Indian Ocean",
        "data_url": IBTRACS_URL,
        "observations": int(len(observations)),
        "storms": int(observations["SID"].nunique()),
        "training_samples": int(len(train_idx)),
        "test_storms": int(len(set(groups[test_idx]))),
        "split_method": "GroupShuffleSplit by cyclone SID (80/20)",
        "evaluation": evaluation,
    }
    artifact = {"model": model, "horizons": HORIZONS,
                "feature_names": FEATURE_NAMES, "metadata": metadata}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, args.output, compress=3)
    (DEMO_DATA_DIR / "track_metrics.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(json.dumps({"artifact": str(args.output), **metadata}, indent=2))


if __name__ == "__main__":
    main()
