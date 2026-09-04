import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../lib/api.js";
import { useToast } from "../lib/toast.jsx";
import Card from "../components/ui/Card.jsx";
import Input from "../components/ui/Input.jsx";
import Badge from "../components/ui/Badge.jsx";
import Skeleton from "../components/ui/Skeleton.jsx";
import { formatINR } from "../lib/currency.js";

export default function Customers() {
  const toast = useToast();
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const res = await api.get("/customers", { params: { search: search || undefined } });
      setCustomers(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to load customers.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Customers</h1>
      <Card>
        <div className="mb-4 flex gap-3">
          <div className="flex-1"><Input placeholder="Search by name, email, or ID..." value={search} onChange={(e) => setSearch(e.target.value)} /></div>
          <button onClick={load} className="rounded-xl bg-gradient-fintech px-4 py-2 text-sm font-medium text-white">Search</button>
        </div>
        {loading ? (
          <div className="space-y-2">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}</div>
        ) : customers.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-16 text-center">
            <div className="text-4xl">👤</div>
            <p className="text-white/60">No customers yet — score a transaction on the Predict page first.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead><tr className="text-white/50"><th className="px-3 py-2">Name</th><th className="px-3 py-2">Email</th><th className="px-3 py-2">Age</th><th className="px-3 py-2">Risk Profile</th><th className="px-3 py-2">Txns</th><th className="px-3 py-2">Avg Amount</th></tr></thead>
              <tbody>
                {customers.map((c) => (
                  <tr key={c.customer_id} className="border-t border-white/5 hover:bg-white/5">
                    <td className="px-3 py-2">
                      <Link to={`/customers/${c.customer_id}`} className="text-accent1 hover:underline">{c.name}</Link>
                    </td>
                    <td className="px-3 py-2 text-white/60">{c.email}</td>
                    <td className="px-3 py-2">{c.age ?? "—"}</td>
                    <td className="px-3 py-2"><Badge tone={c.risk_profile === "High" ? "fraud" : c.risk_profile === "Medium" ? "neutral" : "safe"}>{c.risk_profile}</Badge></td>
                    <td className="px-3 py-2">{c.total_transactions}</td>
                    <td className="px-3 py-2">{formatINR(c.avg_transaction_amount)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
