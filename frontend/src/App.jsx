import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Predict from "./pages/Predict.jsx";
import Alerts from "./pages/Alerts.jsx";
import Analytics from "./pages/Analytics.jsx";
import History from "./pages/History.jsx";
import Customers from "./pages/Customers.jsx";
import CustomerProfile from "./pages/CustomerProfile.jsx";
import Explainability from "./pages/Explainability.jsx";
import NotFound from "./pages/NotFound.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/predict" element={<ProtectedRoute><Predict /></ProtectedRoute>} />
      <Route path="/alerts" element={<ProtectedRoute><Alerts /></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
      <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
      <Route path="/customers" element={<ProtectedRoute><Customers /></ProtectedRoute>} />
      <Route path="/customers/:customerId" element={<ProtectedRoute><CustomerProfile /></ProtectedRoute>} />
      <Route path="/explainability" element={<ProtectedRoute><Explainability /></ProtectedRoute>} />
      <Route path="*" element={<ProtectedRoute><NotFound /></ProtectedRoute>} />
    </Routes>
  );
}
