import { Navigate } from "react-router-dom";
import Layout from "./Layout.jsx";

export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token");
  if (!token) return <Navigate to="/login" replace />;
  return <Layout>{children}</Layout>;
}
