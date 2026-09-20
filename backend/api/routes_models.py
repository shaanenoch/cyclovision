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
    Refreshes metrics from the latest trained artifacts. Training itself is a
    CLI/offline job because it can take minutes and must use an explicit dataset.
    """
    updated_metrics = evaluator.run_evaluation()
    return {
        "status": "success",
        "message": "Metrics refreshed from the latest trained model artifacts.",
        "metrics": updated_metrics
    }
