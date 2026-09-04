import numpy as np, pandas as pd, uuid
from datetime import datetime, timedelta

np.random.seed(42)
N = 5000
CATEGORIES = ["grocery", "electronics", "travel", "dining", "fuel", "online", "entertainment", "other"]
CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"]
METHODS = ["credit_card", "debit_card", "upi", "netbanking", "wallet"]

start = datetime(2025, 1, 1)
rows = []
for i in range(N):
    amount = float(np.round(np.random.lognormal(mean=6.0, sigma=1.1), 2))
    amount = min(amount, 200000)
    ttime = start + timedelta(seconds=int(np.random.uniform(0, 300 * 24 * 3600)))
    category = np.random.choice(CATEGORIES, p=[0.18, 0.14, 0.08, 0.14, 0.12, 0.18, 0.10, 0.06])
    age = int(np.clip(np.random.normal(38, 12), 18, 80))
    location = np.random.choice(CITIES)
    method = np.random.choice(METHODS, p=[0.28, 0.22, 0.28, 0.12, 0.10])
    prev_txn = int(np.clip(np.random.poisson(25), 0, 500))
    avg_amt = float(np.round(np.clip(np.random.normal(amount * 0.8, amount * 0.3 + 50), 10, None), 2))

    is_night = ttime.hour < 5 or ttime.hour >= 23
    high_amount = amount > 15000
    new_location = np.random.random() < 0.1

    fraud_score = -5.5
    if high_amount: fraud_score += 2.5
    if is_night: fraud_score += 1.8
    if new_location: fraud_score += 1.5
    if amount > avg_amt * 4: fraud_score += 1.7
    if method in ("wallet", "online"): fraud_score += 0.4
    fraud_score += np.random.normal(0, 0.8)
    fraud_prob = 1 / (1 + np.exp(-fraud_score))
    fraud = 1 if np.random.random() < fraud_prob else 0

    rows.append({
        "transaction_id": str(uuid.uuid4()),
        "amount": amount,
        "transaction_time": ttime.isoformat(),
        "merchant_category": category,
        "customer_age": age,
        "location": location,
        "payment_method": method,
        "previous_transactions": prev_txn,
        "avg_transaction_amount": avg_amt,
        "fraud": fraud,
    })

df = pd.DataFrame(rows)
current_rate = df["fraud"].mean()
target_rate = 0.025
if current_rate > target_rate:
    fraud_idx = df[df.fraud == 1].index
    keep_n = int(len(df) * target_rate)
    drop_idx = np.random.choice(fraud_idx, size=max(0, len(fraud_idx) - keep_n), replace=False)
    df.loc[drop_idx, "fraud"] = 0

df.to_csv("data/transactions.csv", index=False)
print(f"Generated {len(df)} rows, fraud rate={df['fraud'].mean():.4f}")
