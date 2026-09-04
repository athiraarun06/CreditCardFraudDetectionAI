"""
Combines the ML fraud probability with a business rule engine, since real fraud systems
never rely on a model alone — hard rules catch known patterns instantly and let compliance/
risk teams update behavior without retraining a model.
"""

CRITICAL_AMOUNT_INR = 100_000


def evaluate_rules(txn: dict) -> tuple[float, list[dict]]:
    """Returns (rule_score in [0,1], list of triggered rule descriptions)."""
    triggered = []
    score = 0.0

    amount = float(txn.get("amount", 0))
    currency = txn.get("currency", "INR")
    amount_inr = amount * {"INR": 1, "USD": 83, "EUR": 90, "GBP": 105}.get(currency, 1)

    is_new_device = bool(txn.get("is_new_device", False))
    is_new_location = bool(txn.get("is_new_location", False))
    is_new_merchant = bool(txn.get("is_new_merchant", False))
    txns_last_hour = int(txn.get("txns_last_hour", 0))
    merchant_risk_score = float(txn.get("merchant_risk_score", 0.1))
    vpn_detected = bool(txn.get("vpn_detected", False))
    device_trusted = bool(txn.get("device_trusted", True))
    otp_verified = bool(txn.get("otp_verified", True))
    failed_login_attempts = int(txn.get("failed_login_attempts", 0))
    distance_km = float(txn.get("distance_from_prev_km", 0))
    time_since_last = float(txn.get("time_since_last_txn_minutes", 999))

    if amount_inr > CRITICAL_AMOUNT_INR and is_new_device and is_new_location:
        score += 0.6
        triggered.append({"rule": "high_value_new_device_new_location",
                           "detail": f"Amount ₹{amount_inr:,.0f} exceeds ₹1,00,000 with a new device and new location.",
                           "severity": "critical"})

    if txns_last_hour >= 5:
        score += 0.35
        triggered.append({"rule": "velocity_burst",
                           "detail": f"{txns_last_hour} transactions within the last hour.",
                           "severity": "high"})

    if merchant_risk_score > 0.8:
        score += 0.25
        triggered.append({"rule": "high_risk_merchant",
                           "detail": f"Merchant risk score {merchant_risk_score:.2f} is above 0.8.",
                           "severity": "medium"})

    if vpn_detected:
        score += 0.2
        triggered.append({"rule": "vpn_proxy_detected",
                           "detail": "Transaction originated through a VPN/proxy.",
                           "severity": "medium"})

    if not device_trusted and is_new_device:
        score += 0.15
        triggered.append({"rule": "untrusted_new_device",
                           "detail": "Device is new and not marked as trusted.",
                           "severity": "medium"})

    if not otp_verified:
        score += 0.2
        triggered.append({"rule": "otp_not_verified",
                           "detail": "OTP verification failed or was skipped.",
                           "severity": "high"})

    if failed_login_attempts >= 3:
        score += 0.2
        triggered.append({"rule": "repeated_failed_logins",
                           "detail": f"{failed_login_attempts} failed login attempts before this transaction.",
                           "severity": "high"})

    if distance_km > 500 and time_since_last < 60:
        score += 0.3
        triggered.append({"rule": "impossible_travel",
                           "detail": f"{distance_km:.0f}km from the previous transaction in under an hour.",
                           "severity": "critical"})

    if is_new_merchant and amount_inr > 20000:
        score += 0.1
        triggered.append({"rule": "new_merchant_high_value",
                           "detail": "First transaction with this merchant is unusually large.",
                           "severity": "low"})

    return min(score, 1.0), triggered


def combine_scores(ml_probability: float, rule_score: float) -> float:
    """Weighted blend — rules act as a floor/boost rather than fully overriding the model."""
    combined = 1 - (1 - ml_probability) * (1 - rule_score)
    return round(min(combined, 1.0), 6)


def risk_level_from_probability(prob: float) -> str:
    pct = prob * 100
    if pct >= 75:
        return "Critical"
    if pct >= 50:
        return "High"
    if pct >= 20:
        return "Medium"
    return "Low"


def recommended_action(prob: float, triggered_rules: list[dict]) -> str:
    pct = prob * 100
    has_critical_rule = any(r["severity"] == "critical" for r in triggered_rules)

    if has_critical_rule or pct >= 90:
        return "Freeze Account (Critical)"
    if pct >= 75:
        return "Decline Transaction"
    if pct >= 50:
        return "Hold for Manual Review"
    if pct >= 20:
        return "Send OTP Verification"
    return "Approve Automatically"


RISK_HEADERS = {
    "Low": "Transaction approved automatically",
    "Medium": "OTP verification recommended",
    "High": "Flagged for manual review",
    "Critical": "Transaction blocked / account frozen",
}


def _fact_reasons(txn: dict, df_row) -> list[str]:
    """Ground-truth reasons pulled directly from the actual transaction fields (not SHAP), used
    to corroborate — never contradict — what the SHAP-driven reasons already say."""
    reasons = []

    avg_amt = float(txn.get("avg_transaction_amount") or 0)
    amount = float(txn.get("amount", 0))
    if avg_amt > 0 and amount / avg_amt >= 3:
        reasons.append(f"amount is {amount / avg_amt:.0f}x the customer's average")

    if txn.get("is_new_location"):
        reasons.append("a new/unrecognized location was detected")
    if txn.get("is_new_device"):
        reasons.append("the transaction came from a new, unrecognized device")

    # Use the SAME engineered hour/night flag the model actually saw (df_row), never a
    # re-parsed timestamp, so this reason can never disagree with is_night_transaction.
    try:
        if df_row is not None and "is_night_transaction" in df_row.columns:
            is_night = bool(df_row["is_night_transaction"].iloc[0])
            hour = int(df_row["transaction_hour"].iloc[0])
            if is_night:
                reasons.append(f"it occurred at {hour:02d}:xx, during the 22:00-06:00 night window")
    except Exception:
        pass

    if txn.get("vpn_detected"):
        reasons.append("a VPN/proxy was detected")

    return reasons


def build_explanation(
    txn: dict,
    df_row,
    prediction: int,
    risk_level: str,
    recommended_action_text: str,
    top_features: list[dict],
    triggered_rules: list[dict],
) -> str:
    """
    Builds a plain-English explanation whose header always matches the actual prediction/risk
    level (never says "flagged" for a legitimate transaction), and whose reasons come primarily
    from the top POSITIVE-impact SHAP features that are actually active for this transaction
    (i.e. reflect the customer's real input), corroborated by fact-based checks and any
    triggered business rules.
    """
    header = RISK_HEADERS.get(risk_level, recommended_action_text)

    if prediction == 0 and risk_level == "Low":
        return (
            f"{header} — this transaction is consistent with the customer's normal behavior "
            f"and no significant risk signals were detected."
        )

    reasons = []

    # Rank-order reasons by the model's own confidence: top positive (fraud-pushing) SHAP
    # features that are actually active for this transaction, translated to plain English.
    positive_active = [f for f in top_features if f["impact"] > 0]
    for f in positive_active[:3]:
        reasons.append(f["feature"])

    reasons.extend(_fact_reasons(txn, df_row))

    for r in triggered_rules[:2]:
        reasons.append(r["detail"].rstrip("."))

    # De-duplicate while preserving order
    seen = set()
    unique_reasons = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            unique_reasons.append(r)

    if not unique_reasons:
        return f"{header} — the model's risk score for this transaction was {risk_level.lower()}."

    return f"{header}. Contributing factors: " + "; ".join(unique_reasons[:4]) + "."
