import { useEffect, useState } from "react";
import api from "../lib/api.js";
import { useToast } from "../lib/toast.jsx";
import Card from "../components/ui/Card.jsx";
import Input from "../components/ui/Input.jsx";
import Select from "../components/ui/Select.jsx";
import Button from "../components/ui/Button.jsx";
import Badge from "../components/ui/Badge.jsx";
import Skeleton from "../components/ui/Skeleton.jsx";
import Modal from "../components/ui/Modal.jsx";
import { formatINR } from "../lib/currency.js";

const STATUS_OPTIONS = ["", "fraud", "legit"];

export default function History() {
  const toast = useToast();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({ search: "", customer: "", merchant: "", status: "", start_date: "", end_date: "" });
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const pageSize = 15;

  const load = async () => {
    setLoading(true);
    try {
      const params = Object.fromEntries(
        Object.entries({ page, page_size: pageSize, ...filters }).filter(([, v]) => v)
      );
      const res = await api.get("/transactions", { params });
      setItems(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to load transaction history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [page]);

  const update = (k) => (e) => setFilters({ ...filters, [k]: e.target.value });

  const openDetail = async (txnId) => {
    setSelected(txnId);
    setDetail(null);
    try {
      const res = await api.get(`/transactions/${txnId}`);
      setDetail(res.data);
    } catch (err) {
      toast.error("Failed to load transaction detail.");
    }
  };

  const exportCsv = () => {
    if (items.length === 0) {
      toast.error("No transactions to export.");
      return;
    }
    const header = ["transaction_id", "customer_name", "amount", "transaction_time", "merchant_name", "merchant_category", "merchant_city", "payment_method", "prediction", "probability", "risk_level"];
    const rows = items.map((t) => header.map((h) => JSON.stringify(t[h] ?? "")).join(","));
    const csv = [header.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "transactions.csv";
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Transactions exported as CSV.");
  };

  const exportPdf = () => {
    if (items.length === 0) {
      toast.error("No transactions to export.");
      return;
    }
    const rows = items.map((t) => `
      <tr>
        <td>${t.transaction_id}</td><td>${t.customer_name || ""}</td><td>${formatINR(t.amount)}</td>
        <td>${new Date(t.transaction_time).toLocaleString()}</td><td>${t.merchant_name || ""}</td>
        <td>${t.prediction ? "Fraud" : "Legit"}</td>
      </tr>`).join("");
    const html = `<html><head><title>Transaction Report</title>
      <style>body{font-family:sans-serif;padding:24px;} table{width:100%;border-collapse:collapse;} th,td{border:1px solid #ccc;padding:6px 8px;font-size:12px;text-align:left;} th{background:#f3f3f3;}</style>
      </head><body><h2>Transaction History Report</h2><p>Generated ${new Date().toLocaleString()}</p>
      <table><thead><tr><th>Transaction ID</th><th>Customer</th><th>Amount</th><th>Time</th><th>Merchant</th><th>Status</th></tr></thead>
      <tbody>${rows}</tbody></table></body></html>`;
    const win = window.open("", "_blank");
    win.document.write(html);
    win.document.close();
    win.focus();
    win.print();
    toast.success("Opened print dialog — choose 'Save as PDF' to export.");
  };

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Transaction History</h1>

      <Card>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <Input placeholder="Search..." value={filters.search} onChange={update("search")} />
          <Input placeholder="Customer" value={filters.customer} onChange={update("customer")} />
          <Input placeholder="Merchant" value={filters.merchant} onChange={update("merchant")} />
          <Select options={STATUS_OPTIONS.map((s) => s || "All Statuses")}
                  value={filters.status || "All Statuses"}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value === "All Statuses" ? "" : e.target.value })} />
          <Input type="date" value={filters.start_date} onChange={update("start_date")} />
          <Input type="date" value={filters.end_date} onChange={update("end_date")} />
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          <Button onClick={() => { setPage(1); load(); }}>Apply Filters</Button>
          <Button variant="ghost" onClick={exportCsv}>Export CSV</Button>
          <Button variant="ghost" onClick={exportPdf}>Export PDF</Button>
        </div>
      </Card>

      <Card>
        {loading ? (
          <div className="space-y-2">
            {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
          </div>
        ) : items.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-16 text-center">
            <div className="text-4xl">🔍</div>
            <p className="text-white/60">No transactions found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="text-white/50">
                  <th className="px-3 py-2">Transaction ID</th>
                  <th className="px-3 py-2">Customer</th>
                  <th className="px-3 py-2">Amount</th>
                  <th className="px-3 py-2">Time</th>
                  <th className="px-3 py-2">Merchant</th>
                  <th className="px-3 py-2">Probability</th>
                  <th className="px-3 py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {items.map((t) => (
                  <tr key={t.id} onClick={() => openDetail(t.transaction_id)} className="cursor-pointer border-t border-white/5 hover:bg-white/5">
                    <td className="px-3 py-2 font-mono text-xs text-white/60">{t.transaction_id.slice(0, 14)}...</td>
                    <td className="px-3 py-2">{t.customer_name || "—"}</td>
                    <td className="px-3 py-2">{formatINR(t.amount)}</td>
                    <td className="px-3 py-2 text-white/50">{new Date(t.transaction_time).toLocaleString()}</td>
                    <td className="px-3 py-2">{t.merchant_name || t.merchant_category}</td>
                    <td className="px-3 py-2">{t.probability != null ? `${(t.probability * 100).toFixed(1)}%` : "—"}</td>
                    <td className="px-3 py-2">
                      {t.prediction != null && <Badge tone={t.prediction ? "fraud" : "safe"}>{t.risk_level || (t.prediction ? "Fraud" : "Legit")}</Badge>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="mt-4 flex items-center justify-between text-sm text-white/50">
          <span>Page {page} of {totalPages} ({total} total)</span>
          <div className="flex gap-2">
            <Button variant="ghost" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</Button>
            <Button variant="ghost" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Next</Button>
          </div>
        </div>
      </Card>

      <Modal open={!!selected} onClose={() => setSelected(null)} title="Transaction Detail">
        {!detail ? (
          <div className="space-y-2"><Skeleton className="h-6 w-full" /><Skeleton className="h-32 w-full" /></div>
        ) : (
          <div className="space-y-4 text-sm">
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(detail.transaction).filter(([k]) => !["id"].includes(k)).map(([k, v]) => (
                <div key={k} className="rounded-lg bg-white/5 px-3 py-2">
                  <p className="text-xs text-white/40">{k}</p>
                  <p className="text-white/80">{String(v ?? "—")}</p>
                </div>
              ))}
            </div>
            {detail.prediction && (
              <div>
                <h3 className="mb-2 font-semibold">Prediction</h3>
                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-lg bg-white/5 px-3 py-2"><p className="text-xs text-white/40">Probability</p><p>{(detail.prediction.probability * 100).toFixed(1)}%</p></div>
                  <div className="rounded-lg bg-white/5 px-3 py-2"><p className="text-xs text-white/40">Risk Level</p><p>{detail.prediction.risk_level}</p></div>
                  <div className="rounded-lg bg-white/5 px-3 py-2 col-span-2"><p className="text-xs text-white/40">Recommended Action</p><p>{detail.prediction.recommended_action}</p></div>
                  <div className="rounded-lg bg-white/5 px-3 py-2 col-span-2"><p className="text-xs text-white/40">Explanation</p><p>{detail.prediction.explanation}</p></div>
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
