import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

import Login from "./pages/Login";
import Signup from "./pages/Signup";
import VerifyEmail from "./pages/VerifyEmail";
import Dashboard from "./pages/Dashboard";
import PredictForm from "./pages/PredictForm";
import Results from "./pages/Results";
import SymptomsPage from "./pages/SymptomsPage";
import Reports from "./pages/Reports";
import AddCycleHistory from "./pages/AddCycleHistory";

import ProtectedRoute from "./components/ProtectedRoute";
import ProtectedLayout from "./components/ProtectedLayout";
import Chatbot from "./components/Chatbot"; // updated

import "./style.css";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/verify-email/:token" element={<VerifyEmail />} />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <ProtectedLayout>
                  <Dashboard />
                </ProtectedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/predict"
            element={
              <ProtectedRoute>
                <ProtectedLayout>
                  <PredictForm />
                </ProtectedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/cycles/history"
            element={
              <ProtectedRoute>
                <ProtectedLayout>
                  <AddCycleHistory />
                </ProtectedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/results"
            element={
              <ProtectedRoute>
                <ProtectedLayout>
                  <Results />
                </ProtectedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/symptoms"
            element={
              <ProtectedRoute>
                <ProtectedLayout>
                  <SymptomsPage />
                </ProtectedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute>
                <ProtectedLayout>
                  <Reports />
                </ProtectedLayout>
              </ProtectedRoute>
            }
          />

          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>

        {/* Chatbot visible on all pages */}
        <Chatbot />
      </BrowserRouter>
    </AuthProvider>
  );
}