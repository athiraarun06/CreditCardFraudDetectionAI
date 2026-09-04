export default function Toggle({ label, checked, onChange }) {
  return (
    <label className="flex cursor-pointer items-center justify-between rounded-xl border border-white/10 bg-white/5 px-3 py-2">
      <span className="text-sm text-white/70">{label}</span>
      <span
        onClick={() => onChange(!checked)}
        className={`relative h-6 w-11 rounded-full transition-colors ${checked ? "bg-gradient-fintech" : "bg-white/15"}`}
      >
        <span
          className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${checked ? "translate-x-5" : "translate-x-0.5"}`}
        />
      </span>
    </label>
  );
}
