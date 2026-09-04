import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.transaction import Transaction
from app.models.prediction import Prediction
from app.models.customer import Customer
from app.models.merchant import Merchant
from app.models.alert import Alert
from app.models.user import User
from app.schemas.schemas import TransactionInput, PredictionResponse
from app.ml.predict import predict as run_prediction

router = APIRouter(tags=["predict"])
logger = logging.getLogger("fraud_detection")


def _upsert_customer(db: Session, payload: TransactionInput, user: User) -> str:
    """
    Finds or creates the customer this transaction belongs to, scoped strictly to `user`.
    A customer_id/email supplied by the client is only reused if it actually belongs to this
    user — never another user's customer, even if the ID is guessed or reused across accounts.
    """
    if payload.customer_id:
        existing = db.query(Customer).filter(
            Customer.customer_id == payload.customer_id, Customer.user_id == user.id
        ).first()
        if existing:
            existing.total_transactions = (existing.total_transactions or 0) + 1
            return existing.customer_id
        # Requested ID doesn't belong to this user (or doesn't exist) — fall through and
        # create a fresh customer under this user rather than silently attaching to someone
        # else's record.

    if payload.email:
        existing = db.query(Customer).filter(
            Customer.email == payload.email, Customer.user_id == user.id
        ).first()
        if existing:
            existing.total_transactions = (existing.total_transactions or 0) + 1
            return existing.customer_id

    customer_id = payload.customer_id or f"CUST-{uuid.uuid4().hex[:10].upper()}"
    # Guarantee global uniqueness of the generated/reused ID even across users, since it's a
    # unique DB column.
    if db.query(Customer).filter(Customer.customer_id == customer_id).first():
        customer_id = f"CUST-{uuid.uuid4().hex[:10].upper()}"

    customer = Customer(
        user_id=user.id,
        customer_id=customer_id,
        name=payload.customer_name,
        email=payload.email or f"{customer_id.lower()}@unknown.local",
        phone=payload.phone,
        age=payload.customer_age,
        gender=payload.gender,
        account_created_at=datetime.fromisoformat(payload.account_created_at) if payload.account_created_at else None,
        risk_profile=payload.customer_risk_profile,
        avg_transaction_amount=payload.avg_transaction_amount,
        total_transactions=1,
    )
    db.add(customer)
    db.flush()
    return customer.customer_id


def _upsert_merchant(db: Session, payload: TransactionInput) -> str:
    """Merchants are a shared reference catalog (not per-user) — "Amazon" is the same merchant
    regardless of which bank customer is transacting with it."""
    merchant_id = f"MERCH-{abs(hash(payload.merchant_name)) % 100000}"
    existing = db.query(Merchant).filter(Merchant.merchant_id == merchant_id).first()
    if existing:
        return existing.merchant_id

    merchant = Merchant(
        merchant_id=merchant_id,
        name=payload.merchant_name,
        category=payload.merchant_category,
        country=payload.merchant_country,
        city=payload.merchant_city,
        risk_score=payload.merchant_risk_score,
    )
    db.add(merchant)
    db.flush()
    return merchant.merchant_id


@router.post("/predict", response_model=PredictionResponse)
def predict_transaction(
    payload: TransactionInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    txn_id = payload.transaction_id or f"TXN-{uuid.uuid4().hex[:12].upper()}"
    if db.query(Transaction).filter(Transaction.transaction_id == txn_id).first():
        txn_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

    txn_time_str = payload.transaction_time or datetime.utcnow().isoformat()
    txn_time = datetime.fromisoformat(txn_time_str.replace("Z", ""))

    customer_id = _upsert_customer(db, payload, current_user)
    merchant_id = _upsert_merchant(db, payload)

    txn_dict = payload.dict()
    txn_dict["transaction_id"] = txn_id
    txn_dict["transaction_time"] = txn_time_str
    txn_dict["location"] = payload.location or payload.merchant_city

    result = run_prediction(txn_dict, threshold=payload.threshold)

    txn = Transaction(
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
        card_type=payload.card_type,
        card_last4=payload.card_last4,
        device_type=payload.device_type,
        operating_system=payload.operating_system,
        browser=payload.browser,
        ip_address=payload.ip_address,
        device_id=payload.device_id,
        device_trusted=payload.device_trusted,
        vpn_detected=payload.vpn_detected,
        latitude=payload.latitude,
        longitude=payload.longitude,
        distance_from_prev_km=payload.distance_from_prev_km,
        previous_transactions=payload.previous_transactions,
        avg_transaction_amount=payload.avg_transaction_amount,
        time_since_last_txn_minutes=payload.time_since_last_txn_minutes,
        txns_last_hour=payload.txns_last_hour,
        txns_last_day=payload.txns_last_day,
        is_new_merchant=payload.is_new_merchant,
        is_new_device=payload.is_new_device,
        is_new_location=payload.is_new_location,
        failed_login_attempts=payload.failed_login_attempts,
        otp_verified=payload.otp_verified,
        customer_age=payload.customer_age,
        location=payload.location or payload.merchant_city,
        fraud_probability=result["probability"],
        fraud_label=result["prediction"],
    )
    db.add(txn)

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

    db.commit()

    return PredictionResponse(transaction_id=txn_id, transaction_time=txn_time_str, **result)
