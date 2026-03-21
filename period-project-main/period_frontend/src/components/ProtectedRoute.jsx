import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ProtectedRoute = ({ children }) => {
  const { loading } = useAuth();
  const token = localStorage.getItem("access");

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );
  }

  // ❌ No token → always go to login
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // ✅ Token exists → allow page
  return children;
};

export default ProtectedRoute;
