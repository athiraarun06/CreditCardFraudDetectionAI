export default function Badge({ children, tone = "neutral" }) {
  const tones = {
    neutral: "bg-white/10 text-white/70",
    fraud: "bg-red-500/15 text-red-400 border border-red-500/30",
    safe: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
  };
  return <span className={`rounded-full px-3 py-1 text-xs font-medium ${tones[tone]}`}>{children}</span>;
}
