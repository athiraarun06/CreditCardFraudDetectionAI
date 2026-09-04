export default function Select({ label, options = [], className = "", ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1 block text-sm text-white/60">{label}</span>}
      <select
        className={`w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-white outline-none focus:border-accent1 focus:ring-1 focus:ring-accent1 ${className}`}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt} value={opt} className="bg-[#0a0a12]">
            {opt}
          </option>
        ))}
      </select>
    </label>
  );
}
