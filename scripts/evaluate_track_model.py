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
    
    print(f"Mean Geographic Error:    {tm['mean_geographic_error_km']} km")
    print(f"Held-out cyclones:        {tm['test_storms']}")
    print("-" * 60)
    for hour in [6, 12, 24, 36, 48]:
        item = tm["horizons"][str(hour)]
        print(f"  +{hour:>2} Hour Mean Error:    {item['mean_error_km']} km (67% radius {item['p67_error_km']} km)")
    print("=" * 60)

if __name__ == "__main__":
    main()
