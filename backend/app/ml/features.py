import math
import pandas as pd
import numpy as np

CATEGORICAL_COLS = [
    "merchant_category", "location", "payment_method",
    "card_type", "device_type", "currency",
]
NUMERIC_COLS = [
    "amount", "customer_age", "previous_transactions", "avg_transaction_amount",
    "transaction_hour", "weekday", "weekend_transaction", "is_night_transaction",
    "amount_difference", "amount_ratio", "high_amount_flag", "location_changed",
    "transaction_frequency",
    "international_transaction", "device_change", "merchant_frequency",
    "customer_velocity_score", "geo_distance", "transaction_velocity",
    "historical_success_rate", "merchant_risk_score", "vpn_flag", "device_trust_flag",
    "txns_last_hour", "txns_last_day", "time_since_last_txn_minutes", "failed_login_attempts",
    "otp_flag",
]

HOME_COUNTRY = "India"


def _safe_col(df, name, default):
    if name not in df.columns:
        df[name] = default
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["transaction_time"] = pd.to_datetime(df["transaction_time"])
    df["transaction_hour"] = df["transaction_time"].dt.hour
    df["weekday"] = df["transaction_time"].dt.weekday
    df["weekend_transaction"] = (df["weekday"] >= 5).astype(int)
    # Night window is 22:00-06:00 (inclusive of 22:00, exclusive of 06:00)
    df["is_night_transaction"] = ((df["transaction_hour"] >= 22) | (df["transaction_hour"] < 6)).astype(int)

    df = _safe_col(df, "avg_transaction_amount", df["amount"])
    df["avg_transaction_amount"] = df["avg_transaction_amount"].replace(0, np.nan).fillna(df["amount"])
    df["amount_difference"] = df["amount"] - df["avg_transaction_amount"]
    df["amount_ratio"] = df["amount"] / df["avg_transaction_amount"].replace(0, 1)
    df["high_amount_flag"] = (df["amount"] > 15000).astype(int)

    if "location" in df.columns:
        most_common_loc = df["location"].mode()[0] if not df["location"].mode().empty else "Mumbai"
        df["location_changed"] = (df["location"] != most_common_loc).astype(int)
    else:
        df["location_changed"] = 0

    df = _safe_col(df, "previous_transactions", 0)
    df["transaction_frequency"] = df["previous_transactions"] / (df["previous_transactions"].max() + 1)

    df = _safe_col(df, "merchant_country", HOME_COUNTRY)
    df["international_transaction"] = (df["merchant_country"].astype(str) != HOME_COUNTRY).astype(int)

    df = _safe_col(df, "is_new_device", False)
    df["device_change"] = df["is_new_device"].astype(bool).astype(int)

    if "merchant_name" in df.columns:
        freq = df["merchant_name"].value_counts(normalize=True)
        df["merchant_frequency"] = df["merchant_name"].map(freq).fillna(0.0)
    else:
        df["merchant_frequency"] = 0.0

    df = _safe_col(df, "txns_last_hour", 0)
    df = _safe_col(df, "txns_last_day", 0)
    df["customer_velocity_score"] = (
        df["txns_last_hour"].astype(float) * 3 + df["txns_last_day"].astype(float)
    ) / 10.0

    df = _safe_col(df, "distance_from_prev_km", 0.0)
    df["geo_distance"] = df["distance_from_prev_km"].astype(float)

    df = _safe_col(df, "time_since_last_txn_minutes", 999.0)
    df["transaction_velocity"] = 1.0 / (df["time_since_last_txn_minutes"].astype(float).clip(lower=1) / 60.0)

    df = _safe_col(df, "failed_login_attempts", 0)
    df["historical_success_rate"] = 1.0 - (
        df["failed_login_attempts"].astype(float) / (df["previous_transactions"].astype(float) + df["failed_login_attempts"].astype(float) + 1)
    )

    df = _safe_col(df, "merchant_risk_score", 0.1)
    df = _safe_col(df, "vpn_detected", False)
    df["vpn_flag"] = df["vpn_detected"].astype(bool).astype(int)

    df = _safe_col(df, "device_trusted", True)
    df["device_trust_flag"] = df["device_trusted"].astype(bool).astype(int)

    df = _safe_col(df, "otp_verified", True)
    df["otp_flag"] = df["otp_verified"].astype(bool).astype(int)

    for col in CATEGORICAL_COLS:
        df = _safe_col(df, col, "unknown")

    return df


def haversine_km(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return 0.0
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
