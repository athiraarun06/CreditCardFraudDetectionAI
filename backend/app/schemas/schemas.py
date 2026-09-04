from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    is_admin: bool

    class Config:
        from_attributes = True


CURRENCIES = ("INR", "USD", "EUR", "GBP")
PAYMENT_METHODS = ("Credit Card", "Debit Card", "UPI", "Wallet", "Net Banking")
CARD_TYPES = ("Visa", "Mastercard", "RuPay", "Amex")
DEVICE_TYPES = ("Android", "iPhone", "Web", "POS Terminal")


class TransactionInput(BaseModel):
    model_config = {"protected_namespaces": ()}

    # Identity (auto-generated if omitted)
    transaction_id: Optional[str] = None
    customer_id: Optional[str] = None

    # Customer
    customer_name: str = Field(min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    customer_age: int = Field(ge=18, le=120)
    gender: Optional[str] = None
    account_created_at: Optional[str] = None
    customer_risk_profile: str = Field(default="Low")

    # Transaction
    amount: float = Field(gt=0, le=10_000_000)
    currency: str = Field(default="INR")
    transaction_time: Optional[str] = None
    merchant_name: str = Field(min_length=1, max_length=120)
    merchant_category: str = Field(min_length=1)
    merchant_country: str = Field(default="India")
    merchant_city: str = Field(default="Mumbai")
    merchant_risk_score: float = Field(default=0.1, ge=0, le=1)

    # Payment
    payment_method: str = Field(min_length=1)
    card_type: Optional[str] = None
    card_last4: Optional[str] = Field(default=None, min_length=0, max_length=4)
    device_type: Optional[str] = None
    operating_system: Optional[str] = None
    browser: Optional[str] = None

    # Device & network
    ip_address: Optional[str] = None
    device_id: Optional[str] = None
    device_trusted: bool = True
    vpn_detected: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_from_prev_km: float = Field(default=0.0, ge=0)

    # Behaviour
    previous_transactions: int = Field(default=0, ge=0)
    avg_transaction_amount: float = Field(default=0.0, ge=0)
    time_since_last_txn_minutes: float = Field(default=999.0, ge=0)
    txns_last_hour: int = Field(default=0, ge=0)
    txns_last_day: int = Field(default=0, ge=0)
    is_new_merchant: bool = False
    is_new_device: bool = False
    is_new_location: bool = False
    failed_login_attempts: int = Field(default=0, ge=0)
    otp_verified: bool = True

    # Legacy/compat field used by the business-schema ML pipeline
    location: Optional[str] = None

    threshold: float = Field(default=0.7, ge=0, le=1)


class FeatureContribution(BaseModel):
    feature: str
    impact: float


class TriggeredRule(BaseModel):
    rule: str
    detail: str
    severity: str


class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    transaction_id: str
    probability: float
    ml_probability: float
    rule_score: float
    prediction: int
    threshold: float
    risk_level: str
    confidence: float
    top_features: List[FeatureContribution]
    triggered_rules: List[TriggeredRule]
    recommended_action: str
    explanation: str
    model_used: str
    transaction_time: str


class TransactionRecord(BaseModel):
    id: int
    transaction_id: str
    customer_name: Optional[str] = None
    amount: float
    currency: Optional[str] = "INR"
    transaction_time: datetime
    merchant_name: Optional[str] = None
    merchant_category: str
    merchant_city: Optional[str] = None
    payment_method: str
    prediction: Optional[int] = None
    probability: Optional[float] = None
    risk_level: Optional[str] = None

    class Config:
        from_attributes = True


class PaginatedTransactions(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[TransactionRecord]


class AnalyticsResponse(BaseModel):
    total_transactions: int
    fraud_detected: int
    fraud_rate: float
    total_amount: float
    amount_saved: float
    avg_fraud_probability: float
    high_risk_alerts: int = 0
    pending_reviews: int = 0
    fraud_over_time: List[Any]
    fraud_by_category: List[Any]
    fraud_by_location: List[Any]
    fraud_vs_legit: List[Any]
    fraud_by_hour: List[Any] = []
    fraud_by_payment_method: List[Any] = []
    fraud_by_device: List[Any] = []
    fraud_by_age_group: List[Any] = []
    recent_alerts: List[Any] = []


class ModelMetricsResponse(BaseModel):
    best_model: str
    results: dict


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float


class AlertUpdateRequest(BaseModel):
    status: str = Field(pattern="^(Approved|Blocked|Reviewed|Frozen|Pending)$")


class AlertResponse(BaseModel):
    id: int
    transaction_id: str
    customer_name: Optional[str] = None
    amount: float
    merchant_name: Optional[str] = None
    location: Optional[str] = None
    probability: float
    risk_level: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerResponse(BaseModel):
    id: int
    customer_id: str
    name: str
    email: str
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    risk_profile: str
    avg_transaction_amount: float
    total_transactions: int
    card_status: str = "Active"

    class Config:
        from_attributes = True


class CustomerCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    phone: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=120)
    gender: Optional[str] = None
    risk_profile: str = Field(default="Low", pattern="^(Low|Medium|High)$")


class CustomerUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=120)
    gender: Optional[str] = None
    risk_profile: Optional[str] = Field(default=None, pattern="^(Low|Medium|High)$")
    card_status: Optional[str] = Field(default=None, pattern="^(Active|Blocked)$")


class UserProfileResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    total_transactions: int
    fraud_detected: int
