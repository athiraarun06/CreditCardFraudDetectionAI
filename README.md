# Credit Card Fraud Detection AI System

A real-time, production-shaped fraud detection platform: a machine learning risk model combined
with an explicit business rule engine, wrapped in a full-stack fintech application built to look
and behave like something a bank's fraud operations team could actually use.

Built as an internship/portfolio submission — see [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md)
for the full write-up, [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for diagrams (system
architecture, ER diagram, ML pipeline, deployment), [`docs/TESTING_REPORT.md`](docs/TESTING_REPORT.md)
for real test results, [`docs/VIVA_QUESTIONS.md`](docs/VIVA_QUESTIONS.md) for viva prep, and
[`docs/Project_Presentation.pptx`](docs/Project_Presentation.pptx) for a slide deck generated from
this project's actual training metrics.

## Features

- **Real-time fraud scoring**: ML probability + business rule engine, combined into one auditable
  score with risk level (Low/Medium/High/Critical), confidence, recommended action, and a
  plain-English explanation.
- **Realistic transaction schema**: customer info, payment info, device/network signals
  (IP, VPN detection, geo-distance, device trust), and behavioral features (velocity, new
  device/location/merchant flags, OTP status) — not a toy form.
- **Full ML lifecycle**: cleaning, feature engineering (12+ engineered features), SMOTE, 5-6 model
  comparison, GridSearchCV tuning, cost-optimal threshold selection, and auto-generated confusion
  matrix / ROC / PR / calibration / lift curve plots.
- **SHAP explainability**: summary plot, waterfall plot, feature importance, and per-prediction
  local explanations, surfaced through the UI.
- **Fraud Operations Center UI**: live Dashboard (7 KPIs, 8 charts), Alert Center (Approve/Block/
  Review/Freeze), Customer Profiles (spending history, fraud history), searchable/filterable
  History with a detail modal and CSV/PDF export, and interactive Explainability.
- **Batch prediction**: score a whole CSV of transactions via `/predict-batch`.
- **Security**: JWT auth, bcrypt password hashing, rate limiting, input validation, configurable
  CORS, structured logging, global exception handling.
- **Zero-setup database**: SQLite by default, PostgreSQL via `DATABASE_URL`.
- **Dark/light fintech UI**: glassmorphism, animated speedometer risk meter, toast notifications,
  loading skeletons, empty states, mobile-responsive.

## Screenshots

> _Add screenshots here after running the app locally._

![Dashboard](docs/screenshots/dashboard.png)
![Predict](docs/screenshots/predict.png)
![Alerts](docs/screenshots/alerts.png)

## Folder Structure

```
CreditCardFraudDetectionAI/
├── frontend/src/
│   ├── components/ui/     # Card, Button, Input, Select, Badge, KpiCard, RiskMeter, Skeleton, Modal, Toggle
│   ├── pages/               # Dashboard, Predict, Alerts, Analytics, History, Customers, CustomerProfile, Explainability
│   └── lib/                  # api.js, toast.jsx, theme.jsx, demoData.js
├── backend/app/
│   ├── routers/              # auth, predict, predict_batch, analytics, transactions, alerts,
│   │                           customers, metrics, feature_importance, retrain, health, meta
│   ├── models/                # user, customer, merchant, transaction, prediction, alert, model_metrics
│   ├── schemas/                # Pydantic schemas
│   ├── core/                    # database.py, security.py, rate_limit.py
│   └── ml/                      # features.py, train.py, train_kaggle.py, predict.py,
│                                   decision_engine.py, explain.py, plots.py
├── backend/tests/               # generate_test_transactions.py (30 real scenarios)
├── data/                          # transactions.csv + generate_data.py (+ optional creditcard.csv)
├── notebooks/eda.ipynb
├── sql/schema.sql
├── saved_models/                  # best_model.pkl, metrics.json, model_comparison.md, plots/, shap/
├── docs/                            # ARCHITECTURE.md, API_DOCUMENTATION.md, PROJECT_REPORT.md,
│                                       TESTING_REPORT.md, VIVA_QUESTIONS.md, Project_Presentation.pptx
├── docker-compose.yml
└── README.md
```

## Installation on macOS

### Prerequisites
Python 3.11+, Node.js 18+, (optional) Docker Desktop, (optional) PostgreSQL.

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

> **LightGBM on macOS** needs `libomp`: `brew install libomp && pip install lightgbm`. Training
> works fine without it — LightGBM is simply skipped from the comparison.

```bash
python data/generate_data.py     # generate synthetic demo dataset
python -m app.ml.train           # train & compare models, save best + plots
python -m app.ml.explain         # generate SHAP visualizations
uvicorn app.main:app --reload
```
SQLite (`backend/fraud.db`) is created automatically — no database setup required.

### Frontend

```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:5173`, register an account, and start scoring transactions.

### Run the test suite

```bash
cd backend
python tests/generate_test_transactions.py   # 30 realistic scenarios, see docs/TESTING_REPORT.md
```

## Using SQLite or PostgreSQL

Default: SQLite at `backend/fraud.db`, zero configuration. To use PostgreSQL, copy
`backend/.env.example` to `backend/.env` and set:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fraud_detection
```
Tables are created automatically on startup either way.

## Using the Real Kaggle Dataset

The interactive Predict form uses a business-schema synthetic dataset (fields a human can type
in). The real Kaggle dataset (anonymized PCA features) is supported as a separate benchmark
pipeline — see [`data/README_KAGGLE.md`](data/README_KAGGLE.md):
```bash
kaggle datasets download -d mlg-ulb/creditcardfraud -p data/ --unzip
cd backend && python -m app.ml.train_kaggle
```

## Docker Setup

```bash
cp .env.example .env
docker-compose up --build
```
Starts PostgreSQL (auto-seeded with `sql/schema.sql`), backend on `:8000`, frontend on `:4173`.

## API Documentation

See [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) for the full endpoint reference and
example requests, or the live Swagger UI at `http://localhost:8000/docs`.

## Security

- JWT authentication (`python-jose`), bcrypt password hashing (direct `bcrypt`, not the
  now-incompatible `passlib` shim).
- In-memory rate limiting (120 req/min/IP; swap for Redis in a multi-instance deployment).
- Pydantic input validation on every endpoint; a global exception handler returns clean errors
  instead of leaking stack traces.
- CORS origins configurable via `ALLOWED_ORIGINS` env var (defaults to permissive localhost
  matching for local dev only).
- Secrets (JWT secret, database URL) read from environment variables, never hardcoded.

## Testing

30 realistic transaction scenarios (grocery purchases through cross-border fraud patterns) are
run against the live API in `backend/tests/generate_test_transactions.py`. Full results and
analysis: [`docs/TESTING_REPORT.md`](docs/TESTING_REPORT.md).

## Documentation Index

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system architecture, ER diagram, ML pipeline,
  sequence diagram, deployment diagram (all as Mermaid, renders directly on GitHub).
- [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) — endpoint reference.
- [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md) — formal write-up.
- [`docs/TESTING_REPORT.md`](docs/TESTING_REPORT.md) — real test run results.
- [`docs/VIVA_QUESTIONS.md`](docs/VIVA_QUESTIONS.md) — anticipated questions with answers.
- [`docs/Project_Presentation.pptx`](docs/Project_Presentation.pptx) — slide deck (generated from
  this project's actual training metrics via `docs/generate_pptx.py`).

## Future Enhancements

Real-time streaming ingestion (Kafka), MLflow Model Registry-backed model versioning, role-based
access control, Redis-backed rate limiting for multi-instance deployments, and training on a
larger real-world labeled dataset.
