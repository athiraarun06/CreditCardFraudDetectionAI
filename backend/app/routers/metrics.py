import os
import json
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.schemas.schemas import ModelMetricsResponse

router = APIRouter(tags=["metrics"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
METRICS_PATH = os.path.join(PROJECT_ROOT, "saved_models", "metrics.json")


@router.get("/metrics", response_model=ModelMetricsResponse)
def get_metrics(current_user=Depends(get_current_user)):
    if not os.path.exists(METRICS_PATH):
        raise HTTPException(status_code=404, detail="No trained model metrics available yet. Run training first.")
    with open(METRICS_PATH) as f:
        data = json.load(f)
    return ModelMetricsResponse(best_model=data["best_model"], results=data["results"])
