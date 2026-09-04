"""
Trains directly on the real Kaggle "Credit Card Fraud Detection" dataset
(Time, V1..V28, Amount -> Class). See data/README_KAGGLE.md for how to obtain it.

This is a standalone benchmark pipeline, separate from app.ml.train (which powers the
interactive /predict endpoint using business-schema features the frontend form collects).
"""
import os
import sys
import json
import joblib
import pandas as pd
import mlflow

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
)
from imblearn.over_sampling import SMOTE

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except Exception:
    HAS_XGB = False

try:
    from lightgbm import LGBMClassifier
    HAS_LGBM = True
except Exception:
    HAS_LGBM = False

from app.ml.plots import generate_all_plots

from app.core.paths import PROJECT_ROOT, SAVED_MODELS_DIR, DATA_DIR
DATA_PATH = os.path.join(DATA_DIR, "creditcard.csv")
MLRUNS_DIR = os.path.join(PROJECT_ROOT, "mlruns")


def get_models():
    models = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "decision_tree": DecisionTreeClassifier(max_depth=10, class_weight="balanced", random_state=42),
        "random_forest": RandomForestClassifier(n_estimators=200, max_depth=12, class_weight="balanced", random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingClassifier(n_estimators=150, max_depth=3, random_state=42),
    }
    if HAS_XGB:
        models["xgboost"] = XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.1, eval_metric="logloss",
            random_state=42, n_jobs=-1,
        )
    if HAS_LGBM:
        models["lightgbm"] = LGBMClassifier(n_estimators=300, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1, verbosity=-1)
    return models


def evaluate(y_true, y_pred, y_proba):
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }


def main():
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: {DATA_PATH} not found.")
        print("Download the Kaggle dataset first — see data/README_KAGGLE.md")
        sys.exit(1)

    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    mlflow.set_tracking_uri(f"file:{MLRUNS_DIR}")
    mlflow.set_experiment("credit_card_fraud_detection_kaggle")

    df = pd.read_csv(DATA_PATH)
    df = df.dropna()
    feature_cols = [c for c in df.columns if c != "Class"]

    X = df[feature_cols]
    y = df["Class"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_t = scaler.fit_transform(X_train)
    X_test_t = scaler.transform(X_test)

    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train_t, y_train)

    results = {}
    fitted_models = {}
    for name, model in get_models().items():
        with mlflow.start_run(run_name=f"kaggle_{name}"):
            model.fit(X_train_res, y_train_res)
            y_pred = model.predict(X_test_t)
            y_proba = model.predict_proba(X_test_t)[:, 1]
            metrics = evaluate(y_test, y_pred, y_proba)
            mlflow.log_params(model.get_params())
            mlflow.log_metrics({k: v for k, v in metrics.items() if k != "confusion_matrix"})
            results[name] = metrics
            fitted_models[name] = model
            print(f"{name}: ROC-AUC={metrics['roc_auc']:.4f} F1={metrics['f1']:.4f} Recall={metrics['recall']:.4f}")

    best_name = max(results, key=lambda n: results[n]["roc_auc"])
    best_model = fitted_models[best_name]
    print(f"\nBest model (Kaggle data): {best_name} (ROC-AUC={results[best_name]['roc_auc']:.4f})")

    y_pred_best = best_model.predict(X_test_t)
    y_proba_best = best_model.predict_proba(X_test_t)[:, 1]
    plots_dir = os.path.join(SAVED_MODELS_DIR, "kaggle_plots")
    generate_all_plots(y_test, y_pred_best, y_proba_best, plots_dir)

    joblib.dump(best_model, os.path.join(SAVED_MODELS_DIR, "kaggle_best_model.pkl"))
    joblib.dump(scaler, os.path.join(SAVED_MODELS_DIR, "kaggle_scaler.pkl"))
    with open(os.path.join(SAVED_MODELS_DIR, "kaggle_metrics.json"), "w") as f:
        json.dump({"best_model": best_name, "feature_cols": feature_cols, "results": results}, f, indent=2)

    print("Saved Kaggle-trained model artifacts to", SAVED_MODELS_DIR)


if __name__ == "__main__":
    main()
