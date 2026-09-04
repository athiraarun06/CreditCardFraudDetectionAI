import os
import json
import joblib
import numpy as np
import pandas as pd

from app.ml.features import engineer_features, CATEGORICAL_COLS, NUMERIC_COLS, haversine_km
from app.ml.decision_engine import (
    evaluate_rules, combine_scores, risk_level_from_probability,
    recommended_action, build_explanation,
)

from app.core.paths import SAVED_MODELS_DIR

_model = None
_preprocessor = None
_feature_names = None
_meta = None


def _load():
    global _model, _preprocessor, _feature_names, _meta
    if _model is None:
        _model = joblib.load(os.path.join(SAVED_MODELS_DIR, "best_model.pkl"))
        _preprocessor = joblib.load(os.path.join(SAVED_MODELS_DIR, "preprocessor.pkl"))
        with open(os.path.join(SAVED_MODELS_DIR, "feature_names.json")) as f:
            _feature_names = json.load(f)
        with open(os.path.join(SAVED_MODELS_DIR, "model_meta.json")) as f:
            _meta = json.load(f)
    return _model, _preprocessor, _feature_names, _meta


def _row_from_dict(txn: dict) -> pd.DataFrame:
    row = dict(txn)
    row.setdefault("transaction_id", "manual")
    row.setdefault("transaction_time", pd.Timestamp.utcnow().isoformat())
    row.setdefault("avg_transaction_amount", txn.get("amount", 0))
    row.setdefault("location", txn.get("merchant_city") or txn.get("location") or "unknown")
    row.setdefault("customer_age", txn.get("customer_age") or txn.get("age") or 30)

    if not row.get("distance_from_prev_km") and txn.get("latitude") and txn.get("prev_latitude"):
        row["distance_from_prev_km"] = haversine_km(
            txn.get("prev_latitude"), txn.get("prev_longitude"),
            txn.get("latitude"), txn.get("longitude"),
        )

    df = pd.DataFrame([row])
    return engineer_features(df)


def _humanize_feature(encoded_name: str, df_row: pd.DataFrame):
    """
    Maps an encoded feature name (e.g. "cat__payment_method_UPI" or "num__amount_ratio") back to
    the actual transaction field and the value it holds for THIS transaction, so the explanation
    can never reference a category the user didn't actually select.

    Returns (readable_label, actual_value, is_active) — is_active is False for a one-hot column
    that doesn't match this transaction's real category (e.g. "payment_method_UPI" when the user
    picked "Credit Card"), so callers can filter those out entirely.
    """
    if encoded_name.startswith("cat__"):
        rest = encoded_name[len("cat__"):]
        for col in CATEGORICAL_COLS:
            prefix = col + "_"
            if rest.startswith(prefix):
                category = rest[len(prefix):]
                actual_value = str(df_row[col].iloc[0]) if col in df_row.columns else None
                is_active = actual_value is not None and actual_value == category
                return f"{col} = {actual_value}", actual_value, is_active
        return encoded_name, None, False

    if encoded_name.startswith("num__"):
        col = encoded_name[len("num__"):]
        actual_value = df_row[col].iloc[0] if col in df_row.columns else None
        if isinstance(actual_value, (int, float, np.integer, np.floating)):
            display = round(float(actual_value), 3)
        else:
            display = actual_value
        return f"{col} = {display}", actual_value, True

    return encoded_name, None, True


def top_contributing_features(model, preprocessor, X_transformed, feature_names, df_row, top_n=5):
    """
    Returns the top contributing features, restricted to ones that actually apply to this
    transaction (active categorical dummies only; numeric features are always active), with
    human-readable labels showing the real field and value — never a category the user didn't
    select.
    """
    try:
        import shap
        if hasattr(model, "feature_importances_"):
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_transformed)
            if isinstance(shap_values, list):
                values = shap_values[1][0]
            elif np.asarray(shap_values).ndim == 3:
                values = np.asarray(shap_values)[0, :, 1]
            else:
                values = shap_values[0]
        else:
            raise ValueError("not a tree model")
    except Exception:
        if hasattr(model, "feature_importances_"):
            values = model.feature_importances_
        elif hasattr(model, "coef_"):
            values = model.coef_[0] * X_transformed.toarray()[0] if hasattr(X_transformed, "toarray") else model.coef_[0]
        else:
            values = np.zeros(len(feature_names))

    values = np.array(values).flatten()

    enriched = []
    for i, name in enumerate(feature_names):
        label, actual_value, is_active = _humanize_feature(name, df_row)
        if not is_active:
            continue  # skip categorical dummies that don't reflect this transaction's real value
        enriched.append({
            "feature": label,
            "raw_feature": name,
            "impact": float(values[i]),
            "actual_value": actual_value,
        })

    enriched.sort(key=lambda f: -abs(f["impact"]))
    return enriched[:top_n]


def predict(transaction: dict, threshold: float = 0.7):
    model, preprocessor, feature_names, meta = _load()
    df_row = _row_from_dict(transaction)
    X = df_row[CATEGORICAL_COLS + NUMERIC_COLS]
    X_t = preprocessor.transform(X)

    ml_probability = float(model.predict_proba(X_t)[:, 1][0])
    rule_score, triggered_rules = evaluate_rules(transaction)
    combined_probability = combine_scores(ml_probability, rule_score)

    prediction = int(combined_probability >= threshold or rule_score >= 0.6)
    contributors = top_contributing_features(model, preprocessor, X_t, feature_names, df_row)

    risk_level = risk_level_from_probability(combined_probability)
    action = recommended_action(combined_probability, triggered_rules)
    explanation = build_explanation(
        txn=transaction,
        df_row=df_row,
        prediction=prediction,
        risk_level=risk_level,
        recommended_action_text=action,
        top_features=contributors,
        triggered_rules=triggered_rules,
    )

    # Confidence: how far the probability is from the decision boundary (0.5), scaled to [0,1]
    confidence = round(min(abs(combined_probability - 0.5) * 2, 1.0), 4)

    return {
        "probability": combined_probability,
        "ml_probability": round(ml_probability, 6),
        "rule_score": round(rule_score, 6),
        "prediction": prediction,
        "threshold": threshold,
        "risk_level": risk_level,
        "confidence": confidence,
        "top_features": [{"feature": c["feature"], "impact": c["impact"]} for c in contributors],
        "triggered_rules": triggered_rules,
        "recommended_action": action,
        "explanation": explanation,
        "model_used": meta["model_name"],
    }
