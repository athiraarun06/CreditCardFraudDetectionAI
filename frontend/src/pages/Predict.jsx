import { useRef, useState } from "react";
import { motion } from "framer-motion";
import api from "../lib/api.js";
import { useToast } from "../lib/toast.jsx";
import {
  CURRENCIES, MERCHANT_CATEGORIES, CITIES, COUNTRIES, PAYMENT_METHODS,
  CARD_TYPES, DEVICE_TYPES, OS_LIST, BROWSERS, GENDERS, RISK_PROFILES,
  randomIp, randomDeviceId, nowLocalDatetime,
} from "../lib/demoData.js";
import Card from "../components/ui/Card.jsx";
import Input from "../components/ui/Input.jsx";
import Select from "../components/ui/Select.jsx";
import Button from "../components/ui/Button.jsx";
import Toggle from "../components/ui/Toggle.jsx";
import RiskMeter from "../components/ui/RiskMeter.jsx";
import Badge from "../components/ui/Badge.jsx";

const initial = {
  customer_name: "Rahul Sharma",
  email: "rahul.sharma@example.com",
  phone: "+91 98765 43210",
  customer_age: 34,
  gender: GENDERS[0],
  customer_risk_profile: RISK_PROFILES[0],

  amount: 1500,
  currency: CURRENCIES[0],
  transaction_time: nowLocalDatetime(),
  merchant_name: "Big Bazaar",
  merchant_category: MERCHANT_CATEGORIES[0],
  merchant_country: COUNTRIES[0],
  merchant_city: CITIES[0],
  merchant_risk_score: 0.1,

  payment_method: PAYMENT_METHODS[0],
  card_type: CARD_TYPES[0],
  card_last4: "4242",
  device_type: DEVICE_TYPES[0],
  operating_system: OS_LIST[0],
  browser: BROWSERS[0],

  ip_address: randomIp(),
  device_id: randomDeviceId(),
  device_trusted: true,
  vpn_detected: false,
  latitude: 19.076,
  longitude: 72.8777,
  distance_from_prev_km: 0,

  previous_transactions: 25,
  avg_transaction_amount: 1200,
  time_since_last_txn_minutes: 240,
  txns_last_hour: 1,
  txns_last_day: 3,
  is_new_merchant: false,
  is_new_device: false,
  is_new_location: false,
  failed_login_attempts: 0,
  otp_verified: true,

  threshold: 0.7,
};

const RISK_BADGE_TONE = { Low: "safe", Medium: "neutral", High: "fraud", Critical: "fraud" };

function Section({ title, children }) {
  return (
    <div className="space-y-3 border-t border-white/5 pt-4 first:border-t-0 first:pt-0">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-white/40">{title}</h3>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">{children}</div>
    </div>
  );
}

export default function Predict() {
  const toast = useToast();
  const fileRef = useRef(null);
  const [form, setForm] = useState(initial);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);
  const [batchResult, setBatchResult] = useState(null);

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const updateBool = (k) => (val) => setForm({ ...form, [k]: val });

  const regenerateIds = () => {
    setForm({ ...form, ip_address: randomIp(), device_id: randomDeviceId(), transaction_time: nowLocalDatetime() });
    toast.info("Regenerated transaction ID, IP, and timestamp.");
  };

  const validate = () => {
    if (Number(form.amount) <= 0) return "Amount must be greater than 0.";
    if (Number(form.customer_age) < 18 || Number(form.customer_age) > 120) return "Customer age must be between 18 and 120.";
    if (Number(form.threshold) < 0 || Number(form.threshold) > 1) return "Threshold must be between 0 and 1.";
    return null;
  };

  const submit = async (e) => {
    e.preventDefault();
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      toast.error(validationError);
      return;
    }
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const payload = {
        ...form,
        amount: Number(form.amount),
        customer_age: Number(form.customer_age),
        merchant_risk_score: Number(form.merchant_risk_score),
        latitude: Number(form.latitude),
        longitude: Number(form.longitude),
        distance_from_prev_km: Number(form.distance_from_prev_km),
        previous_transactions: Number(form.previous_transactions),
        avg_transaction_amount: Number(form.avg_transaction_amount),
        time_since_last_txn_minutes: Number(form.time_since_last_txn_minutes),
        txns_last_hour: Number(form.txns_last_hour),
        txns_last_day: Number(form.txns_last_day),
        failed_login_attempts: Number(form.failed_login_attempts),
        threshold: Number(form.threshold),
        // Send the wall-clock value the user actually picked, as-is — converting through
        // `new Date(...).toISOString()` reinterprets it in the browser's local timezone and
        // shifts the hour, which was corrupting is_night_transaction and every hour-based feature.
        transaction_time: `${form.transaction_time}:00`,
      };
      const res = await api.post("/predict", payload);
      setResult(res.data);
      toast[res.data.prediction ? "error" : "success"](
        res.data.prediction ? `Flagged: ${res.data.recommended_action}` : "Transaction looks legitimate."
      );
    } catch (err) {
      const msg = err.response?.data?.detail || "Prediction failed. Please check the backend is running.";
      setError(typeof msg === "string" ? msg : "Validation error — check the form values.");
      toast.error(typeof msg === "string" ? msg : "Validation error.");
    } finally {
      setLoading(false);
    }
  };

  const uploadBatch = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBatchLoading(true);
    setBatchResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await api.post("/predict-batch", fd, { headers: { "Content-Type": "multipart/form-data" } });
      setBatchResult(res.data);
      toast.success(`Processed ${res.data.processed} transactions, ${res.data.fraud_detected} flagged as fraud.`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Batch upload failed.");
    } finally {
      setBatchLoading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Transaction Simulator</h1>
        <Button variant="ghost" onClick={regenerateIds}>🔄 Regenerate IDs</Button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <form onSubmit={submit} className="space-y-5">
            <Section title="Customer Information">
              <Input label="Customer Name" required value={form.customer_name} onChange={update("customer_name")} />
              <Input label="Email" type="email" value={form.email} onChange={update("email")} />
              <Input label="Phone Number" value={form.phone} onChange={update("phone")} />
              <Input label="Age" type="number" min="18" max="120" required value={form.customer_age} onChange={update("customer_age")} />
              <Select label="Gender" options={GENDERS} value={form.gender} onChange={update("gender")} />
              <Select label="Customer Risk Profile" options={RISK_PROFILES} value={form.customer_risk_profile} onChange={update("customer_risk_profile")} />
            </Section>

            <Section title="Transaction Information">
              <Input label={`Amount (${form.currency})`} type="number" step="0.01" min="0.01" required value={form.amount} onChange={update("amount")} />
              <Select label="Currency" options={CURRENCIES} value={form.currency} onChange={update("currency")} />
              <Input label="Timestamp" type="datetime-local" value={form.transaction_time} onChange={update("transaction_time")} className="sm:col-span-2" />
              <Input label="Merchant Name" required value={form.merchant_name} onChange={update("merchant_name")} />
              <Select label="Merchant Category" options={MERCHANT_CATEGORIES} value={form.merchant_category} onChange={update("merchant_category")} />
              <Select label="Merchant Country" options={COUNTRIES} value={form.merchant_country} onChange={update("merchant_country")} />
              <Select label="Merchant City" options={CITIES} value={form.merchant_city} onChange={update("merchant_city")} />
              <Input label="Merchant Risk Score (0-1)" type="number" step="0.05" min="0" max="1" value={form.merchant_risk_score} onChange={update("merchant_risk_score")} />
            </Section>

            <Section title="Payment Information">
              <Select label="Payment Method" options={PAYMENT_METHODS} value={form.payment_method} onChange={update("payment_method")} />
              <Select label="Card Type" options={CARD_TYPES} value={form.card_type} onChange={update("card_type")} />
              <Input label="Last 4 Digits" maxLength={4} value={form.card_last4} onChange={update("card_last4")} />
              <Select label="Device Type" options={DEVICE_TYPES} value={form.device_type} onChange={update("device_type")} />
              <Select label="Operating System" options={OS_LIST} value={form.operating_system} onChange={update("operating_system")} />
              <Select label="Browser" options={BROWSERS} value={form.browser} onChange={update("browser")} />
            </Section>

            <Section title="Device & Network">
              <Input label="IP Address" value={form.ip_address} onChange={update("ip_address")} />
              <Input label="Device ID" value={form.device_id} onChange={update("device_id")} />
              <Input label="Latitude" type="number" step="0.0001" value={form.latitude} onChange={update("latitude")} />
              <Input label="Longitude" type="number" step="0.0001" value={form.longitude} onChange={update("longitude")} />
              <Input label="Distance From Previous Txn (km)" type="number" min="0" value={form.distance_from_prev_km} onChange={update("distance_from_prev_km")} />
              <div />
              <Toggle label="Device Trusted?" checked={form.device_trusted} onChange={updateBool("device_trusted")} />
              <Toggle label="VPN / Proxy Detected?" checked={form.vpn_detected} onChange={updateBool("vpn_detected")} />
            </Section>

            <Section title="Behaviour Features">
              <Input label="Previous Transactions" type="number" min="0" value={form.previous_transactions} onChange={update("previous_transactions")} />
              <Input label="Avg Transaction Amount" type="number" step="0.01" min="0" value={form.avg_transaction_amount} onChange={update("avg_transaction_amount")} />
              <Input label="Time Since Last Txn (min)" type="number" min="0" value={form.time_since_last_txn_minutes} onChange={update("time_since_last_txn_minutes")} />
              <Input label="Txns in Last Hour" type="number" min="0" value={form.txns_last_hour} onChange={update("txns_last_hour")} />
              <Input label="Txns in Last Day" type="number" min="0" value={form.txns_last_day} onChange={update("txns_last_day")} />
              <Input label="Failed Login Attempts" type="number" min="0" value={form.failed_login_attempts} onChange={update("failed_login_attempts")} />
              <Toggle label="New Merchant?" checked={form.is_new_merchant} onChange={updateBool("is_new_merchant")} />
              <Toggle label="New Device?" checked={form.is_new_device} onChange={updateBool("is_new_device")} />
              <Toggle label="New Location?" checked={form.is_new_location} onChange={updateBool("is_new_location")} />
              <Toggle label="OTP Verified?" checked={form.otp_verified} onChange={updateBool("otp_verified")} />
            </Section>

            <Input label="Decision Threshold" type="number" step="0.01" min="0" max="1" value={form.threshold} onChange={update("threshold")} />
            {error && <p className="text-sm text-red-400">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>{loading ? "Analyzing..." : "Score Transaction"}</Button>
          </form>
        </Card>

        <div className="space-y-6">
          <Card className="flex min-h-[420px] flex-col items-center justify-center">
            {!result && <p className="text-white/40">Submit a transaction to see the fraud risk assessment.</p>}
            {result && (
              <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="w-full space-y-4 text-center">
                <RiskMeter probability={result.probability} />
                <div className="flex flex-wrap items-center justify-center gap-2">
                  <Badge tone={result.prediction ? "fraud" : "safe"}>{result.prediction ? "FRAUDULENT" : "LEGITIMATE"}</Badge>
                  <Badge tone={RISK_BADGE_TONE[result.risk_level]}>{result.risk_level} Risk</Badge>
                  <Badge>Confidence {(result.confidence * 100).toFixed(0)}%</Badge>
                </div>

                <div className="grid grid-cols-2 gap-2 text-left text-xs text-white/50">
                  <div className="rounded-lg bg-white/5 px-3 py-2">
                    <p className="text-white/40">Transaction ID</p>
                    <p className="font-mono text-white/80">{result.transaction_id}</p>
                  </div>
                  <div className="rounded-lg bg-white/5 px-3 py-2">
                    <p className="text-white/40">Timestamp</p>
                    <p className="text-white/80">{new Date(result.transaction_time).toLocaleString()}</p>
                  </div>
                </div>

                <div className="rounded-xl bg-white/5 px-4 py-3 text-left">
                  <p className="text-xs uppercase tracking-wide text-white/40">Recommended Action</p>
                  <p className="mt-1 text-sm font-semibold text-white/90">{result.recommended_action}</p>
                </div>

                <div className="rounded-xl bg-white/5 px-4 py-3 text-left">
                  <p className="text-xs uppercase tracking-wide text-white/40">AI Explanation</p>
                  <p className="mt-1 text-sm text-white/70">{result.explanation}</p>
                </div>

                {result.triggered_rules.length > 0 && (
                  <div className="text-left">
                    <h3 className="mb-2 text-sm font-semibold text-white/70">Triggered Rules</h3>
                    <ul className="space-y-1">
                      {result.triggered_rules.map((r) => (
                        <li key={r.rule} className="rounded-lg bg-white/5 px-3 py-1.5 text-xs text-white/60">
                          <span className={`mr-2 rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase ${
                            r.severity === "critical" ? "bg-red-500/20 text-red-300" :
                            r.severity === "high" ? "bg-orange-500/20 text-orange-300" :
                            "bg-yellow-500/20 text-yellow-300"
                          }`}>{r.severity}</span>
                          {r.detail}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="text-left">
                  <h3 className="mb-2 text-sm font-semibold text-white/70">Top Contributing Factors (SHAP)</h3>
                  <ul className="space-y-1">
                    {result.top_features.map((f) => (
                      <li key={f.feature} className="flex justify-between rounded-lg bg-white/5 px-3 py-1.5 text-xs">
                        <span className="text-white/60">{f.feature}</span>
                        <span className={f.impact >= 0 ? "text-red-400" : "text-emerald-400"}>{f.impact.toFixed(3)}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            )}
          </Card>

          <Card>
            <h2 className="mb-2 font-semibold">Batch Prediction (CSV Upload)</h2>
            <p className="mb-4 text-sm text-white/50">
              Columns: customer_name, merchant_name, amount, merchant_category, customer_age, payment_method
              (optional: merchant_city, previous_transactions, avg_transaction_amount). Max 2000 rows.
            </p>
            <input
              ref={fileRef}
              type="file"
              accept=".csv"
              onChange={uploadBatch}
              disabled={batchLoading}
              className="block w-full text-sm text-white/60 file:mr-4 file:rounded-lg file:border-0 file:bg-gradient-fintech file:px-4 file:py-2 file:text-white"
            />
            {batchLoading && <p className="mt-3 text-sm text-white/50">Processing batch...</p>}
            {batchResult && (
              <div className="mt-4 grid grid-cols-3 gap-3 text-center">
                <div className="rounded-xl bg-white/5 p-3"><p className="text-xs text-white/50">Processed</p><p className="text-lg font-bold">{batchResult.processed}</p></div>
                <div className="rounded-xl bg-white/5 p-3"><p className="text-xs text-white/50">Fraud Detected</p><p className="text-lg font-bold text-red-400">{batchResult.fraud_detected}</p></div>
                <div className="rounded-xl bg-white/5 p-3"><p className="text-xs text-white/50">Failed Rows</p><p className="text-lg font-bold">{batchResult.failed}</p></div>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
