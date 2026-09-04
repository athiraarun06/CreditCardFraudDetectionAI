import os
import json
from datetime import datetime
from fastapi import APIRouter

router = APIRouter(tags=["meta"])

from app.core.paths import SAVED_MODELS_DIR
META_PATH = os.path.join(SAVED_MODELS_DIR, "model_meta.json")
METRICS_PATH = os.path.join(SAVED_MODELS_DIR, "metrics.json")


@router.get("/version")
def get_version():
    return {
        "app": "Credit Card Fraud Detection AI System",
        "version": "1.1.0",
        "api_time": datetime.utcnow().isoformat(),
    }


@router.get("/model-info")
def get_model_info():
    if not os.path.exists(META_PATH):
        return {"trained": False, "message": "No model has been trained yet. Run `python -m app.ml.train`."}

    with open(META_PATH) as f:
        meta = json.load(f)

    best_metrics = None
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH) as f:
            metrics_data = json.load(f)
        best_metrics = metrics_data.get("results", {}).get(metrics_data.get("best_model"))

    model_path = os.path.join(SAVED_MODELS_DIR, "best_model.pkl")
    trained_at = None
    if os.path.exists(model_path):
        trained_at = datetime.fromtimestamp(os.path.getmtime(model_path)).isoformat()

    return {
        "trained": True,
        "model_name": meta.get("model_name"),
        "categorical_features": meta.get("categorical_cols"),
        "numeric_features": meta.get("numeric_cols"),
        "trained_at": trained_at,
        "metrics": best_metrics,
    }
