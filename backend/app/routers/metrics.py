import os
import json
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.schemas.schemas import ModelMetricsResponse

router = APIRouter(tags=["metrics"])

from app.core.paths import SAVED_MODELS_DIR
METRICS_PATH = os.path.join(SAVED_MODELS_DIR, "metrics.json")


@router.get("/metrics", response_model=ModelMetricsResponse)
def get_metrics(current_user=Depends(get_current_user)):
    if not os.path.exists(METRICS_PATH):
        raise HTTPException(status_code=404, detail="No trained model metrics available yet. Run training first.")
    with open(METRICS_PATH) as f:
        data = json.load(f)
    return ModelMetricsResponse(best_model=data["best_model"], results=data["results"])
