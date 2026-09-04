import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend, LineChart, Line } from "recharts";
import api from "../lib/api.js";
import { useToast } from "../lib/toast.jsx";
import Card from "../components/ui/Card.jsx";
import Input from "../components/ui/Input.jsx";
import Select from "../components/ui/Select.jsx";
import Button from "../components/ui/Button.jsx";
import { SkeletonCard } from "../components/ui/Skeleton.jsx";
import { MERCHANT_CATEGORIES, CITIES as CITY_LIST, COUNTRIES, PAYMENT_METHODS } from "../lib/demoData.js";
import { formatINR } from "../lib/currency.js";

const CATEGORIES = ["", ...MERCHANT_CATEGORIES];
const CITIES = ["", ...CITY_LIST];
const METHODS = ["", ...PAYMENT_METHODS];
const COUNTRY_OPTIONS = ["", ...COUNTRIES];
const RISK_LEVELS = ["", "Low", "Medium", "High", "Critical"];

export default function Analytics() {
  const toast = useToast();
  const [filters, setFilters] = useState({ start_date: "", end_date: "", merchant_category: "", location: "", payment_method: "", country: "", risk_level: "" });
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setError("");
    setLoading(true);
    try {
      const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
      const res = await api.get("/analytics", { params });
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const update = (k) => (e) => setFilters({ ...filters, [k]: e.target.value });

  const exportCsv = () => {
    if (!data) return;
    const header = ["date", "total", "fraud"];
    const rows = data.fraud_over_time.map((r) => header.map((h) => r[h]).join(","));
    const csv = [header.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "analytics_filtered.csv";
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Filtered analytics exported.");
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Analytics</h1>

      <Card>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Input label="Start Date" type="date" value={filters.start_date} onChange={update("start_date")} />
          <Input label="End Date" type="date" value={filters.end_date} onChange={update("end_date")} />
          <Select label="Merchant Category" options={CATEGORIES} value={filters.merchant_category} onChange={update("merchant_category")} />
          <Select label="Location" options={CITIES} value={filters.location} onChange={update("location")} />
          <Select label="Payment Method" options={METHODS} value={filters.payment_method} onChange={update("payment_method")} />
          <Select label="Country" options={COUNTRY_OPTIONS} value={filters.country} onChange={update("country")} />
          <Select label="Risk Level" options={RISK_LEVELS} value={filters.risk_level} onChange={update("risk_level")} />
          <div className="flex items-end gap-2">
            <Button onClick={load} className="flex-1">Apply</Button>
            <Button variant="ghost" onClick={exportCsv}>Report CSV</Button>
          </div>
        </div>
      </Card>

      {error && <p className="text-red-400">{error}</p>}
      {loading && !data && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} lines={1} />)}
          </div>
          <SkeletonCard lines={6} />
        </div>
      )}
      {data && (
        <>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <Card><p className="text-xs text-white/50">Transactions</p><p className="text-xl font-bold">{data.total_transactions}</p></Card>
            <Card><p className="text-xs text-white/50">Fraud</p><p className="text-xl font-bold text-red-400">{data.fraud_detected}</p></Card>
            <Card><p className="text-xs text-white/50">Fraud Rate</p><p className="text-xl font-bold">{(data.fraud_rate * 100).toFixed(2)}%</p></Card>
            <Card><p className="text-xs text-white/50">Total Amount</p><p className="text-xl font-bold">{formatINR(data.total_amount, { decimals: false })}</p></Card>
          </div>

          <Card>
            <h2 className="mb-4 font-semibold">Fraud by Location</h2>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={data.fraud_by_location}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="location" stroke="rgba(255,255,255,0.4)" fontSize={12} />
                <YAxis stroke="rgba(255,255,255,0.4)" fontSize={12} />
                <Tooltip contentStyle={{ background: "#0a0a12", border: "1px solid rgba(255,255,255,0.1)" }} />
                <Legend />
                <Bar dataKey="total" fill="#2563eb" radius={[6, 6, 0, 0]} name="Total" />
                <Bar dataKey="fraud" fill="#ef4444" radius={[6, 6, 0, 0]} name="Fraud" />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          <Card>
            <h2 className="mb-4 font-semibold">Fraud by Payment Method</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={data.fraud_by_payment_method}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="payment_method" stroke="rgba(255,255,255,0.4)" fontSize={12} />
                <YAxis stroke="rgba(255,255,255,0.4)" fontSize={12} />
                <Tooltip contentStyle={{ background: "#0a0a12", border: "1px solid rgba(255,255,255,0.1)" }} />
                <Legend />
                <Bar dataKey="total" fill="#2563eb" radius={[6, 6, 0, 0]} name="Total" />
                <Bar dataKey="fraud" fill="#ef4444" radius={[6, 6, 0, 0]} name="Fraud" />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          <Card>
            <h2 className="mb-4 font-semibold">Trend Over Time</h2>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={data.fraud_over_time}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="date" stroke="rgba(255,255,255,0.4)" fontSize={12} />
                <YAxis stroke="rgba(255,255,255,0.4)" fontSize={12} />
                <Tooltip contentStyle={{ background: "#0a0a12", border: "1px solid rgba(255,255,255,0.1)" }} />
                <Legend />
                <Line type="monotone" dataKey="total" stroke="#2563eb" strokeWidth={2} dot={false} name="Total" />
                <Line type="monotone" dataKey="fraud" stroke="#ef4444" strokeWidth={2} dot={false} name="Fraud" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </>
      )}
    </div>
  );
}
