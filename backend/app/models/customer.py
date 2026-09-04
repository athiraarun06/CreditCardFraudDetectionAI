from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    customer_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, index=True, nullable=False)
    phone = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    account_created_at = Column(DateTime, nullable=True)
    risk_profile = Column(String, default="Low")  # Low / Medium / High
    avg_transaction_amount = Column(Float, default=0.0)
    total_transactions = Column(Integer, default=0)
    card_status = Column(String, default="Active")  # Active / Blocked
    created_at = Column(DateTime(timezone=True), server_default=func.now())
