import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import api from "../lib/api.js";
import { useToast } from "../lib/toast.jsx";
import Card from "../components/ui/Card.jsx";
import Badge from "../components/ui/Badge.jsx";
import Button from "../components/ui/Button.jsx";
import Select from "../components/ui/Select.jsx";
import Skeleton from "../components/ui/Skeleton.jsx";
import { formatINR } from "../lib/currency.js";

const STATUS_FILTERS = ["", "Pending", "Approved", "Blocked", "Reviewed", "Frozen"];
const RISK_TONE = { High: "fraud", Critical: "fraud" };

const ACTIONS = [
  { label: "Approve", status: "Approved", variant: "ghost" },
  { label: "Review", status: "Reviewed", variant: "ghost" },
  { label: "Block", status: "Blocked", variant: "primary" },
  { label: "Freeze", status: "Frozen", variant: "primary" },
];

export default function Alerts() {
  const toast = useToast();
  const [alerts, setAlerts] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const params = statusFilter ? { status: statusFilter } : {};
      const res = await api.get("/alerts", { params });
      setAlerts(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to load alerts.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [statusFilter]);

  const act = async (alertId, status) => {
    setBusyId(alertId);
    try {
      await api.post(`/alerts/${alertId}/action`, { status });
      toast.success(`Alert marked as ${status}.`);
      setAlerts((prev) => prev.map((a) => (a.id === alertId ? { ...a, status } : a)));
    } catch (err) {
      toast.error(err.response?.data?.detail || "Action failed.");
    } finally {
      setBusyId(null);
    }
  };

  const pendingCount = alerts.filter((a) => a.status === "Pending").length;
  const criticalCount = alerts.filter((a) => a.risk_level === "Critical").length;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">Fraud Alert Center</h1>
        <div className="flex items-center gap-3">
          <span className="text-sm text-white/50">{pendingCount} pending · {criticalCount} critical</span>
          <Select options={STATUS_FILTERS.map((s) => s || "All Statuses")}
                  value={statusFilter || "All Statuses"}
                  onChange={(e) => setStatusFilter(e.target.value === "All Statuses" ? "" : e.target.value)} />
        </div>
      </div>

      <Card>
        {loading ? (
          <div className="space-y-2">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}</div>
        ) : alerts.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-16 text-center">
            <div className="text-4xl">🛡️</div>
            <p className="text-white/60">No fraud alerts — all clear.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="text-white/50">
                  <th className="px-3 py-2">Transaction ID</th>
                  <th className="px-3 py-2">Customer</th>
                  <th className="px-3 py-2">Amount</th>
                  <th className="px-3 py-2">Merchant</th>
                  <th className="px-3 py-2">Location</th>
                  <th className="px-3 py-2">Probability</th>
                  <th className="px-3 py-2">Risk</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                <AnimatePresence>
                  {alerts.map((a) => (
                    <motion.tr
                      key={a.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className={`border-t border-white/5 ${a.risk_level === "Critical" ? "bg-red-500/5" : ""} hover:bg-white/5`}
                    >
                      <td className="px-3 py-2 font-mono text-xs text-white/60">{a.transaction_id.slice(0, 14)}...</td>
                      <td className="px-3 py-2">{a.customer_name || "—"}</td>
                      <td className="px-3 py-2">{formatINR(a.amount)}</td>
                      <td className="px-3 py-2">{a.merchant_name || "—"}</td>
                      <td className="px-3 py-2">{a.location || "—"}</td>
                      <td className="px-3 py-2 font-semibold text-red-400">{(a.probability * 100).toFixed(1)}%</td>
                      <td className="px-3 py-2"><Badge tone={RISK_TONE[a.risk_level] || "neutral"}>{a.risk_level}</Badge></td>
                      <td className="px-3 py-2"><Badge tone={a.status === "Pending" ? "neutral" : "safe"}>{a.status}</Badge></td>
                      <td className="px-3 py-2">
                        <div className="flex gap-1">
                          {ACTIONS.map((act_) => (
                            <button
                              key={act_.status}
                              disabled={busyId === a.id || a.status === act_.status}
                              onClick={() => act(a.id, act_.status)}
                              className="rounded-md border border-white/10 bg-white/5 px-2 py-1 text-[11px] hover:bg-white/10 disabled:opacity-40"
                            >
                              {act_.label}
                            </button>
                          ))}
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </AnimatePresence>
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
