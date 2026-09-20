"""
CycloneAI - Track Model Evaluation Script
Computes MAE, RMSE, and Geodesic Distance Error in km for 6h to 48h forecasts.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.evaluation.evaluator import ModelEvaluator

def main():
    print("=" * 60)
    print("CycloneAI: Track Prediction Model Geodesic Error Report")
    print("=" * 60)
    evaluator = ModelEvaluator()
    metrics = evaluator.run_evaluation()
    tm = metrics["track_prediction_metrics"]
    
    print(f"Latitude MAE:             {tm['mae_lat_deg']}°")
    print(f"Longitude MAE:            {tm['mae_lon_deg']}°")
    print(f"Latitude RMSE:            {tm['rmse_lat_deg']}°")
    print(f"Longitude RMSE:           {tm['rmse_lon_deg']}°")
    print(f"Mean Geographic Error:    {tm['mean_geographic_error_km']} km")
    print("-" * 60)
    print(f"  +6 Hour Error:          {tm['error_6h_km']} km")
    print(f"  +12 Hour Error:         {tm['error_12h_km']} km")
    print(f"  +24 Hour Error:         {tm['error_24h_km']} km")
    print(f"  +36 Hour Error:         {tm['error_36h_km']} km")
    print(f"  +48 Hour Error:         {tm['error_48h_km']} km")
    print("=" * 60)

if __name__ == "__main__":
    main()
