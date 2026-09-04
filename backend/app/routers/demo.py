import random
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.transaction import Transaction
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.user import User
from app.ml.predict import predict as run_prediction
from app.routers.predict import _upsert_customer, _upsert_merchant
from app.schemas.schemas import TransactionInput

router = APIRouter(tags=["demo"])

DEMO_CUSTOMERS = [
    {"name": "Athira Arun", "email": "athira.personal@example.com", "age": 27, "gender": "Female"},
    {"name": "Athira Arun (Business)", "email": "athira.business@example.com", "age": 27, "gender": "Female"},
    {"name": "Rahul Sharma", "email": "rahul.sharma@example.com", "age": 34, "gender": "Male"},
]

MERCHANTS = [
    ("Big Bazaar", "grocery", 0.05), ("DMart", "grocery", 0.05),
    ("Indian Oil", "fuel", 0.05), ("Shell", "fuel", 0.08),
    ("MakeMyTrip", "travel", 0.15), ("IRCTC", "travel", 0.1),
    ("Amazon", "online", 0.1), ("Flipkart", "online", 0.1),
    ("Swiggy", "dining", 0.05), ("Zomato", "dining", 0.05),
    ("Netflix", "entertainment", 0.05), ("Spotify", "entertainment", 0.05),
    ("PVR Cinemas", "entertainment", 0.05),
    ("Apollo Pharmacy", "grocery", 0.05),
    ("Tanishq Jewellery", "electronics", 0.2),
    ("Reliance Digital", "electronics", 0.15),
    ("HDFC ATM", "other", 0.05), ("SBI ATM", "other", 0.05),
    ("Uber", "travel", 0.08),
    ("Unknown Overseas Retailer", "electronics", 0.85),
]

CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Wallet", "Net Banking"]
DEVICE_TYPES = ["Android", "iPhone", "Web"]

CATEGORY_AMOUNT_RANGE = {
    "grocery": (200, 3000), "fuel": (500, 4000), "travel": (2000, 40000),
    "online": (300, 15000), "dining": (150, 2500), "entertainment": (150, 1500),
    "electronics": (2000, 150000), "other": (500, 20000),
}


@router.post("/demo/generate")
def generate_demo_transactions(
    count: int = Query(70, ge=10, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generates realistic demo transactions for THIS user only — never shared or visible to
    other accounts. Roughly 8-12% are deliberately built to look fraudulent so the dashboard,
    alerts, and analytics have something meaningful to show."""
    created = 0
    fraud_count = 0
    now = datetime.utcnow()

    for i in range(count):
        customer = random.choice(DEMO_CUSTOMERS)
        merchant_name, category, base_risk = random.choice(MERCHANTS)
        low, high = CATEGORY_AMOUNT_RANGE[category]

        make_fraud = random.random() < 0.10
        days_ago = random.uniform(0, 30)
        txn_time = now - timedelta(days=days_ago, hours=random.uniform(0, 24))

        if make_fraud:
            amount = round(random.uniform(high * 3, high * 8), 2)
            is_new_device = True
            is_new_location = random.random() < 0.7
            vpn_detected = random.random() < 0.5
            device_trusted = False
            otp_verified = random.random() < 0.3
            txns_last_hour = random.randint(3, 9)
            failed_login_attempts = random.randint(1, 5)
            merchant_risk_score = max(base_risk, random.uniform(0.5, 0.95))
            txn_time = txn_time.replace(hour=random.choice([0, 1, 2, 3, 22, 23]))
        else:
            amount = round(random.uniform(low, high), 2)
            is_new_device = random.random() < 0.05
            is_new_location = random.random() < 0.05
            vpn_detected = False
            device_trusted = True
            otp_verified = True
            txns_last_hour = random.randint(0, 2)
            failed_login_attempts = 0
            merchant_risk_score = base_risk

        payload_data = {
            "customer_name": customer["name"],
            "email": customer["email"],
            "customer_age": customer["age"],
            "gender": customer["gender"],
            "amount": amount,
            "currency": "INR",
            "transaction_time": txn_time.isoformat(),
            "merchant_name": merchant_name,
            "merchant_category": category,
            "merchant_country": "India" if not (make_fraud and random.random() < 0.3) else "Russia",
            "merchant_city": random.choice(CITIES),
            "merchant_risk_score": round(merchant_risk_score, 2),
            "payment_method": random.choice(PAYMENT_METHODS),
            "device_type": random.choice(DEVICE_TYPES),
            "device_trusted": device_trusted,
            "vpn_detected": vpn_detected,
            "previous_transactions": random.randint(5, 80),
            "avg_transaction_amount": round((low + high) / 2, 2),
            "txns_last_hour": txns_last_hour,
            "txns_last_day": txns_last_hour + random.randint(0, 5),
            "is_new_merchant": random.random() < 0.15,
            "is_new_device": is_new_device,
            "is_new_location": is_new_location,
            "failed_login_attempts": failed_login_attempts,
            "otp_verified": otp_verified,
            "threshold": 0.7,
        }

        try:
            payload = TransactionInput(**payload_data)
        except Exception:
            continue

        txn_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        customer_id = _upsert_customer(db, payload, current_user)
        merchant_id = _upsert_merchant(db, payload)

        txn_dict = payload.dict()
        txn_dict["transaction_id"] = txn_id
        txn_dict["transaction_time"] = payload_data["transaction_time"]

        result = run_prediction(txn_dict, threshold=payload.threshold)

        db.add(Transaction(
            user_id=current_user.id,
            transaction_id=txn_id,
            customer_id=customer_id,
            customer_name=payload.customer_name,
            amount=payload.amount,
            currency=payload.currency,
            transaction_time=txn_time,
            merchant_id=merchant_id,
            merchant_name=payload.merchant_name,
            merchant_category=payload.merchant_category,
            merchant_country=payload.merchant_country,
            merchant_city=payload.merchant_city,
            merchant_risk_score=payload.merchant_risk_score,
            payment_method=payload.payment_method,
            device_type=payload.device_type,
            device_trusted=payload.device_trusted,
            vpn_detected=payload.vpn_detected,
            previous_transactions=payload.previous_transactions,
            avg_transaction_amount=payload.avg_transaction_amount,
            txns_last_hour=payload.txns_last_hour,
            txns_last_day=payload.txns_last_day,
            is_new_merchant=payload.is_new_merchant,
            is_new_device=payload.is_new_device,
            is_new_location=payload.is_new_location,
            failed_login_attempts=payload.failed_login_attempts,
            otp_verified=payload.otp_verified,
            customer_age=payload.customer_age,
            location=payload.merchant_city,
            fraud_probability=result["probability"],
            fraud_label=result["prediction"],
        ))
        db.add(Prediction(
            user_id=current_user.id,
            transaction_id=txn_id,
            probability=result["probability"],
            ml_probability=result["ml_probability"],
            rule_score=result["rule_score"],
            prediction=result["prediction"],
            threshold=result["threshold"],
            risk_level=result["risk_level"],
            confidence=result["confidence"],
            model_used=result["model_used"],
            top_features=result["top_features"],
            triggered_rules=result["triggered_rules"],
            recommended_action=result["recommended_action"],
            explanation=result["explanation"],
        ))
        if result["risk_level"] in ("High", "Critical"):
            db.add(Alert(
                user_id=current_user.id,
                transaction_id=txn_id,
                customer_name=payload.customer_name,
                amount=payload.amount,
                merchant_name=payload.merchant_name,
                location=payload.merchant_city,
                probability=result["probability"],
                risk_level=result["risk_level"],
                status="Pending",
            ))
            fraud_count += 1

        created += 1

    db.commit()
    return {"status": "ok", "created": created, "flagged_high_risk": fraud_count}
