from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    transaction_id = Column(String, ForeignKey("transactions.transaction_id"), nullable=False, index=True)
    probability = Column(Float, nullable=False)
    ml_probability = Column(Float, nullable=True)
    rule_score = Column(Float, nullable=True)
    prediction = Column(Integer, nullable=False)
    threshold = Column(Float, default=0.7)
    risk_level = Column(String, nullable=True)  # Low / Medium / High / Critical
    confidence = Column(Float, nullable=True)
    model_used = Column(String, nullable=True)
    top_features = Column(JSON, nullable=True)
    triggered_rules = Column(JSON, nullable=True)
    recommended_action = Column(String, nullable=True)
    explanation = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
