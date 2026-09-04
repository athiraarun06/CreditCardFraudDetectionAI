import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import Logo from "./ui/Logo.jsx";
import ProfileDropdown from "./ProfileDropdown.jsx";
import { useTheme } from "../lib/theme.jsx";

const links = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/predict", label: "Predict" },
  { to: "/alerts", label: "Alerts" },
  { to: "/analytics", label: "Analytics" },
  { to: "/history", label: "History" },
  { to: "/customers", label: "Customers" },
  { to: "/explainability", label: "Explainability" },
];

export default function Layout({ children }) {
  const navigate = useNavigate();
  const { theme, toggle } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 glass border-b border-white/5 px-4 py-4 sm:px-6">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-2">
            <Logo className="h-8 w-8" />
            <span className="font-semibold tracking-tight">FraudGuard AI</span>
          </div>
          <nav className="hidden gap-1 md:flex">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm transition-colors ${
                    isActive ? "bg-white/10 text-white" : "text-white/60 hover:text-white"
                  }`
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            <button
              onClick={toggle}
              aria-label="Toggle theme"
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm hover:bg-white/10"
            >
              {theme === "dark" ? "🌙" : "☀️"}
            </button>
            <ProfileDropdown />
            <button
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm md:hidden"
              onClick={() => setMenuOpen((o) => !o)}
              aria-label="Toggle menu"
            >
              ☰
            </button>
          </div>
        </div>
        {menuOpen && (
          <nav className="mx-auto mt-3 flex max-w-7xl flex-col gap-1 md:hidden">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                onClick={() => setMenuOpen(false)}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm ${isActive ? "bg-white/10 text-white" : "text-white/60"}`
                }
              >
                {l.label}
              </NavLink>
            ))}
            <button onClick={logout} className="rounded-lg px-3 py-2 text-left text-sm text-white/60">
              Logout
            </button>
          </nav>
        )}
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">{children}</main>
    </div>
  );
}
