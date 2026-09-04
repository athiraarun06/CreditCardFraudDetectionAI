from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    risk_score = Column(Float, default=0.1)  # 0-1, higher = riskier merchant
    created_at = Column(DateTime(timezone=True), server_default=func.now())
