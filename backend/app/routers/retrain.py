from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException

from app.core.security import get_current_user

router = APIRouter(tags=["retrain"])


def _run_training():
    from app.ml.train import main as train_main  # lazy: training deps (mlflow, xgboost,
    train_main()                                  # lightgbm) aren't installed in slim/serverless deploys


@router.post("/retrain")
def retrain(background_tasks: BackgroundTasks, current_user=Depends(get_current_user)):
    try:
        import mlflow  # noqa: F401
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Retraining is unavailable in this deployment (training dependencies are not "
                   "installed). Run `python -m app.ml.train` locally instead.",
        )
    background_tasks.add_task(_run_training)
    return {"status": "retraining_started", "message": "Model retraining has been scheduled in the background."}
