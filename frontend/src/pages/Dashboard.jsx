import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { LineChart, Line, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import api from "../lib/api.js";
import { useToast } from "../lib/toast.jsx";
import { formatINR } from "../lib/currency.js";
import Card from "../components/ui/Card.jsx";
import KpiCard from "../components/ui/KpiCard.jsx";
import Badge from "../components/ui/Badge.jsx";
import Button from "../components/ui/Button.jsx";
import { SkeletonCard } from "../components/ui/Skeleton.jsx";

const COLORS = ["#7c3aed", "#ef4444"];

export default function Dashboard() {
  const toast = useToast();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [generating, setGenerating] = useState(false);

  const load = () => {
    api.get("/analytics").then((res) => setData(res.data)).catch((err) => setError(err.response?.data?.detail || "Failed to load analytics. Is the backend running?"));
  };

  useEffect(() => { load(); }, []);

  const generateDemoData = async () => {
    setGenerating(true);
    try {
      const res = await api.post("/demo/generate", null, { params: { count: 70 } });
      toast.success(`Generated ${res.data.created} demo transactions (${res.data.flagged_high_risk} flagged as high risk).`);
      load();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to generate demo transactions.");
    } finally {
      setGenerating(false);
    }
  };

  if (error) {
    return (
      <Card className="text-center">
        <p className="text-red-400">{error}</p>
      </Card>
    );
  }

  if (!data) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Fraud Operations Dashboard</h1>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 7 }).map((_, i) => <SkeletonCard key={i} lines={1} />)}
        </div>
        <SkeletonCard lines={6} />
      </div>
    );
  }

  if (data.total_transactions === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Fraud Operations Dashboard</h1>
        <Card className="flex flex-col items-center gap-3 py-16 text-center">
          <div className="text-5xl">📊</div>
          <p className="text-lg font-semibold">No transactions yet</p>
          <p className="max-w-sm text-sm text-white/50">
            Head to <Link to="/predict" className="text-accent1 hover:underline">Predict</Link> and score your
            first transaction, or generate sample data below — this dashboard fills in with live
            data as predictions come in. This data is private to your account only.
          </p>
          <Button onClick={generateDemoData} disabled={generating}>
            {generating ? "Generating..." : "Generate Demo Transactions"}
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">Fraud Operations Dashboard</h1>
        <Button variant="ghost" onClick={generateDemoData} disabled={generating}>
          {generating ? "Generating..." : "+ Generate Demo Transactions"}
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard label="Total Transactions" value={data.total_transactions} gradient />
        <KpiCard label="Total Fraud" value={data.fraud_detected} />
        <KpiCard label="Fraud Rate" value={`${(data.fraud_rate * 100).toFixed(2)}%`} />
        <KpiCard label="Amount Prevented" value={formatINR(data.amount_saved, { decimals: false })} />
        <KpiCard label="Avg Fraud Probability" value={`${(data.avg_fraud_probability * 100).toFixed(1)}%`} />
        <KpiCard label="High Risk Alerts" value={data.high_risk_alerts} />
        <KpiCard label="Pending Manual Reviews" value={data.pending_reviews} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <h2 className="mb-4 font-semibold">Fraud Trend (Transactions & Fraud Over Time)</h2>
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

        <Card>
          <h2 className="mb-4 font-semibold">Fraud vs Legitimate</h2>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={data.fraud_vs_legit} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={4}>
                {data.fraud_vs_legit.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "#0a0a12", border: "1px solid rgba(255,255,255,0.1)" }} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="mb-4 font-semibold">Fraud by Merchant Category</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.fraud_by_category}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="category" stroke="rgba(255,255,255,0.4)" fontSize={11} />
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
              <XAxis dataKey="payment_method" stroke="rgba(255,255,255,0.4)" fontSize={11} />
              <YAxis stroke="rgba(255,255,255,0.4)" fontSize={12} />
              <Tooltip contentStyle={{ background: "#0a0a12", border: "1px solid rgba(255,255,255,0.1)" }} />
              <Legend />
              <Bar dataKey="total" fill="#2563eb" radius={[6, 6, 0, 0]} name="Total" />
              <Bar dataKey="fraud" fill="#ef4444" radius={[6, 6, 0, 0]} name="Fraud" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="mb-4 font-semibold">Fraud by Device</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data.fraud_by_device}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="device" stroke="rgba(255,255,255,0.4)" fontSize={11} />
              <YAxis stroke="rgba(255,255,255,0.4)" fontSize={12} />
              <Tooltip contentStyle={{ background: "#0a0a12", border: "1px solid rgba(255,255,255,0.1)" }} />
              <Bar dataKey="fraud" fill="#ef4444" radius={[6, 6, 0, 0]} name="Fraud" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h2 className="mb-4 font-semibold">Fraud by Hour of Day</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data.fraud_by_hour}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="hour" stroke="rgba(255,255,255,0.4)" fontSize={11} />
              <YAxis stroke="rgba(255,255,255,0.4)" fontSize={12} />
              <Tooltip contentStyle={{ background: "#0a0a12", border: "1px solid rgba(255,255,255,0.1)" }} />
              <Bar dataKey="fraud" fill="#ef4444" radius={[6, 6, 0, 0]} name="Fraud" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="mb-4 font-semibold">Fraud by Customer Age Group</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data.fraud_by_age_group}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="age_group" stroke="rgba(255,255,255,0.4)" fontSize={11} />
              <YAxis stroke="rgba(255,255,255,0.4)" fontSize={12} />
              <Tooltip contentStyle={{ background: "#0a0a12", border: "1px solid rgba(255,255,255,0.1)" }} />
              <Legend />
              <Bar dataKey="total" fill="#2563eb" radius={[6, 6, 0, 0]} name="Total" />
              <Bar dataKey="fraud" fill="#ef4444" radius={[6, 6, 0, 0]} name="Fraud" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h2 className="mb-4 font-semibold">Fraud by Location</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data.fraud_by_location}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="location" stroke="rgba(255,255,255,0.4)" fontSize={11} />
              <YAxis stroke="rgba(255,255,255,0.4)" fontSize={12} />
              <Tooltip contentStyle={{ background: "#0a0a12", border: "1px solid rgba(255,255,255,0.1)" }} />
              <Legend />
              <Bar dataKey="total" fill="#2563eb" radius={[6, 6, 0, 0]} name="Total" />
              <Bar dataKey="fraud" fill="#ef4444" radius={[6, 6, 0, 0]} name="Fraud" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-semibold">Recent Suspicious Transactions</h2>
          <Link to="/alerts" className="text-sm text-accent1 hover:underline">View Alert Center →</Link>
        </div>
        {data.recent_alerts.length === 0 ? (
          <p className="text-sm text-white/40">No fraud alerts yet.</p>
        ) : (
          <div className="space-y-2">
            {data.recent_alerts.map((a) => (
              <div key={a.transaction_id} className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-white/5 px-4 py-2">
                <span className="font-mono text-xs text-white/50">{a.transaction_id.slice(0, 14)}...</span>
                <span className="text-sm text-white/70">{a.customer_name}</span>
                <span className="text-sm text-white/70">{formatINR(a.amount)}</span>
                <span className="text-sm text-white/50">{a.merchant_name} · {a.location}</span>
                <Badge tone="fraud">{a.risk_level} · {(a.probability * 100).toFixed(1)}%</Badge>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
