import os
import json
import joblib
import numpy as np
import pandas as pd

from app.ml.features import engineer_features, CATEGORICAL_COLS, NUMERIC_COLS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
SAVED_MODELS_DIR = os.path.join(PROJECT_ROOT, "saved_models")
SHAP_DIR = os.path.join(SAVED_MODELS_DIR, "shap")
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "transactions.csv")


def get_feature_importance(top_n=15):
    model = joblib.load(os.path.join(SAVED_MODELS_DIR, "best_model.pkl"))
    with open(os.path.join(SAVED_MODELS_DIR, "feature_names.json")) as f:
        feature_names = json.load(f)

    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_[0])
    else:
        importances = np.zeros(len(feature_names))

    pairs = sorted(zip(feature_names, importances), key=lambda p: -p[1])[:top_n]
    return [{"feature": name, "importance": float(val)} for name, val in pairs]


def generate_shap_plots(sample_size=200):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(SHAP_DIR, exist_ok=True)
    model = joblib.load(os.path.join(SAVED_MODELS_DIR, "best_model.pkl"))
    preprocessor = joblib.load(os.path.join(SAVED_MODELS_DIR, "preprocessor.pkl"))
    with open(os.path.join(SAVED_MODELS_DIR, "feature_names.json")) as f:
        feature_names = np.array(json.load(f))

    df = pd.read_csv(DATA_PATH).sample(min(sample_size, 500), random_state=42)
    df = engineer_features(df)
    X = df[CATEGORICAL_COLS + NUMERIC_COLS]
    X_t = preprocessor.transform(X)
    if hasattr(X_t, "toarray"):
        X_t = X_t.toarray()

    import shap
    if hasattr(model, "feature_importances_"):
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_t)
        if isinstance(shap_values, list):
            sv = shap_values[1]  # positive (fraud) class
        elif shap_values.ndim == 3:
            sv = shap_values[:, :, 1]  # (n_samples, n_features, n_classes) -> positive class
        else:
            sv = shap_values
    else:
        explainer = shap.Explainer(model, X_t)
        sv = explainer(X_t).values
        if sv.ndim == 3:
            sv = sv[:, :, 1]

    sv = np.asarray(sv)
    if sv.ndim != 2:
        sv = sv.reshape(sv.shape[0], -1)

    plt.figure()
    shap.summary_plot(sv, X_t, feature_names=feature_names, show=False)
    plt.tight_layout()
    plt.savefig(os.path.join(SHAP_DIR, "summary_plot.png"), dpi=120)
    plt.close()

    plt.figure()
    mean_abs = np.abs(sv).mean(axis=0)
    idx = np.argsort(-mean_abs)[:15]
    plt.barh([feature_names[i] for i in idx][::-1], mean_abs[idx][::-1], color="#8b5cf6")
    plt.title("SHAP Feature Importance")
    plt.tight_layout()
    plt.savefig(os.path.join(SHAP_DIR, "feature_importance.png"), dpi=120)
    plt.close()

    try:
        ev = explainer.expected_value
        if isinstance(ev, (list, np.ndarray)):
            ev = np.asarray(ev).flatten()
            base_value = float(ev[1]) if len(ev) > 1 else float(ev[0])
        else:
            base_value = float(ev)
        exp = shap.Explanation(
            values=sv[0], base_values=base_value, data=X_t[0], feature_names=feature_names,
        )
        plt.figure()
        shap.plots.waterfall(exp, show=False)
        plt.tight_layout()
        plt.savefig(os.path.join(SHAP_DIR, "waterfall_plot.png"), dpi=120)
        plt.close()
    except Exception as e:
        print("Waterfall plot skipped:", e)

    print("SHAP plots saved to", SHAP_DIR)


if __name__ == "__main__":
    generate_shap_plots()
