from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.transaction import Transaction
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.user import User
from app.schemas.schemas import AnalyticsResponse

router = APIRouter(tags=["analytics"])


def _age_group(age):
    if age is None:
        return "Unknown"
    if age < 25:
        return "18-24"
    if age < 35:
        return "25-34"
    if age < 45:
        return "35-44"
    if age < 60:
        return "45-59"
    return "60+"


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    merchant_category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Transaction).join(
        Prediction, Transaction.transaction_id == Prediction.transaction_id
    ).filter(Transaction.user_id == current_user.id)

    if start_date:
        q = q.filter(Transaction.transaction_time >= datetime.fromisoformat(start_date))
    if end_date:
        q = q.filter(Transaction.transaction_time <= datetime.fromisoformat(end_date))
    if merchant_category:
        q = q.filter(Transaction.merchant_category == merchant_category)
    if location:
        q = q.filter((Transaction.location == location) | (Transaction.merchant_city == location))
    if payment_method:
        q = q.filter(Transaction.payment_method == payment_method)
    if country:
        q = q.filter(Transaction.merchant_country == country)

    rows = q.add_columns(Prediction.probability, Prediction.prediction, Prediction.risk_level).all()
    if risk_level:
        rows = [r for r in rows if r.risk_level == risk_level]

    total_transactions = len(rows)
    fraud_detected = sum(1 for r in rows if r.prediction == 1)
    total_amount = sum(r.Transaction.amount for r in rows)
    amount_saved = sum(r.Transaction.amount for r in rows if r.prediction == 1)
    avg_prob = (sum(r.probability for r in rows) / total_transactions) if total_transactions else 0.0
    fraud_rate = (fraud_detected / total_transactions) if total_transactions else 0.0
    high_risk_alerts = sum(1 for r in rows if r.risk_level in ("High", "Critical"))

    pending_reviews = db.query(Alert).filter(
        Alert.status == "Pending", Alert.user_id == current_user.id
    ).count()

    by_day = {}
    by_category = {}
    by_location = {}
    by_hour = {h: {"hour": h, "total": 0, "fraud": 0} for h in range(24)}
    by_payment_method = {}
    by_device = {}
    by_age_group = {}
    recent_alerts = []

    for r in rows:
        txn = r.Transaction
        day = txn.transaction_time.strftime("%Y-%m-%d")
        by_day.setdefault(day, {"date": day, "total": 0, "fraud": 0})
        by_day[day]["total"] += 1
        by_day[day]["fraud"] += 1 if r.prediction == 1 else 0

        cat = txn.merchant_category
        by_category.setdefault(cat, {"category": cat, "total": 0, "fraud": 0})
        by_category[cat]["total"] += 1
        by_category[cat]["fraud"] += 1 if r.prediction == 1 else 0

        loc = txn.merchant_city or txn.location or "Unknown"
        by_location.setdefault(loc, {"location": loc, "total": 0, "fraud": 0})
        by_location[loc]["total"] += 1
        by_location[loc]["fraud"] += 1 if r.prediction == 1 else 0

        pm = txn.payment_method
        by_payment_method.setdefault(pm, {"payment_method": pm, "total": 0, "fraud": 0})
        by_payment_method[pm]["total"] += 1
        by_payment_method[pm]["fraud"] += 1 if r.prediction == 1 else 0

        dev = txn.device_type or "Unknown"
        by_device.setdefault(dev, {"device": dev, "total": 0, "fraud": 0})
        by_device[dev]["total"] += 1
        by_device[dev]["fraud"] += 1 if r.prediction == 1 else 0

        age_group = _age_group(txn.customer_age)
        by_age_group.setdefault(age_group, {"age_group": age_group, "total": 0, "fraud": 0})
        by_age_group[age_group]["total"] += 1
        by_age_group[age_group]["fraud"] += 1 if r.prediction == 1 else 0

        hour = txn.transaction_time.hour
        by_hour[hour]["total"] += 1
        by_hour[hour]["fraud"] += 1 if r.prediction == 1 else 0

        if r.prediction == 1:
            recent_alerts.append({
                "transaction_id": txn.transaction_id,
                "customer_name": txn.customer_name,
                "amount": txn.amount,
                "location": loc,
                "merchant_name": txn.merchant_name or txn.merchant_category,
                "merchant_category": txn.merchant_category,
                "probability": r.probability,
                "risk_level": r.risk_level,
                "transaction_time": txn.transaction_time.isoformat(),
            })

    recent_alerts = sorted(recent_alerts, key=lambda x: x["transaction_time"], reverse=True)[:10]
    age_group_order = ["18-24", "25-34", "35-44", "45-59", "60+", "Unknown"]

    return AnalyticsResponse(
        total_transactions=total_transactions,
        fraud_detected=fraud_detected,
        fraud_rate=round(fraud_rate, 4),
        total_amount=round(total_amount, 2),
        amount_saved=round(amount_saved, 2),
        avg_fraud_probability=round(avg_prob, 4),
        high_risk_alerts=high_risk_alerts,
        pending_reviews=pending_reviews,
        fraud_over_time=sorted(by_day.values(), key=lambda x: x["date"]),
        fraud_by_category=list(by_category.values()),
        fraud_by_location=list(by_location.values()),
        fraud_vs_legit=[
            {"name": "Legitimate", "value": total_transactions - fraud_detected},
            {"name": "Fraud", "value": fraud_detected},
        ],
        fraud_by_hour=list(by_hour.values()),
        fraud_by_payment_method=list(by_payment_method.values()),
        fraud_by_device=list(by_device.values()),
        fraud_by_age_group=sorted(by_age_group.values(), key=lambda x: age_group_order.index(x["age_group"]) if x["age_group"] in age_group_order else 99),
        recent_alerts=recent_alerts,
    )
