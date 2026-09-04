import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../lib/api.js";
import { useToast } from "../lib/toast.jsx";
import Card from "../components/ui/Card.jsx";
import Input from "../components/ui/Input.jsx";
import Button from "../components/ui/Button.jsx";
import Logo from "../components/ui/Logo.jsx";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function Register() {
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const validate = () => {
    if (!form.full_name.trim()) return "Please enter your full name.";
    if (!EMAIL_RE.test(form.email)) return "Please enter a valid email address.";
    if (form.password.length < 6) return "Password must be at least 6 characters.";
    return null;
  };

  const submit = async (e) => {
    e.preventDefault();
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }
    setError("");
    setLoading(true);
    try {
      await api.post("/register", form);
      const res = await api.post("/login", { email: form.email, password: form.password });
      localStorage.setItem("token", res.data.access_token);
      toast.success("Account created successfully!");
      navigate("/dashboard");
    } catch (err) {
      const msg = err.response?.data?.detail || "Registration failed. Check the backend is running.";
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
          <h1 className="text-2xl font-bold">Create your account</h1>
          <p className="text-sm text-white/50">Join FraudGuard AI</p>
        </div>
        <form onSubmit={submit} className="space-y-4">
          <Input label="Full name" required value={form.full_name} onChange={update("full_name")} placeholder="Jane Doe" />
          <Input label="Email" type="email" required value={form.email} onChange={update("email")} placeholder="you@example.com" />
          <Input label="Password" type="password" required minLength={6} value={form.password} onChange={update("password")} placeholder="At least 6 characters" />
          {error && <p className="text-sm text-red-400">{error}</p>}
          <Button type="submit" className="w-full" disabled={loading}>{loading ? "Creating..." : "Create Account"}</Button>
        </form>
        <p className="mt-4 text-center text-sm text-white/50">
          Already have an account? <Link to="/login" className="text-accent1 hover:underline">Sign in</Link>
        </p>
      </Card>
    </div>
  );
}
