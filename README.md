<div align="center">

# 🛡️ Credit Card Fraud Detection AI System

**A real-time fraud detection platform combining a trained machine learning risk model with an auditable business rule engine — built to look and behave like a bank's fraud operations center.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-000000?style=for-the-badge&logo=vercel)](https://credit-card-fraud-detection-ai-athira-arun.vercel.app)
[![Backend API](https://img.shields.io/badge/Backend%20API-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://creditcard-fraud-backend.onrender.com/docs)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)

**[🚀 Try the Live App](https://credit-card-fraud-detection-ai-athira-arun.vercel.app)** · **[📘 API Docs](https://creditcard-fraud-backend.onrender.com/docs)** · **[📄 Project Report](docs/PROJECT_REPORT.md)**

*Author: **Athira Arun***

</div>

---

## 🌐 Live Deployment

| | URL |
|---|---|
| **Frontend (app)** | [credit-card-fraud-detection-ai-athira-arun.vercel.app](https://credit-card-fraud-detection-ai-athira-arun.vercel.app) |
| **Backend (API + Swagger docs)** | [creditcard-fraud-backend.onrender.com/docs](https://creditcard-fraud-backend.onrender.com/docs) |

> Register a free account on the live app, then click **"Generate Demo Transactions"** on the Dashboard to instantly populate it with realistic sample data — all private to your own account. The backend runs on Render's free tier, so the very first request after a period of inactivity may take 20–30s to wake up.

---

## ✨ Features

- 🔮 **Real-time fraud scoring** — ML probability + business rule engine, combined into one auditable score with risk level (Low/Medium/High/Critical), confidence, recommended action, and a plain-English explanation.
- 🧾 **Realistic transaction schema** — customer info, payment info, device/network signals (IP, VPN detection, geo-distance, device trust), and behavioral features (velocity, new device/location/merchant flags, OTP status) — not a toy form.
- 🤖 **Full ML lifecycle** — cleaning, feature engineering (12+ engineered features), SMOTE, 5–6 model comparison, GridSearchCV tuning, cost-optimal threshold selection, and auto-generated confusion matrix / ROC / PR / calibration / lift curve plots.
- 🔍 **SHAP explainability** — summary plot, waterfall plot, feature importance, and per-prediction local explanations, surfaced through the UI.
- 🚨 **Fraud Operations Center UI** — live Dashboard (7 KPIs, 8 charts), Alert Center (Approve/Block/Review/Freeze), Customer Profiles (spending history, fraud history), searchable/filterable History with a detail modal and CSV/PDF export, and interactive Explainability.
- 📊 **Batch prediction** — score a whole CSV of transactions via `/predict-batch`.
- 🔐 **Multi-user data isolation** — every account sees only its own transactions, alerts, customers, and analytics, enforced by JWT-scoped queries on every endpoint.
- 🛡️ **Security** — JWT auth, bcrypt password hashing, rate limiting, input validation, configurable CORS, structured logging, global exception handling.
- 🗄️ **Zero-setup database** — SQLite by default, PostgreSQL via `DATABASE_URL` (used in production).
- 🌓 **Dark/light fintech UI** — glassmorphism, animated speedometer risk meter, toast notifications, loading skeletons, empty states, mobile-responsive.

---

## 📚 Documentation

Built as an internship/portfolio submission:

| Document | Contents |
|---|---|
| [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md) | Full written report |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System architecture, ER diagram, ML pipeline & deployment diagrams (Mermaid) |
| [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) | Full endpoint reference & example requests |
| [`docs/TESTING_REPORT.md`](docs/TESTING_REPORT.md) | 30 real test scenarios run against the live API |
| [`docs/VIVA_QUESTIONS.md`](docs/VIVA_QUESTIONS.md) | Anticipated viva questions with answers |
| [`docs/Project_Presentation.pptx`](docs/Project_Presentation.pptx) | Slide deck generated from this project's actual training metrics |

---

## 📁 Folder Structure

```
CreditCardFraudDetectionAI/
├── frontend/src/
│   ├── components/ui/     # Card, Button, Input, Select, Badge, KpiCard, RiskMeter, Skeleton, Modal, Toggle
│   ├── pages/               # Dashboard, Predict, Alerts, Analytics, History, Customers, CustomerProfile, Explainability
│   └── lib/                  # api.js, toast.jsx, theme.jsx, currency.js, demoData.js
├── backend/app/
│   ├── routers/              # auth, predict, predict_batch, analytics, transactions, alerts,
│   │                           customers, demo, metrics, feature_importance, retrain, health, meta
│   ├── models/                # user, customer, merchant, transaction, prediction, alert, model_metrics
│   ├── schemas/                # Pydantic schemas
│   ├── core/                    # database.py, security.py, rate_limit.py, paths.py
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

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Framer Motion, Recharts, Axios, React Router |
| **Backend** | FastAPI, SQLAlchemy, Pydantic, python-jose, bcrypt |
| **Machine Learning** | scikit-learn, XGBoost, LightGBM, imbalanced-learn (SMOTE), SHAP, MLflow |
| **Database** | SQLite (dev) / PostgreSQL (production) |
| **Deployment** | Vercel (frontend), Render (backend + PostgreSQL), Docker + docker-compose |

---

## 💻 Installation on macOS

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

---

## 🗄️ Using SQLite or PostgreSQL

Default: SQLite at `backend/fraud.db`, zero configuration. To use PostgreSQL, copy
`backend/.env.example` to `backend/.env` and set:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fraud_detection
```
Tables are created automatically on startup either way.

## 📈 Using the Real Kaggle Dataset

The interactive Predict form uses a business-schema synthetic dataset (fields a human can type
in). The real Kaggle dataset (anonymized PCA features) is supported as a separate benchmark
pipeline — see [`data/README_KAGGLE.md`](data/README_KAGGLE.md):
```bash
kaggle datasets download -d mlg-ulb/creditcardfraud -p data/ --unzip
cd backend && python -m app.ml.train_kaggle
```

## 🐳 Docker Setup

```bash
cp .env.example .env
docker-compose up --build
```
Starts PostgreSQL (auto-seeded with `sql/schema.sql`), backend on `:8000`, frontend on `:4173`.

## 🚀 Deploying Your Own Copy

- **Frontend → Vercel**: import the repo, set Root Directory to `frontend`, add env var `VITE_API_URL` pointing at your backend.
- **Backend → Render**: create a Web Service from `backend/`, add a managed PostgreSQL instance, set `DATABASE_URL`, `JWT_SECRET`, and `ALLOWED_ORIGINS` (your frontend's URL) as environment variables.

## 📖 API Documentation

See [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) for the full endpoint reference and
example requests, or the live Swagger UI at **[creditcard-fraud-backend.onrender.com/docs](https://creditcard-fraud-backend.onrender.com/docs)** (or `http://localhost:8000/docs` locally).

## 🔐 Security

- JWT authentication (`python-jose`), bcrypt password hashing (direct `bcrypt`, not the
  now-incompatible `passlib` shim).
- In-memory rate limiting (120 req/min/IP; swap for Redis in a multi-instance deployment).
- Pydantic input validation on every endpoint; a global exception handler returns clean errors
  instead of leaking stack traces.
- CORS origins configurable via `ALLOWED_ORIGINS` env var (defaults to permissive localhost
  matching for local dev only).
- Secrets (JWT secret, database URL) read from environment variables, never hardcoded.
- Every table storing user data carries a `user_id` foreign key, and every query is scoped to the
  authenticated user — verified end-to-end with two separate test accounts and live cross-account
  access attempts (all correctly returned 404).

## 🧪 Testing

30 realistic transaction scenarios (grocery purchases through cross-border fraud patterns) are
run against the live API in `backend/tests/generate_test_transactions.py`. Full results and
analysis: [`docs/TESTING_REPORT.md`](docs/TESTING_REPORT.md).

## 🔭 Future Enhancements

Real-time streaming ingestion (Kafka), MLflow Model Registry-backed model versioning, role-based
access control, Redis-backed rate limiting for multi-instance deployments, and training on a
larger real-world labeled dataset.

---

<div align="center">

**Built by Athira Arun** · [Live Demo](https://credit-card-fraud-detection-ai-athira-arun.vercel.app) · [API Docs](https://creditcard-fraud-backend.onrender.com/docs)

</div>
