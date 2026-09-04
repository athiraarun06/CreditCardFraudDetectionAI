import { motion } from "framer-motion";

export function riskLevel(pct) {
  if (pct >= 75) return { label: "Critical", color: "#dc2626" };
  if (pct >= 50) return { label: "High", color: "#f97316" };
  if (pct >= 20) return { label: "Medium", color: "#eab308" };
  return { label: "Low", color: "#22c55e" };
}

export default function RiskMeter({ probability = 0 }) {
  const pct = Math.max(0, Math.min(100, Math.round(probability * 100)));
  const { label, color } = riskLevel(pct);
  const angle = -90 + (pct / 100) * 180;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative h-40 w-52">
        <svg viewBox="0 0 200 110" className="h-full w-full">
          <defs>
            <linearGradient id="riskGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#22c55e" />
              <stop offset="20%" stopColor="#22c55e" />
              <stop offset="20%" stopColor="#eab308" />
              <stop offset="50%" stopColor="#eab308" />
              <stop offset="50%" stopColor="#f97316" />
              <stop offset="75%" stopColor="#f97316" />
              <stop offset="75%" stopColor="#dc2626" />
              <stop offset="100%" stopColor="#dc2626" />
            </linearGradient>
          </defs>
          <path d="M 10 100 A 90 90 0 0 1 190 100" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="14" strokeLinecap="round" />
          <path d="M 10 100 A 90 90 0 0 1 190 100" fill="none" stroke="url(#riskGradient)" strokeWidth="14" strokeLinecap="round" opacity="0.35" />
          <motion.path
            d="M 10 100 A 90 90 0 0 1 190 100"
            fill="none"
            stroke={color}
            strokeWidth="14"
            strokeLinecap="round"
            strokeDasharray={283}
            initial={{ strokeDashoffset: 283 }}
            animate={{ strokeDashoffset: 283 * (1 - pct / 100) }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
          <motion.line
            x1="100" y1="100" x2="100" y2="30"
            stroke="#fff" strokeWidth="3" strokeLinecap="round"
            style={{ transformOrigin: "100px 100px" }}
            initial={{ rotate: -90 }}
            animate={{ rotate: angle }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
          <circle cx="100" cy="100" r="6" fill="#fff" />
        </svg>
        <div className="absolute inset-x-0 bottom-0 flex flex-col items-center">
          <span className="text-3xl font-bold" style={{ color }}>{pct}%</span>
          <span className="text-xs text-white/50">fraud probability</span>
        </div>
      </div>
      <span className="rounded-full px-3 py-1 text-sm font-semibold" style={{ color, backgroundColor: `${color}22` }}>
        {label} Risk
      </span>
    </div>
  );
}
