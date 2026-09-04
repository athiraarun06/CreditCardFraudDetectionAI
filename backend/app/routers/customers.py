import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.prediction import Prediction
from app.models.user import User
from app.schemas.schemas import CustomerResponse, CustomerCreateRequest, CustomerUpdateRequest

router = APIRouter(tags=["customers"])


@router.post("/customers", response_model=CustomerResponse)
def create_customer(
    payload: CustomerCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer_id = f"CUST-{uuid.uuid4().hex[:10].upper()}"
    customer = Customer(
        user_id=current_user.id,
        customer_id=customer_id,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        age=payload.age,
        gender=payload.gender,
        risk_profile=payload.risk_profile,
        card_status="Active",
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: str,
    payload: CustomerUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id, Customer.user_id == current_user.id
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id, Customer.user_id == current_user.id
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    db.delete(customer)
    db.commit()
    return {"status": "deleted", "customer_id": customer_id}


@router.get("/customers", response_model=List[CustomerResponse])
def list_customers(
    search: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Customer).filter(Customer.user_id == current_user.id)
    if search:
        like = f"%{search}%"
        q = q.filter((Customer.name.ilike(like)) | (Customer.email.ilike(like)) | (Customer.customer_id.ilike(like)))
    return q.order_by(Customer.created_at.desc()).limit(limit).all()


@router.get("/customers/{customer_id}")
def get_customer_profile(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id, Customer.user_id == current_user.id
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    txns = (
        db.query(Transaction, Prediction.prediction, Prediction.probability, Prediction.risk_level)
        .outerjoin(Prediction, Transaction.transaction_id == Prediction.transaction_id)
        .filter(Transaction.customer_id == customer_id, Transaction.user_id == current_user.id)
        .order_by(Transaction.transaction_time.desc())
        .all()
    )

    by_month = {}
    by_merchant = {}
    fraud_history = []
    for t, pred, prob, risk in txns:
        month = t.transaction_time.strftime("%Y-%m")
        by_month.setdefault(month, {"month": month, "total": 0.0, "count": 0})
        by_month[month]["total"] += t.amount
        by_month[month]["count"] += 1

        merch = t.merchant_name or t.merchant_category
        by_merchant.setdefault(merch, {"merchant": merch, "total": 0.0, "count": 0})
        by_merchant[merch]["total"] += t.amount
        by_merchant[merch]["count"] += 1

        if pred == 1:
            fraud_history.append({
                "transaction_id": t.transaction_id,
                "amount": t.amount,
                "merchant_name": merch,
                "probability": prob,
                "risk_level": risk,
                "transaction_time": t.transaction_time.isoformat(),
            })

    return {
        "customer": {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "age": customer.age,
            "gender": customer.gender,
            "risk_profile": customer.risk_profile,
            "avg_transaction_amount": customer.avg_transaction_amount,
            "total_transactions": customer.total_transactions,
        },
        "monthly_spending": sorted(by_month.values(), key=lambda x: x["month"]),
        "merchant_breakdown": sorted(by_merchant.values(), key=lambda x: -x["total"])[:10],
        "fraud_history": fraud_history,
        "recent_transactions": [
            {
                "transaction_id": t.transaction_id,
                "amount": t.amount,
                "merchant_name": t.merchant_name or t.merchant_category,
                "transaction_time": t.transaction_time.isoformat(),
                "prediction": pred,
                "risk_level": risk,
            }
            for t, pred, prob, risk in txns[:20]
        ],
    }
