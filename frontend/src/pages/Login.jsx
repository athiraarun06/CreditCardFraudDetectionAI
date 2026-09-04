import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../lib/api.js";
import { useToast } from "../lib/toast.jsx";
import Card from "../components/ui/Card.jsx";
import Input from "../components/ui/Input.jsx";
import Button from "../components/ui/Button.jsx";
import Logo from "../components/ui/Logo.jsx";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.post("/login", { email, password });
      localStorage.setItem("token", res.data.access_token);
      toast.success("Welcome back!");
      navigate("/dashboard");
    } catch (err) {
      const msg = err.response?.data?.detail || "Login failed. Check the backend is running.";
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <div className="mb-6 text-center">
          <Logo className="mx-auto mb-3 h-16 w-16" />
          <h1 className="text-2xl font-bold">Welcome back</h1>
          <p className="text-sm text-white/50">Sign in to FraudGuard AI</p>
        </div>
        <form onSubmit={submit} className="space-y-4">
          <Input label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
          <Input label="Password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
          {error && <p className="text-sm text-red-400">{error}</p>}
          <Button type="submit" className="w-full" disabled={loading}>{loading ? "Signing in..." : "Sign In"}</Button>
        </form>
        <p className="mt-4 text-center text-sm text-white/50">
          No account? <Link to="/register" className="text-accent1 hover:underline">Register</Link>
        </p>
      </Card>
    </div>
  );
}
