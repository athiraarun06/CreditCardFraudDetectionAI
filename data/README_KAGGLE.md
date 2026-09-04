# Using the real Kaggle Credit Card Fraud dataset

This project ships with a synthetic dataset (`transactions.csv`) that powers the interactive
Predict page, dashboard, and analytics (it has business fields like merchant category, location,
age, payment method — fields a user can actually type into a form).

The real Kaggle dataset ("Credit Card Fraud Detection", ULB/MLG) at
https://www.kaggle.com/mlg-ulb/creditcardfraud has a **different schema**: `Time`, `V1`...`V28`
(anonymized PCA components), `Amount`, `Class`. It contains no merchant/location/age/payment
fields — those were removed for privacy when the dataset was published — so it cannot power the
interactive form. It's included here to demonstrate the pipeline on real, industry-standard fraud
data with genuine metrics.

## Steps

1. Download `creditcard.csv` from Kaggle (requires a free Kaggle account):
   ```bash
   kaggle datasets download -d mlg-ulb/creditcardfraud -p data/ --unzip
   ```
   or download manually from the Kaggle website and place the file at `data/creditcard.csv`.

2. From `backend/`, run the dedicated training pipeline:
   ```bash
   python -m app.ml.train_kaggle
   ```
   This trains Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost, and
   LightGBM (if installed) directly on `Time/V1-V28/Amount -> Class`, applies SMOTE, evaluates
   each with accuracy/precision/recall/F1/ROC-AUC/PR-AUC, picks the best by ROC-AUC, and saves:
   - `saved_models/kaggle_best_model.pkl`
   - `saved_models/kaggle_metrics.json`
   - `saved_models/kaggle_plots/confusion_matrix.png`, `roc_curve.png`, `pr_curve.png`

This is a standalone benchmark — it does not replace the model behind `/predict`, since that
endpoint needs to accept the business-schema fields the frontend form collects.
