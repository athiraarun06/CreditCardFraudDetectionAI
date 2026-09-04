"""
30 realistic test transactions covering the business scenarios required for the internship
submission — run against a live backend to sanity-check that predicted fraud probabilities make
business sense (low for routine purchases, high for classic fraud patterns).

Usage (from backend/, with the API running on http://localhost:8000):
    python tests/generate_test_transactions.py
"""
import json
import os
import sys
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")
EMAIL = "test-runner@example.com"
PASSWORD = "testpass123"

BASE = {
    "customer_name": "Test Customer", "email": "test@example.com", "customer_age": 32,
    "gender": "Male", "customer_risk_profile": "Low",
    "currency": "INR", "merchant_country": "India", "merchant_city": "Mumbai",
    "merchant_risk_score": 0.1, "payment_method": "Credit Card", "card_type": "Visa",
    "card_last4": "1234", "device_type": "Android", "operating_system": "Android 14",
    "browser": "Chrome", "device_trusted": True, "vpn_detected": False,
    "latitude": 19.076, "longitude": 72.8777, "distance_from_prev_km": 0,
    "previous_transactions": 40, "avg_transaction_amount": 1500,
    "time_since_last_txn_minutes": 180, "txns_last_hour": 1, "txns_last_day": 2,
    "is_new_merchant": False, "is_new_device": False, "is_new_location": False,
    "failed_login_attempts": 0, "otp_verified": True, "threshold": 0.7,
}


def txn(name, expected, **overrides):
    data = {**BASE, **overrides}
    data["_name"] = name
    data["_expected"] = expected
    return data


TEST_CASES = [
    txn("Normal grocery purchase", "low", amount=850, merchant_name="Big Bazaar", merchant_category="grocery", payment_method="UPI"),
    txn("Petrol payment", "low", amount=2000, merchant_name="Indian Oil", merchant_category="fuel", payment_method="Debit Card"),
    txn("Netflix subscription", "low", amount=649, merchant_name="Netflix", merchant_category="entertainment", payment_method="Credit Card", is_new_merchant=False),
    txn("International online purchase (known merchant)", "medium", amount=8000, merchant_name="Amazon Global", merchant_category="online", merchant_country="USA", is_new_location=True),
    txn("Airport travel booking", "medium", amount=35000, merchant_name="MakeMyTrip", merchant_category="travel", is_new_merchant=True),
    txn("ATM-style high withdrawal", "medium", amount=25000, merchant_name="HDFC ATM", merchant_category="other", payment_method="Debit Card"),
    txn("Luxury shopping spree", "high", amount=180000, merchant_name="Louis Vuitton", merchant_category="electronics", merchant_risk_score=0.4, is_new_merchant=True),
    txn("Multiple rapid UPI payments", "high", amount=5000, merchant_name="Local Store", merchant_category="other", payment_method="UPI", txns_last_hour=7, txns_last_day=12),
    txn("New device login + purchase", "medium", amount=3000, merchant_name="Flipkart", merchant_category="online", is_new_device=True, device_trusted=False),
    txn("VPN transaction", "medium", amount=4500, merchant_name="Steam", merchant_category="online", vpn_detected=True),
    txn("Midnight foreign transaction", "high", amount=95000, merchant_name="Unknown Retailer", merchant_category="electronics",
        merchant_country="Russia", merchant_city="Moscow", transaction_time="2026-01-01T02:15:00", is_new_location=True, is_new_device=True),
    txn("Routine dining out", "low", amount=1200, merchant_name="Domino's Pizza", merchant_category="dining", payment_method="UPI"),
    txn("Coffee shop tap-to-pay", "low", amount=250, merchant_name="Starbucks", merchant_category="dining", payment_method="Wallet"),
    txn("Monthly electricity bill", "low", amount=3200, merchant_name="Tata Power", merchant_category="other", payment_method="Net Banking"),
    txn("Mobile recharge", "low", amount=399, merchant_name="Jio", merchant_category="other", payment_method="UPI"),
    txn("New merchant electronics purchase, high value", "high", amount=120000, merchant_name="Cheap Gadgets Co", merchant_category="electronics",
        is_new_merchant=True, is_new_device=True, is_new_location=True, merchant_risk_score=0.85),
    txn("Failed OTP + high amount", "critical", amount=200000, merchant_name="QuickCash Loans", merchant_category="other",
        otp_verified=False, failed_login_attempts=5, is_new_device=True, is_new_location=True),
    txn("Impossible travel (2 cities in minutes)", "high", amount=15000, merchant_name="City Mart", merchant_category="grocery",
        distance_from_prev_km=1800, time_since_last_txn_minutes=20),
    txn("Regular UPI transfer to known merchant", "low", amount=500, merchant_name="Local Kirana", merchant_category="grocery", payment_method="UPI"),
    txn("Weekend entertainment outing", "low", amount=1800, merchant_name="PVR Cinemas", merchant_category="entertainment"),
    txn("High-risk merchant, average amount", "medium", amount=4000, merchant_name="Offshore Betting Co", merchant_category="online", merchant_risk_score=0.9),
    txn("Senior citizen normal purchase", "low", amount=1100, merchant_name="Apollo Pharmacy", merchant_category="grocery", customer_age=68),
    txn("Young adult first credit card use", "medium", amount=6000, merchant_name="Zara", merchant_category="other",
        customer_age=19, previous_transactions=1, avg_transaction_amount=500, is_new_merchant=True),
    txn("Wallet top-up", "low", amount=1000, merchant_name="Paytm", merchant_category="other", payment_method="Wallet"),
    txn("Fuel purchase abroad while traveling", "medium", amount=3000, merchant_name="Shell", merchant_category="fuel",
        merchant_country="UAE", merchant_city="Dubai", is_new_location=True),
    txn("Large but explainable purchase (matches avg)", "low", amount=5000, merchant_name="Reliance Digital", merchant_category="electronics", avg_transaction_amount=4800),
    txn("Suspicious velocity burst on new device", "critical", amount=45000, merchant_name="FastCash Exchange", merchant_category="other",
        txns_last_hour=9, is_new_device=True, vpn_detected=True, otp_verified=False),
    txn("Standard hotel booking", "low", amount=12000, merchant_name="Taj Hotels", merchant_category="travel"),
    txn("Subscription renewal", "low", amount=199, merchant_name="Spotify", merchant_category="entertainment"),
    txn("Cross-border wire-style large transfer", "critical", amount=500000, merchant_name="Unknown Forex", merchant_category="other",
        merchant_country="China", is_new_merchant=True, is_new_device=True, is_new_location=True, merchant_risk_score=0.95, otp_verified=False),
]


def main():
    session = requests.Session()
    try:
        session.post(f"{API_URL}/register", json={"email": EMAIL, "password": PASSWORD, "full_name": "Test Runner"})
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to {API_URL}. Is the backend running?")
        sys.exit(1)

    login = session.post(f"{API_URL}/login", json={"email": EMAIL, "password": PASSWORD})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    results = []
    for case in TEST_CASES:
        name, expected = case.pop("_name"), case.pop("_expected")
        resp = session.post(f"{API_URL}/predict", json=case, headers=headers)
        if resp.status_code != 200:
            results.append({"name": name, "expected": expected, "error": resp.text})
            continue
        data = resp.json()
        results.append({
            "name": name,
            "expected": expected,
            "probability": round(data["probability"] * 100, 1),
            "risk_level": data["risk_level"],
            "recommended_action": data["recommended_action"],
        })

    print(f"\n{'Scenario':<55} {'Expected':<10} {'Prob %':<8} {'Risk':<10} Action")
    print("-" * 120)
    for r in results:
        if "error" in r:
            print(f"{r['name']:<55} {r['expected']:<10} ERROR: {r['error'][:40]}")
            continue
        print(f"{r['name']:<55} {r['expected']:<10} {r['probability']:<8} {r['risk_level']:<10} {r['recommended_action']}")

    out_path = os.path.join(os.path.dirname(__file__), "test_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved detailed results to {out_path}")


if __name__ == "__main__":
    main()
