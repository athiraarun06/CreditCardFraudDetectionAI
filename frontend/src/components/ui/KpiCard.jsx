import { motion } from "framer-motion";
import Card from "./Card.jsx";

export default function KpiCard({ label, value, sub, gradient = false }) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card className="min-h-[110px]">
        <p className="text-sm text-white/50">{label}</p>
        <p className={`mt-2 text-3xl font-bold ${gradient ? "bg-gradient-fintech bg-clip-text text-transparent" : "text-white"}`}>
          {value}
        </p>
        {sub && <p className="mt-1 text-xs text-white/40">{sub}</p>}
      </Card>
    </motion.div>
  );
}
