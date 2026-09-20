from fastapi import APIRouter
from ml.evaluation.evaluator import ModelEvaluator

router = APIRouter()
evaluator = ModelEvaluator()

@router.get("/model/metrics")
def get_model_evaluation_metrics():
    """
    Returns authentic validation metrics, confusion matrix, loss/acc curves,
    and geodesic track prediction errors evaluated against real validation data.
    """
    metrics = evaluator.load_metrics()
    return metrics

@router.post("/model/train")
def trigger_model_training():
    """
    Re-trains/re-evaluates models and updates evaluation metrics records.
    """
    updated_metrics = evaluator.run_evaluation()
    return {
        "status": "success",
        "message": "Model training & validation evaluation completed.",
        "metrics": updated_metrics
    }
