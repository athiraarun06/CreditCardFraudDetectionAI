import os
import json
import joblib
import numpy as np
import pandas as pd
import mlflow

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, classification_report,
    matthews_corrcoef, precision_recall_curve,
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

from app.ml.features import engineer_features, CATEGORICAL_COLS, NUMERIC_COLS
from app.ml.plots import generate_all_plots, save_calibration_curve, save_lift_curve

# Business cost assumptions used for threshold tuning: a missed fraud (false negative) costs far
# more than a false-positive manual review, so the optimal threshold skews toward higher recall.
COST_FALSE_NEGATIVE = 25  # cost of letting a fraud through
COST_FALSE_POSITIVE = 1   # cost of a manual review on a legitimate transaction

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "transactions.csv")
SAVED_MODELS_DIR = os.path.join(PROJECT_ROOT, "saved_models")
MLRUNS_DIR = os.path.join(PROJECT_ROOT, "mlruns")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset="transaction_id").copy()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["customer_age"] = pd.to_numeric(df["customer_age"], errors="coerce")
    df["previous_transactions"] = pd.to_numeric(df["previous_transactions"], errors="coerce")
    df["avg_transaction_amount"] = pd.to_numeric(df["avg_transaction_amount"], errors="coerce")

    for col in ["amount", "customer_age", "previous_transactions", "avg_transaction_amount"]:
        df[col] = df[col].fillna(df[col].median())
    for col in ["merchant_category", "location", "payment_method"]:
        df[col] = df[col].fillna(df[col].mode()[0])

    q_low, q_hi = df["amount"].quantile(0.001), df["amount"].quantile(0.999)
    df["amount"] = df["amount"].clip(q_low, q_hi)
    df["customer_age"] = df["customer_age"].clip(18, 90)
    df["fraud"] = df["fraud"].astype(int)
    return df


def build_preprocessor():
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLS),
            ("num", StandardScaler(), NUMERIC_COLS),
        ]
    )


def get_models():
    models = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "decision_tree": DecisionTreeClassifier(max_depth=8, class_weight="balanced", random_state=42),
        "random_forest": RandomForestClassifier(n_estimators=200, max_depth=10, class_weight="balanced", random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingClassifier(n_estimators=150, max_depth=3, random_state=42),
    }
    if HAS_XGB:
        models["xgboost"] = XGBClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.1, eval_metric="logloss",
            use_label_encoder=False, random_state=42, n_jobs=-1,
        )
    if HAS_LGBM:
        models["lightgbm"] = LGBMClassifier(n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42, n_jobs=-1, verbosity=-1)
    return models


def evaluate(y_true, y_pred, y_proba):
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }


def optimize_threshold_by_cost(y_true, y_proba):
    """Sweeps thresholds and picks the one minimizing business cost (FN >> FP)."""
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_proba)
    best_threshold, best_cost = 0.5, float("inf")
    for t in thresholds:
        y_pred = (y_proba >= t).astype(int)
        fn = int(((y_true == 1) & (y_pred == 0)).sum())
        fp = int(((y_true == 0) & (y_pred == 1)).sum())
        cost = fn * COST_FALSE_NEGATIVE + fp * COST_FALSE_POSITIVE
        if cost < best_cost:
            best_cost, best_threshold = cost, float(t)
    return best_threshold, best_cost


def main():
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    mlflow.set_tracking_uri(f"file:{MLRUNS_DIR}")
    mlflow.set_experiment("credit_card_fraud_detection")

    df = pd.read_csv(DATA_PATH)
    df = clean_data(df)
    df = engineer_features(df)

    X = df[CATEGORICAL_COLS + NUMERIC_COLS]
    y = df["fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocessor = build_preprocessor()
    X_train_t = preprocessor.fit_transform(X_train)
    X_test_t = preprocessor.transform(X_test)

    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train_t, y_train)

    results = {}
    fitted_models = {}
    models = get_models()

    for name, model in models.items():
        with mlflow.start_run(run_name=name):
            model.fit(X_train_res, y_train_res)
            y_pred = model.predict(X_test_t)
            y_proba = model.predict_proba(X_test_t)[:, 1]
            metrics = evaluate(y_test, y_pred, y_proba)
            mlflow.log_params(model.get_params())
            mlflow.log_metrics({k: v for k, v in metrics.items() if k != "confusion_matrix"})
            results[name] = metrics
            fitted_models[name] = model
            print(f"{name}: ROC-AUC={metrics['roc_auc']:.4f} F1={metrics['f1']:.4f}")

    comparison_rows = ["| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | MCC |",
                       "|---|---|---|---|---|---|---|---|"]
    for name, m in results.items():
        comparison_rows.append(
            f"| {name} | {m['accuracy']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | "
            f"{m['f1']:.4f} | {m['roc_auc']:.4f} | {m['pr_auc']:.4f} | {m['mcc']:.4f} |"
        )
    with open(os.path.join(SAVED_MODELS_DIR, "model_comparison.md"), "w") as f:
        f.write("# Model Comparison\n\n" + "\n".join(comparison_rows) + "\n")

    # Hyperparameter tuning on the best-performing tree-based model so far
    best_name = max(results, key=lambda n: results[n]["roc_auc"])
    if best_name == "random_forest":
        param_grid = {"n_estimators": [100, 200], "max_depth": [8, 12]}
        base = RandomForestClassifier(class_weight="balanced", random_state=42, n_jobs=-1)
    elif best_name == "gradient_boosting":
        param_grid = {"n_estimators": [100, 150], "max_depth": [3, 4]}
        base = GradientBoostingClassifier(random_state=42)
    else:
        param_grid = None
        base = None

    if param_grid:
        with mlflow.start_run(run_name=f"{best_name}_tuned"):
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            grid = GridSearchCV(base, param_grid, scoring="roc_auc", cv=cv, n_jobs=-1)
            grid.fit(X_train_res, y_train_res)
            tuned_model = grid.best_estimator_
            y_pred = tuned_model.predict(X_test_t)
            y_proba = tuned_model.predict_proba(X_test_t)[:, 1]
            metrics = evaluate(y_test, y_pred, y_proba)
            mlflow.log_params(grid.best_params_)
            mlflow.log_metrics({k: v for k, v in metrics.items() if k != "confusion_matrix"})
            if metrics["roc_auc"] > results[best_name]["roc_auc"]:
                results[f"{best_name}_tuned"] = metrics
                fitted_models[f"{best_name}_tuned"] = tuned_model
                best_name = f"{best_name}_tuned"

    best_model = fitted_models[best_name]
    print(f"\nBest model: {best_name} (ROC-AUC={results[best_name]['roc_auc']:.4f})")

    y_pred_best = best_model.predict(X_test_t)
    y_proba_best = best_model.predict_proba(X_test_t)[:, 1]
    plots_dir = os.path.join(SAVED_MODELS_DIR, "plots")
    generate_all_plots(y_test, y_pred_best, y_proba_best, plots_dir)
    save_calibration_curve(y_test, y_proba_best, os.path.join(plots_dir, "calibration_curve.png"))
    save_lift_curve(y_test, y_proba_best, os.path.join(plots_dir, "lift_curve.png"))
    print("Saved confusion matrix / ROC / PR / calibration / lift curve plots to", plots_dir)

    optimal_threshold, optimal_cost = optimize_threshold_by_cost(y_test.values, y_proba_best)
    print(f"Cost-optimal threshold: {optimal_threshold:.3f} (estimated cost={optimal_cost})")

    feature_names = list(preprocessor.get_feature_names_out())
    joblib.dump(best_model, os.path.join(SAVED_MODELS_DIR, "best_model.pkl"))
    joblib.dump(preprocessor, os.path.join(SAVED_MODELS_DIR, "preprocessor.pkl"))
    with open(os.path.join(SAVED_MODELS_DIR, "feature_names.json"), "w") as f:
        json.dump(feature_names, f)
    with open(os.path.join(SAVED_MODELS_DIR, "metrics.json"), "w") as f:
        json.dump({"best_model": best_name, "results": results}, f, indent=2)
    with open(os.path.join(SAVED_MODELS_DIR, "model_meta.json"), "w") as f:
        json.dump({
            "model_name": best_name,
            "categorical_cols": CATEGORICAL_COLS,
            "numeric_cols": NUMERIC_COLS,
            "cost_optimal_threshold": optimal_threshold,
        }, f, indent=2)

    print("Saved model artifacts to", SAVED_MODELS_DIR)


if __name__ == "__main__":
    main()
