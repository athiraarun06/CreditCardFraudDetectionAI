import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.transaction import Transaction
from app.models.prediction import Prediction
from app.models.user import User
from app.schemas.schemas import PaginatedTransactions, TransactionRecord

router = APIRouter(tags=["transactions"])


@router.get("/transactions", response_model=PaginatedTransactions)
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: Optional[str] = Query(None),
    customer: Optional[str] = Query(None),
    merchant: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="fraud | legit"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Transaction, Prediction.prediction, Prediction.probability, Prediction.risk_level).outerjoin(
        Prediction, Transaction.transaction_id == Prediction.transaction_id
    ).filter(Transaction.user_id == current_user.id)

    if search:
        like = f"%{search}%"
        q = q.filter(
            (Transaction.transaction_id.ilike(like))
            | (Transaction.merchant_city.ilike(like))
            | (Transaction.merchant_category.ilike(like))
            | (Transaction.customer_name.ilike(like))
        )
    if customer:
        q = q.filter(Transaction.customer_name.ilike(f"%{customer}%"))
    if merchant:
        q = q.filter(Transaction.merchant_name.ilike(f"%{merchant}%"))
    if status == "fraud":
        q = q.filter(Prediction.prediction == 1)
    elif status == "legit":
        q = q.filter(Prediction.prediction == 0)
    if start_date:
        q = q.filter(Transaction.transaction_time >= datetime.fromisoformat(start_date))
    if end_date:
        q = q.filter(Transaction.transaction_time <= datetime.fromisoformat(end_date))

    total = q.count()
    rows = (
        q.order_by(Transaction.transaction_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        TransactionRecord(
            id=t.id,
            transaction_id=t.transaction_id,
            customer_name=t.customer_name,
            amount=t.amount,
            currency=t.currency,
            transaction_time=t.transaction_time,
            merchant_name=t.merchant_name,
            merchant_category=t.merchant_category,
            merchant_city=t.merchant_city,
            payment_method=t.payment_method,
            prediction=pred,
            probability=prob,
            risk_level=risk,
        )
        for t, pred, prob, risk in rows
    ]

    return PaginatedTransactions(total=total, page=page, page_size=page_size, items=items)


@router.get("/transactions/{transaction_id}")
def get_transaction_detail(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    txn = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id, Transaction.user_id == current_user.id
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    pred = db.query(Prediction).filter(
        Prediction.transaction_id == transaction_id, Prediction.user_id == current_user.id
    ).order_by(Prediction.id.desc()).first()

    txn_dict = {c.name: getattr(txn, c.name) for c in txn.__table__.columns}
    pred_dict = {c.name: getattr(pred, c.name) for c in pred.__table__.columns} if pred else None

    return {"transaction": txn_dict, "prediction": pred_dict}


@router.post("/transactions")
def create_transaction_record(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Logs a raw transaction without running it through fraud scoring (e.g. for bulk import)."""
    txn_id = payload.get("transaction_id") or f"TXN-{uuid.uuid4().hex[:12].upper()}"
    txn_time = payload.get("transaction_time")
    txn = Transaction(
        user_id=current_user.id,
        transaction_id=txn_id,
        customer_name=payload.get("customer_name"),
        amount=float(payload.get("amount", 0)),
        currency=payload.get("currency", "INR"),
        transaction_time=datetime.fromisoformat(txn_time) if txn_time else datetime.utcnow(),
        merchant_name=payload.get("merchant_name"),
        merchant_category=payload.get("merchant_category", "other"),
        merchant_city=payload.get("merchant_city"),
        merchant_country=payload.get("merchant_country", "India"),
        payment_method=payload.get("payment_method", "Credit Card"),
        customer_age=payload.get("customer_age"),
        location=payload.get("location") or payload.get("merchant_city"),
    )
    db.add(txn)
    db.commit()
    return {"transaction_id": txn_id, "status": "logged"}
