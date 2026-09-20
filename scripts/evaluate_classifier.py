"""
CycloneAI - Classifier Evaluation Script
Evaluates intensity classification accuracy, precision, recall, F1, and confusion matrix.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.evaluation.evaluator import ModelEvaluator

def main():
    print("=" * 60)
    print("CycloneAI: Satellite Classifier Evaluation Report")
    print("=" * 60)
    evaluator = ModelEvaluator()
    metrics = evaluator.run_evaluation()
    
    print(f"Model Name:           {metrics['model_name']}")
    print(f"Model Version:        {metrics['model_version']}")
    print(f"Dataset Size:         {metrics['dataset_size']} observations")
    print(f"Training Accuracy:    {metrics['training_accuracy'] * 100:.2f}%")
    print(f"Validation Accuracy:  {metrics['validation_accuracy'] * 100:.2f}%")
    print(f"Weighted Precision:   {metrics['precision']:.4f}")
    print(f"Weighted Recall:      {metrics['recall']:.4f}")
    print(f"F1-Score:             {metrics['f1_score']:.4f}")
    print("\nConfusion Matrix:")
    print("Labels:", metrics["confusion_matrix"]["labels"])
    for row in metrics["confusion_matrix"]["matrix"]:
        print(" ", row)
    print("=" * 60)

if __name__ == "__main__":
    main()
