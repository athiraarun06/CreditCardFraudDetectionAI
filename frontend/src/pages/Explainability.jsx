import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import api from "../lib/api.js";
import Card from "../components/ui/Card.jsx";
import { SkeletonCard } from "../components/ui/Skeleton.jsx";

const API_ORIGIN = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

export default function Explainability() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/explainability").then((res) => setData(res.data)).catch((err) => setError(err.response?.data?.detail || "Model not trained yet."));
  }, []);

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Model Explainability</h1>
        <Card className="text-center">
          <p className="text-amber-400">{error}</p>
          <p className="mt-2 text-sm text-white/50">Run <code>python -m app.ml.train</code> from the backend/ folder to train a model.</p>
        </Card>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Model Explainability</h1>
        <SkeletonCard lines={8} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Model Explainability</h1>

      <Card>
        <h2 className="mb-4 font-semibold">Top Contributing Features (Global Importance)</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data.top_features} layout="vertical" margin={{ left: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis type="number" stroke="rgba(255,255,255,0.4)" fontSize={12} />
            <YAxis type="category" dataKey="feature" stroke="rgba(255,255,255,0.4)" fontSize={11} width={160} />
            <Tooltip contentStyle={{ background: "#0a0a12", border: "1px solid rgba(255,255,255,0.1)" }} />
            <Bar dataKey="importance" fill="#7c3aed" radius={[0, 6, 6, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Card>
        <h2 className="mb-4 font-semibold">Plain-English Explanation</h2>
        <ul className="space-y-2 text-sm text-white/70">
          {data.explanations.map((e) => (
            <li key={e.feature} className="rounded-lg bg-white/5 px-4 py-2">
              {e.explanation}
            </li>
          ))}
        </ul>
      </Card>

      {(data.images.shap_summary || data.images.shap_feature_importance || data.images.shap_waterfall) && (
        <Card>
          <h2 className="mb-4 font-semibold">SHAP Visualizations</h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {data.images.shap_summary && (
              <div>
                <p className="mb-2 text-xs text-white/50">Summary Plot</p>
                <img src={`${API_ORIGIN}${data.images.shap_summary}`} alt="SHAP summary plot" className="w-full rounded-xl border border-white/10" />
              </div>
            )}
            {data.images.shap_feature_importance && (
              <div>
                <p className="mb-2 text-xs text-white/50">Feature Importance</p>
                <img src={`${API_ORIGIN}${data.images.shap_feature_importance}`} alt="SHAP feature importance" className="w-full rounded-xl border border-white/10" />
              </div>
            )}
            {data.images.shap_waterfall && (
              <div>
                <p className="mb-2 text-xs text-white/50">Waterfall (sample prediction)</p>
                <img src={`${API_ORIGIN}${data.images.shap_waterfall}`} alt="SHAP waterfall plot" className="w-full rounded-xl border border-white/10" />
              </div>
            )}
          </div>
        </Card>
      )}

      {(data.images.confusion_matrix || data.images.roc_curve || data.images.pr_curve) && (
        <Card>
          <h2 className="mb-4 font-semibold">Model Evaluation</h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {data.images.confusion_matrix && (
              <div>
                <p className="mb-2 text-xs text-white/50">Confusion Matrix</p>
                <img src={`${API_ORIGIN}${data.images.confusion_matrix}`} alt="Confusion matrix" className="w-full rounded-xl border border-white/10" />
              </div>
            )}
            {data.images.roc_curve && (
              <div>
                <p className="mb-2 text-xs text-white/50">ROC Curve</p>
                <img src={`${API_ORIGIN}${data.images.roc_curve}`} alt="ROC curve" className="w-full rounded-xl border border-white/10" />
              </div>
            )}
            {data.images.pr_curve && (
              <div>
                <p className="mb-2 text-xs text-white/50">Precision-Recall Curve</p>
                <img src={`${API_ORIGIN}${data.images.pr_curve}`} alt="Precision-recall curve" className="w-full rounded-xl border border-white/10" />
              </div>
            )}
            {data.images.calibration_curve && (
              <div>
                <p className="mb-2 text-xs text-white/50">Calibration Curve</p>
                <img src={`${API_ORIGIN}${data.images.calibration_curve}`} alt="Calibration curve" className="w-full rounded-xl border border-white/10" />
              </div>
            )}
            {data.images.lift_curve && (
              <div>
                <p className="mb-2 text-xs text-white/50">Lift Curve</p>
                <img src={`${API_ORIGIN}${data.images.lift_curve}`} alt="Lift curve" className="w-full rounded-xl border border-white/10" />
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
