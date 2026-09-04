from fastapi import APIRouter, Depends, BackgroundTasks

from app.core.security import get_current_user
from app.ml.train import main as train_main

router = APIRouter(tags=["retrain"])


@router.post("/retrain")
def retrain(background_tasks: BackgroundTasks, current_user=Depends(get_current_user)):
    background_tasks.add_task(train_main)
    return {"status": "retraining_started", "message": "Model retraining has been scheduled in the background."}
