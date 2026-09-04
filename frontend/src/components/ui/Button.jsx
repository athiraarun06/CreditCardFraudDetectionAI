export default function Button({ children, className = "", variant = "primary", ...props }) {
  const base = "px-4 py-2 rounded-xl font-medium transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-gradient-fintech text-white hover:brightness-110 shadow-lg shadow-accent1/30",
    ghost: "bg-white/5 text-white hover:bg-white/10 border border-white/10",
  };
  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}
