export default function Card({ children, className = "" }) {
  return (
    <div className={`glass rounded-2xl p-5 shadow-lg shadow-black/30 transition-all hover:shadow-accent1/20 ${className}`}>
      {children}
    </div>
  );
}
