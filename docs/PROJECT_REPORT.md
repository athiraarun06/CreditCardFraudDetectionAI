# Project Report: Credit Card Fraud Detection AI System

## 1. Introduction

Credit card fraud costs the global financial industry tens of billions of dollars annually. This
project builds a real-time fraud detection platform combining a machine learning risk model with
a business rule engine, wrapped in a full-stack fintech application that mirrors how a bank's
fraud operations team would actually work: score transactions in real time, queue high-risk ones
for manual review, track customer risk profiles, and explain every decision.

## 2. Objectives

- Build an end-to-end system: data → features → ML model → rule engine → API → UI.
- Detect fraud in real time with an interpretable, auditable decision (not a black box).
- Support both a synthetic demo dataset (for the interactive UI) and the real Kaggle Credit Card
  Fraud dataset (for genuine model benchmarking).
- Ship a production-shaped system: authentication, rate limiting, structured logging, error
  handling, Docker packaging, and automated tests — not just a notebook.

## 3. System Overview

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for full diagrams. In short:

- **Frontend**: React + Vite + Tailwind + Framer Motion, seven pages (Dashboard, Predict, Alerts,
  Analytics, History, Customers, Explainability), dark/light theming, toasts, skeleton loading
  states, and a mobile-responsive layout.
- **Backend**: FastAPI with JWT authentication, structured logging, a global exception handler,
  an in-memory rate limiter, and 18 REST endpoints.
- **ML**: scikit-learn/XGBoost/LightGBM models trained with SMOTE-balanced data, evaluated with
  accuracy/precision/recall/F1/ROC-AUC/PR-AUC/MCC, a cost-optimized decision threshold, and SHAP
  explainability.
- **Decision Engine**: combines the ML probability with an explicit business rule set (velocity
  bursts, impossible travel, high-risk merchants, VPN/proxy detection, failed OTP, new
  device+location+high-amount combinations) into one auditable score.
- **Database**: SQLite by default (zero setup), PostgreSQL supported via `DATABASE_URL`. Seven
  tables: users, customers, merchants, transactions, predictions, alerts, model_metrics.

## 4. Data

Two datasets are used, deliberately for different purposes (see
[`data/README_KAGGLE.md`](../data/README_KAGGLE.md) for the full rationale):
1. A synthetic, business-schema dataset (`transactions.csv`) with human-meaningful fields
   (merchant, location, age, payment method) that powers the interactive Predict form.
2. The real, anonymized Kaggle "Credit Card Fraud Detection" dataset (`creditcard.csv`,
   PCA-transformed `V1`-`V28` features), trained via a separate pipeline
   (`app/ml/train_kaggle.py`) to benchmark against industry-standard, real-world fraud data.

## 5. Feature Engineering

Beyond raw transaction fields, the pipeline derives: `amount_ratio`, `amount_difference`,
`is_night_transaction`, `weekend_transaction`, `international_transaction`, `device_change`,
`merchant_frequency`, `customer_velocity_score`, `geo_distance` (haversine), `transaction_velocity`,
`historical_success_rate`, and flags for VPN/device-trust/OTP status. See
`backend/app/ml/features.py`.

## 6. Model Training & Evaluation

Five to six classifiers are trained and compared (Logistic Regression, Decision Tree, Random
Forest, Gradient Boosting, XGBoost, LightGBM where available), the best selected by ROC-AUC, then
tuned via `GridSearchCV` with 5-fold stratified cross-validation. See
`saved_models/model_comparison.md` and `saved_models/metrics.json` for the actual run's numbers,
and `saved_models/plots/` for the generated confusion matrix, ROC curve, PR curve, calibration
curve, and lift curve.

## 7. Decision Engine

`app/ml/decision_engine.py` implements explicit rules (e.g. "amount > ₹1,00,000 AND new device AND
new location → Critical") and blends the rule score with the ML probability via
`1 - (1-ml_prob)×(1-rule_score)`, so either signal can escalate risk. Risk is bucketed into
Low/Medium/High/Critical, mapped to a recommended action (Approve Automatically / Send OTP
Verification / Hold for Manual Review / Decline Transaction / Freeze Account), and explained in
plain English (`build_explanation()`).

## 8. Testing

30 realistic scenarios (routine purchases through classic fraud patterns) were run against the
live API — see [`TESTING_REPORT.md`](TESTING_REPORT.md) for the full results table and analysis.
Routine transactions consistently scored low risk; transactions stacking multiple independent
risk signals correctly escalated to Critical.

## 9. Results Summary

- End-to-end verified: registration, login, real-time prediction, batch CSV prediction, alert
  management, customer profiles, analytics filtering, CSV/PDF export, and SHAP explainability all
  function against a live database.
- The combined ML+rules approach avoids both failure modes of a naive system: it doesn't
  auto-decline every large purchase (unacceptable false-positive rate), and it doesn't miss
  fraud patterns that a pure ML model under-weights (compounding behavioral red flags).

## 10. Future Work

Real-time streaming ingestion, MLflow Model Registry-backed versioning, role-based access control,
Redis-backed rate limiting for multi-instance deployments, and training on a larger real-world
labeled dataset.
