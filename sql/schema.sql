CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    customer_id VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    phone VARCHAR,
    age INTEGER,
    gender VARCHAR,
    account_created_at TIMESTAMP,
    risk_profile VARCHAR DEFAULT 'Low',
    avg_transaction_amount FLOAT DEFAULT 0,
    total_transactions INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_user ON customers(user_id);

CREATE TABLE IF NOT EXISTS merchants (
    id SERIAL PRIMARY KEY,
    merchant_id VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    country VARCHAR,
    city VARCHAR,
    risk_score FLOAT DEFAULT 0.1,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_merchants_category ON merchants(category);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    transaction_id VARCHAR UNIQUE NOT NULL,
    customer_id VARCHAR REFERENCES customers(customer_id),
    customer_name VARCHAR,
    amount FLOAT NOT NULL,
    currency VARCHAR DEFAULT 'INR',
    transaction_time TIMESTAMP NOT NULL,
    merchant_id VARCHAR REFERENCES merchants(merchant_id),
    merchant_name VARCHAR,
    merchant_category VARCHAR NOT NULL,
    merchant_country VARCHAR,
    merchant_city VARCHAR,
    merchant_risk_score FLOAT DEFAULT 0.1,
    payment_method VARCHAR NOT NULL,
    card_type VARCHAR,
    card_last4 VARCHAR,
    device_type VARCHAR,
    operating_system VARCHAR,
    browser VARCHAR,
    ip_address VARCHAR,
    device_id VARCHAR,
    device_trusted BOOLEAN DEFAULT TRUE,
    vpn_detected BOOLEAN DEFAULT FALSE,
    latitude FLOAT,
    longitude FLOAT,
    distance_from_prev_km FLOAT DEFAULT 0,
    previous_transactions INTEGER DEFAULT 0,
    avg_transaction_amount FLOAT DEFAULT 0,
    time_since_last_txn_minutes FLOAT DEFAULT 0,
    txns_last_hour INTEGER DEFAULT 0,
    txns_last_day INTEGER DEFAULT 0,
    is_new_merchant BOOLEAN DEFAULT FALSE,
    is_new_device BOOLEAN DEFAULT FALSE,
    is_new_location BOOLEAN DEFAULT FALSE,
    failed_login_attempts INTEGER DEFAULT 0,
    otp_verified BOOLEAN DEFAULT TRUE,
    customer_age INTEGER,
    location VARCHAR,
    fraud_probability FLOAT,
    fraud_label INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_transactions_time ON transactions(transaction_time);
CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_merchant ON transactions(merchant_id);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(merchant_category);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    transaction_id VARCHAR REFERENCES transactions(transaction_id),
    probability FLOAT NOT NULL,
    ml_probability FLOAT,
    rule_score FLOAT,
    prediction INTEGER NOT NULL,
    threshold FLOAT DEFAULT 0.7,
    risk_level VARCHAR,
    confidence FLOAT,
    model_used VARCHAR,
    top_features JSONB,
    triggered_rules JSONB,
    recommended_action VARCHAR,
    explanation VARCHAR,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_predictions_txn ON predictions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_predictions_user ON predictions(user_id);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    transaction_id VARCHAR REFERENCES transactions(transaction_id),
    customer_name VARCHAR,
    amount FLOAT NOT NULL,
    merchant_name VARCHAR,
    location VARCHAR,
    probability FLOAT NOT NULL,
    risk_level VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'Pending',
    action_taken_by VARCHAR,
    created_at TIMESTAMPTZ DEFAULT now(),
    resolved_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_risk ON alerts(risk_level);
CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id);

CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR NOT NULL,
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1 FLOAT,
    roc_auc FLOAT,
    pr_auc FLOAT,
    extra JSONB,
    trained_at TIMESTAMPTZ DEFAULT now()
);
