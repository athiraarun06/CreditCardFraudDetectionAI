import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse, UserProfileResponse

router = APIRouter(tags=["auth"])
logger = logging.getLogger("fraud_detection")


@router.post("/register", response_model=UserResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    try:
        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    except Exception as e:
        db.rollback()
        logger.exception(f"Registration failed for {payload.email}: {e}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = create_access_token({"sub": user.email})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserProfileResponse)
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).count()
    fraud_detected = db.query(Transaction).filter(
        Transaction.user_id == current_user.id, Transaction.fraud_label == 1
    ).count()
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        total_transactions=total_transactions,
        fraud_detected=fraud_detected,
    )
