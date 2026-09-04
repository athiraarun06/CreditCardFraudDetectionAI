from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    transaction_id = Column(String, ForeignKey("transactions.transaction_id"), nullable=False, index=True)
    customer_name = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    merchant_name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    probability = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False, index=True)  # High / Critical
    status = Column(String, default="Pending", index=True)  # Pending / Approved / Blocked / Reviewed / Frozen
    action_taken_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
