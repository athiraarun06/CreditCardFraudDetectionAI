import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../lib/api.js";

export default function ProfileDropdown() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [profile, setProfile] = useState(null);
  const ref = useRef(null);

  useEffect(() => {
    const onClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const toggleOpen = () => {
    if (!open && !profile) {
      api.get("/me").then((res) => setProfile(res.data)).catch(() => {});
    }
    setOpen((o) => !o);
  };

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const initials = (profile?.full_name || profile?.email || "?")
    .split(" ")
    .map((s) => s[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={toggleOpen}
        className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-fintech text-xs font-bold text-white"
        aria-label="Account menu"
      >
        {initials}
      </button>

      {open && (
        <div className="glass absolute right-0 top-11 w-72 rounded-2xl border border-white/10 p-4 shadow-xl">
          {!profile ? (
            <p className="text-sm text-white/50">Loading...</p>
          ) : (
            <>
              <div className="mb-3 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-fintech text-sm font-bold text-white">
                  {initials}
                </div>
                <div className="min-w-0">
                  <p className="truncate font-semibold">{profile.full_name || "Unnamed User"}</p>
                  <p className="truncate text-xs text-white/50">{profile.email}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="rounded-lg bg-white/5 px-3 py-2">
                  <p className="text-white/40">Account Created</p>
                  <p className="text-white/80">{new Date(profile.created_at).toLocaleDateString()}</p>
                </div>
                <div className="rounded-lg bg-white/5 px-3 py-2">
                  <p className="text-white/40">Total Transactions</p>
                  <p className="text-white/80">{profile.total_transactions}</p>
                </div>
                <div className="col-span-2 rounded-lg bg-white/5 px-3 py-2">
                  <p className="text-white/40">Fraud Detected</p>
                  <p className="text-white/80">{profile.fraud_detected}</p>
                </div>
              </div>
              <button
                onClick={logout}
                className="mt-4 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white/80 hover:bg-white/10"
              >
                Logout
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
