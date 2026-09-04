import io
import uuid
import logging
from datetime import datetime
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.schemas import TransactionInput
from app.ml.predict import predict as run_prediction
from app.routers.predict import _upsert_customer, _upsert_merchant
from app.models.transaction import Transaction
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.user import User

router = APIRouter(tags=["predict"])
logger = logging.getLogger("fraud_detection")

REQUIRED_COLUMNS = [
    "amount", "merchant_category", "customer_age", "payment_method", "customer_name", "merchant_name",
]


@router.post("/predict-batch")
async def predict_batch(
    file: UploadFile = File(...),
    threshold: float = 0.7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    raw = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"CSV is missing required columns: {missing}")

    if len(df) > 2000:
        raise HTTPException(status_code=400, detail="Batch size limited to 2000 rows per upload.")

    results = []
    errors = []
    for idx, row in df.iterrows():
        try:
            data = {
                "transaction_id": str(row.get("transaction_id") or uuid.uuid4()),
                "customer_name": str(row["customer_name"]),
                "amount": float(row["amount"]),
                "transaction_time": str(row.get("transaction_time") or datetime.utcnow().isoformat()),
                "merchant_name": str(row["merchant_name"]),
                "merchant_category": str(row["merchant_category"]),
                "merchant_city": str(row.get("merchant_city") or row.get("location") or "Mumbai"),
                "merchant_country": str(row.get("merchant_country") or "India"),
                "customer_age": int(row["customer_age"]),
                "location": str(row.get("location") or row.get("merchant_city") or "Mumbai"),
                "payment_method": str(row["payment_method"]),
                "previous_transactions": int(row.get("previous_transactions", 0) or 0),
                "avg_transaction_amount": float(row.get("avg_transaction_amount", row["amount"]) or row["amount"]),
                "threshold": threshold,
            }
            payload = TransactionInput(**data)
            txn_dict = payload.dict()
            txn_dict["transaction_id"] = data["transaction_id"]
            txn_dict["transaction_time"] = data["transaction_time"]

            customer_id = _upsert_customer(db, payload, current_user)
            merchant_id = _upsert_merchant(db, payload)
            result = run_prediction(txn_dict, threshold=threshold)

            txn = Transaction(
                user_id=current_user.id,
                transaction_id=data["transaction_id"],
                customer_id=customer_id,
                customer_name=payload.customer_name,
                amount=payload.amount,
                currency=payload.currency,
                transaction_time=pd.to_datetime(data["transaction_time"]),
                merchant_id=merchant_id,
                merchant_name=payload.merchant_name,
                merchant_category=payload.merchant_category,
                merchant_country=payload.merchant_country,
                merchant_city=payload.merchant_city,
                merchant_risk_score=payload.merchant_risk_score,
                payment_method=payload.payment_method,
                previous_transactions=payload.previous_transactions,
                avg_transaction_amount=payload.avg_transaction_amount,
                customer_age=payload.customer_age,
                location=payload.location,
                fraud_probability=result["probability"],
                fraud_label=result["prediction"],
            )
            db.add(txn)
            db.commit()
            db.add(Prediction(
                user_id=current_user.id,
                transaction_id=data["transaction_id"],
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
                    transaction_id=data["transaction_id"],
                    customer_name=payload.customer_name,
                    amount=payload.amount,
                    merchant_name=payload.merchant_name,
                    location=payload.merchant_city,
                    probability=result["probability"],
                    risk_level=result["risk_level"],
                    status="Pending",
                ))
            results.append({"row": int(idx), "transaction_id": data["transaction_id"], **result})
        except Exception as e:
            db.rollback()  # keep the session usable for subsequent rows after a mid-loop failure
            logger.warning(f"Batch predict failed for row {idx}: {e}")
            errors.append({"row": int(idx), "error": str(e)})

    db.commit()

    fraud_count = sum(1 for r in results if r["prediction"] == 1)
    return {
        "total_rows": len(df),
        "processed": len(results),
        "failed": len(errors),
        "fraud_detected": fraud_count,
        "results": results,
        "errors": errors,
    }
