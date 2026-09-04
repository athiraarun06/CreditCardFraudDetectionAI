import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, LineChart, Line } from "recharts";
import api from "../lib/api.js";
import { useToast } from "../lib/toast.jsx";
import Card from "../components/ui/Card.jsx";
import Badge from "../components/ui/Badge.jsx";
import { SkeletonCard } from "../components/ui/Skeleton.jsx";
import { formatINR } from "../lib/currency.js";

export default function CustomerProfile() {
  const { customerId } = useParams();
  const toast = useToast();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get(`/customers/${customerId}`)
      .then((res) => setData(res.data))
      .catch((err) => {
        const msg = err.response?.data?.detail || "Failed to load customer profile.";
        setError(msg);
        toast.error(msg);
      });
  }, [customerId]);

  if (error) {
    return (
      <div className="space-y-6">
        <Link to="/customers" className="text-sm text-accent1 hover:underline">← Back to Customers</Link>
        <Card className="text-center text-red-400">{error}</Card>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-6">
        <SkeletonCard lines={4} />
        <SkeletonCard lines={6} />
      </div>
    );
  }

  const { customer, monthly_spending, merchant_breakdown, fraud_history, recent_transactions } = data;

  return (
    <div className="space-y-6">
      <Link to="/customers" className="text-sm text-accent1 hover:underline">← Back to Customers</Link>

      <Card>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">{customer.name}</h1>
            <p className="text-sm text-white/50">{customer.email} · {customer.phone || "No phone on file"}</p>
            <p className="mt-1 font-mono text-xs text-white/40">{customer.customer_id}</p>
          </div>
          <div className="flex gap-2">
            <Badge tone={customer.risk_profile === "High" ? "fraud" : customer.risk_profile === "Medium" ? "neutral" : "safe"}>
              {customer.risk_profile} Risk Profile
            </Badge>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="rounded-xl bg-white/5 p-3"><p className="text-xs text-white/50">Age</p><p className="text-lg font-bold">{customer.age ?? "—"}</p></div>
          <div className="rounded-xl bg-white/5 p-3"><p className="text-xs text-white/50">Gender</p><p className="text-lg font-bold">{customer.gender ?? "—"}</p></div>
          <div className="rounded-xl bg-white/5 p-3"><p className="text-xs text-white/50">Total Transactions</p><p className="text-lg font-bold">{customer.total_transactions}</p></div>
          <div className="rounded-xl bg-white/5 p-3"><p className="text-xs text-white/50">Avg Amount</p><p className="text-lg font-bold">{formatINR(customer.avg_transaction_amount)}</p></div>
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="mb-4 font-semibold">Monthly Spending</h2>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={monthly_spending}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="month" stroke="rgba(255,255,255,0.4)" fontSize={12} />
              <YAxis stroke="rgba(255,255,255,0.4)" fontSize={12} />
              <Tooltip contentStyle={{ background: "#0a0a12", border: "1px solid rgba(255,255,255,0.1)" }} />
              <Line type="monotone" dataKey="total" stroke="#7c3aed" strokeWidth={2} name="Spending" />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h2 className="mb-4 font-semibold">Merchant Breakdown</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={merchant_breakdown} layout="vertical" margin={{ left: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis type="number" stroke="rgba(255,255,255,0.4)" fontSize={12} />
              <YAxis type="category" dataKey="merchant" stroke="rgba(255,255,255,0.4)" fontSize={11} width={110} />
              <Tooltip contentStyle={{ background: "#0a0a12", border: "1px solid rgba(255,255,255,0.1)" }} />
              <Bar dataKey="total" fill="#2563eb" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card>
        <h2 className="mb-4 font-semibold">Fraud History</h2>
        {fraud_history.length === 0 ? (
          <p className="text-sm text-white/40">No fraud incidents on record for this customer.</p>
        ) : (
          <div className="space-y-2">
            {fraud_history.map((f) => (
              <div key={f.transaction_id} className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-red-500/5 px-4 py-2">
                <span className="font-mono text-xs text-white/50">{f.transaction_id}</span>
                <span className="text-sm">{formatINR(f.amount)} · {f.merchant_name}</span>
                <Badge tone="fraud">{(f.probability * 100).toFixed(0)}% · {f.risk_level}</Badge>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card>
        <h2 className="mb-4 font-semibold">Recent Transactions</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead><tr className="text-white/50"><th className="px-3 py-2">Transaction</th><th className="px-3 py-2">Merchant</th><th className="px-3 py-2">Amount</th><th className="px-3 py-2">Time</th><th className="px-3 py-2">Risk</th></tr></thead>
            <tbody>
              {recent_transactions.map((t) => (
                <tr key={t.transaction_id} className="border-t border-white/5">
                  <td className="px-3 py-2 font-mono text-xs text-white/50">{t.transaction_id.slice(0, 14)}...</td>
                  <td className="px-3 py-2">{t.merchant_name}</td>
                  <td className="px-3 py-2">{formatINR(t.amount)}</td>
                  <td className="px-3 py-2 text-white/50">{new Date(t.transaction_time).toLocaleString()}</td>
                  <td className="px-3 py-2">{t.risk_level && <Badge tone={t.prediction ? "fraud" : "safe"}>{t.risk_level}</Badge>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
