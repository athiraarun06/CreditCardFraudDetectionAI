export default function Logo({ className = "h-8 w-8" }) {
  return (
    <svg viewBox="0 0 200 200" className={className} xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="logoRing" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#3b82f6" />
          <stop offset="55%" stopColor="#93c5fd" />
          <stop offset="100%" stopColor="#e5e7eb" />
        </linearGradient>
        <linearGradient id="logoShield" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#60a5fa" />
          <stop offset="100%" stopColor="#2563eb" />
        </linearGradient>
        <linearGradient id="logoText" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#f8fafc" />
          <stop offset="35%" stopColor="#60a5fa" />
          <stop offset="65%" stopColor="#3b82f6" />
          <stop offset="100%" stopColor="#f8fafc" />
        </linearGradient>
      </defs>

      {/* Outer ring with a dashed gap at top-right */}
      <circle
        cx="100" cy="100" r="88"
        fill="none" stroke="url(#logoRing)" strokeWidth="6" strokeLinecap="round"
        strokeDasharray="230 18 15 15 10"
        transform="rotate(120 100 100)"
      />

      {/* Dotted trail, bottom-right */}
      {Array.from({ length: 9 }).map((_, i) => (
        <circle
          key={i}
          cx={128 + i * 6.5}
          cy={148 + i * 5.2}
          r={2.4 - i * 0.12}
          fill="#3b82f6"
          opacity={1 - i * 0.08}
        />
      ))}

      {/* Shield with circuit traces */}
      <g transform="translate(66 28)">
        <path
          d="M34 0 L64 12 L64 42 C64 66 50 82 34 90 C18 82 4 66 4 42 L4 12 Z"
          fill="none" stroke="url(#logoShield)" strokeWidth="6" strokeLinejoin="round"
        />
        <path
          d="M34 18 L34 34 L20 34 L20 48 M34 34 L48 34 L48 26"
          fill="none" stroke="url(#logoShield)" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"
        />
        <circle cx="34" cy="18" r="3.2" fill="#60a5fa" />
        <circle cx="20" cy="48" r="3.2" fill="#60a5fa" />
        <circle cx="48" cy="26" r="3.2" fill="#60a5fa" />
      </g>

      {/* FGA lettering */}
      <text
        x="100" y="150"
        textAnchor="middle"
        fontFamily="Arial, Helvetica, sans-serif"
        fontWeight="800"
        fontSize="58"
        letterSpacing="-1"
        fill="url(#logoText)"
      >
        FGA
      </text>
    </svg>
  );
}
