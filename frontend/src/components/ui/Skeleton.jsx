export default function Skeleton({ className = "" }) {
  return <div className={`skeleton ${className}`} />;
}

export function SkeletonCard({ lines = 3 }) {
  return (
    <div className="glass space-y-3 rounded-2xl p-5">
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-8 w-1/2" />
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} className="h-3 w-full" />
      ))}
    </div>
  );
}
