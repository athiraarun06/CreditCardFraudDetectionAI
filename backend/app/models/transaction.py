from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)

    # Customer
    customer_id = Column(String, ForeignKey("customers.customer_id"), index=True, nullable=True)
    customer_name = Column(String, nullable=True)

    # Transaction info
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    transaction_time = Column(DateTime, nullable=False, index=True)
    merchant_id = Column(String, ForeignKey("merchants.merchant_id"), index=True, nullable=True)
    merchant_name = Column(String, nullable=True)
    merchant_category = Column(String, nullable=False, index=True)
    merchant_country = Column(String, nullable=True)
    merchant_city = Column(String, nullable=True)
    merchant_risk_score = Column(Float, default=0.1)

    # Payment info
    payment_method = Column(String, nullable=False)
    card_type = Column(String, nullable=True)
    card_last4 = Column(String, nullable=True)
    device_type = Column(String, nullable=True)
    operating_system = Column(String, nullable=True)
    browser = Column(String, nullable=True)

    # Device & network
    ip_address = Column(String, nullable=True)
    device_id = Column(String, nullable=True)
    device_trusted = Column(Boolean, default=True)
    vpn_detected = Column(Boolean, default=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    distance_from_prev_km = Column(Float, default=0.0)

    # Behaviour
    previous_transactions = Column(Integer, default=0)
    avg_transaction_amount = Column(Float, default=0.0)
    time_since_last_txn_minutes = Column(Float, default=0.0)
    txns_last_hour = Column(Integer, default=0)
    txns_last_day = Column(Integer, default=0)
    is_new_merchant = Column(Boolean, default=False)
    is_new_device = Column(Boolean, default=False)
    is_new_location = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    otp_verified = Column(Boolean, default=True)

    # Legacy business-schema fields (kept for backward compatibility with the synthetic dataset)
    customer_age = Column(Integer, nullable=True)
    location = Column(String, nullable=True)

    # Denormalized copy of the latest prediction for this transaction, so list/detail views
    # don't require a join with `predictions` just to show risk at a glance.
    fraud_probability = Column(Float, nullable=True)
    fraud_label = Column(Integer, nullable=True)  # 0 = legitimate, 1 = fraud

    created_at = Column(DateTime(timezone=True), server_default=func.now())
