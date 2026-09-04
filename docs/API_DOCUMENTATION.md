# API Documentation

Interactive Swagger UI: `http://localhost:8000/docs` · ReDoc: `http://localhost:8000/redoc`

All endpoints except `/health`, `/version`, `/register`, `/login` require `Authorization: Bearer <JWT>`.
Rate limit: 120 requests/minute per client IP (returns `429` when exceeded).

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/version` | App version + server time |
| GET | `/model-info` | Trained model name, features, latest metrics |
| POST | `/register` | Create a user account |
| POST | `/login` | Get a JWT access token |
| POST | `/predict` | Score one transaction (full realistic schema) |
| POST | `/predict-batch` | Score a CSV of transactions (multipart upload, max 2000 rows) |
| GET | `/transactions` | Paginated, filterable transaction + prediction history |
| GET | `/transactions/{transaction_id}` | Full detail for one transaction |
| POST | `/transactions` | Log a raw transaction without fraud scoring (bulk import) |
| GET | `/customers` | List/search customers |
| GET | `/customers/{customer_id}` | Customer profile: spending history, merchant breakdown, fraud history |
| GET | `/alerts` | List fraud alerts, filterable by status/risk level |
| POST | `/alerts/{alert_id}/action` | Approve / Block / Review / Freeze an alert |
| GET | `/analytics` | KPIs + chart data, filterable by date/category/location/payment method/country/risk level |
| GET | `/metrics` | Last training run's model comparison metrics |
| GET | `/feature-importance` | Global feature importance list |
| GET | `/explainability` | Feature importance + plain-English explanations + SHAP/plot image URLs |
| POST | `/retrain` | Kick off model retraining in the background |

## Example: full `/predict` request

```bash
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Priya Nair", "email": "priya@example.com", "customer_age": 29,
    "gender": "Female", "customer_risk_profile": "Low",
    "amount": 150000, "currency": "INR",
    "merchant_name": "Unknown Electronics", "merchant_category": "electronics",
    "merchant_country": "Russia", "merchant_city": "Moscow", "merchant_risk_score": 0.9,
    "payment_method": "Credit Card", "card_type": "Visa", "card_last4": "1234",
    "device_type": "Web", "device_trusted": false, "vpn_detected": true,
    "previous_transactions": 2, "avg_transaction_amount": 1200,
    "txns_last_hour": 6, "txns_last_day": 8,
    "is_new_merchant": true, "is_new_device": true, "is_new_location": true,
    "otp_verified": false, "failed_login_attempts": 4,
    "threshold": 0.7
  }'
```

Response includes `probability`, `ml_probability`, `rule_score`, `risk_level`
(Low/Medium/High/Critical), `confidence`, `recommended_action`
(Approve Automatically / Send OTP Verification / Hold for Manual Review / Decline Transaction /
Freeze Account), `top_features` (SHAP), `triggered_rules`, and a plain-English `explanation`.

## Example: batch predict

```bash
curl -X POST http://localhost:8000/predict-batch \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@transactions_to_score.csv"
```
Required CSV columns: `amount, merchant_category, customer_age, payment_method, customer_name, merchant_name`.

## Example: acting on an alert

```bash
curl -X POST http://localhost:8000/alerts/1/action \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"status": "Frozen"}'
```
