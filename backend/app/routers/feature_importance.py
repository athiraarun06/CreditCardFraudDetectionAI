import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.schemas.schemas import FeatureImportanceItem
from app.ml.explain import get_feature_importance

router = APIRouter(tags=["explainability"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
SHAP_DIR = os.path.join(PROJECT_ROOT, "saved_models", "shap")
PLOTS_DIR = os.path.join(PROJECT_ROOT, "saved_models", "plots")


@router.get("/feature-importance", response_model=List[FeatureImportanceItem])
def feature_importance(current_user=Depends(get_current_user)):
    try:
        return get_feature_importance()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not trained yet. Run `python -m app.ml.train`.")


@router.get("/explainability")
def explainability(current_user=Depends(get_current_user)):
    try:
        importance = get_feature_importance()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not trained yet. Run `python -m app.ml.train`.")

    def asset(dir_path, filename, url_prefix):
        return f"{url_prefix}/{filename}" if os.path.exists(os.path.join(dir_path, filename)) else None

    explanations = []
    for item in importance[:5]:
        explanations.append({
            "feature": item["feature"],
            "importance": item["importance"],
            "explanation": (
                f"'{item['feature']}' is one of the strongest signals the model uses. "
                f"Transactions with unusual values on this feature are significantly more "
                f"likely to be flagged as fraudulent."
            ),
        })

    return {
        "top_features": importance,
        "explanations": explanations,
        "images": {
            "shap_summary": asset(SHAP_DIR, "summary_plot.png", "/static/models/shap"),
            "shap_feature_importance": asset(SHAP_DIR, "feature_importance.png", "/static/models/shap"),
            "shap_waterfall": asset(SHAP_DIR, "waterfall_plot.png", "/static/models/shap"),
            "confusion_matrix": asset(PLOTS_DIR, "confusion_matrix.png", "/static/models/plots"),
            "roc_curve": asset(PLOTS_DIR, "roc_curve.png", "/static/models/plots"),
            "pr_curve": asset(PLOTS_DIR, "pr_curve.png", "/static/models/plots"),
            "calibration_curve": asset(PLOTS_DIR, "calibration_curve.png", "/static/models/plots"),
            "lift_curve": asset(PLOTS_DIR, "lift_curve.png", "/static/models/plots"),
        },
    }
