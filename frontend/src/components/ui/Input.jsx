export default function Input({ label, className = "", ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1 block text-sm text-white/60">{label}</span>}
      <input
        className={`w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-white placeholder-white/30 outline-none focus:border-accent1 focus:ring-1 focus:ring-accent1 ${className}`}
        {...props}
      />
    </label>
  );
}
