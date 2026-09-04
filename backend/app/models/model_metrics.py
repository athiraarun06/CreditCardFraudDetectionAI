from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class ModelMetrics(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1 = Column(Float)
    roc_auc = Column(Float)
    pr_auc = Column(Float)
    extra = Column(JSON, nullable=True)
    trained_at = Column(DateTime(timezone=True), server_default=func.now())
