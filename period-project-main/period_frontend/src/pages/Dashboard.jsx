import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { API_BASE_URL } from "../config";
import Chatbot from "../components/Chatbot";

// base url constant is defined in multiple places; replicate here for simplicity
const API_BASE = API_BASE_URL;

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const [cycleCount, setCycleCount] = useState(null);

  React.useEffect(() => {
    const token =
      localStorage.getItem("access") ||
      localStorage.getItem("access_token") ||
      localStorage.getItem("token");
    if (!token) return;

    fetch(`${API_BASE}/cycles/?include_history=true`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data)) setCycleCount(data.length);
      })
      .catch((e) => console.error("failed to load cycles", e));
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-pink-50 to-rose-100">

        {/* NAVBAR */}
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              {/* Logo */}
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center">
                  <svg
                    className="w-6 h-6 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <span className="ml-3 text-xl font-bold text-gray-900">MCIDS</span>
              </div>

              {/* User */}
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-700">
                  Welcome, <span className="font-semibold">{user?.username}</span>
                </span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* MAIN */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">

          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Menstrual Cycle Irregularity Detection
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Advanced AI-powered analysis to help detect and understand menstrual cycle patterns
            </p>
          </div>

          {/* Cards */}
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">

            {/* Predict */}
            <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition">
              <div className="flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-pink-500 to-rose-600 mb-6">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold mb-3">Predict Irregularity</h2>
              <p className="text-gray-600 mb-6">
                Analyze your cycle data using AI to detect irregularities.
              </p>
              <button
                onClick={() => navigate("/predict")}
                className="w-full py-3 rounded-lg bg-gradient-to-r from-pink-500 to-rose-600 text-white font-semibold hover:opacity-90"
              >
                Start Prediction
              </button>
            </div>

            {/* Add history (only when there are fewer than two saved cycles) */}
            {cycleCount !== null && cycleCount < 2 && (
              <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition">
                <div className="flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-green-500 to-teal-600 mb-6">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold mb-3">Add Cycle History</h2>
                <p className="text-gray-600 mb-6">
                  Enter at least two past cycle lengths so the AI can make accurate predictions.
                </p>
                <button
                  onClick={() => navigate("/cycles/history")}
                  className="w-full py-3 rounded-lg bg-gradient-to-r from-green-500 to-teal-600 text-white font-semibold hover:opacity-90"
                >
                  Add History
                </button>
              </div>
            )}

            {/* Reports */}
            <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition">
              <div className="flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-cyan-600 mb-6">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5l5 5v12a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold mb-3">Previous Reports</h2>
              <p className="text-gray-600 mb-6">
                View and track your past cycle analysis reports.
              </p>
              <button
                onClick={() => navigate("/reports")}
                className="w-full py-3 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-600 text-white font-semibold hover:opacity-90"
              >
                View Reports
              </button>
            </div>

            {/* Symptoms */}
            <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition">
              <div className="flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 mb-6">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M19.428 15.341A8 8 0 118.659 4.572M21 21l-4.35-4.35" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold mb-3">Track Symptoms</h2>
              <p className="text-gray-600 mb-6">
                Log symptoms and relate them to menstrual health.
              </p>
              <button
                onClick={() => navigate("/symptoms")}
                className="w-full py-3 rounded-lg bg-gradient-to-r from-purple-500 to-indigo-600 text-white font-semibold hover:opacity-90"
              >
                Track Symptoms
              </button>
            </div>

          </div>

          {/* Diet & Health Awareness Section */}
          <div className="mt-16 max-w-5xl mx-auto bg-white rounded-[2rem] shadow-xl overflow-hidden relative mb-12 border border-pink-100">
            <div className="absolute top-0 right-0 -mt-16 -mr-16 w-64 h-64 bg-pink-300 opacity-20 rounded-full blur-3xl"></div>
            <div className="absolute bottom-0 left-0 -mb-16 -ml-16 w-64 h-64 bg-rose-300 opacity-20 rounded-full blur-3xl"></div>
            
            <div className="relative p-10 md:p-14 text-gray-800">
              <div className="text-center mb-12">
                <span className="inline-block py-1 px-4 rounded-full bg-pink-100 text-pink-600 text-sm font-bold tracking-widest uppercase mb-4 shadow-sm border border-pink-200">Wellness Guide</span>
                <h2 className="text-3xl md:text-4xl font-extrabold mb-4 text-gray-900">Cycle-Synced Diet & Nutrition</h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">Nourishing your body with the right foods at different stages of your cycle can alleviate symptoms and boost your energy levels naturally.</p>
              </div>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white/80 backdrop-blur-sm border border-pink-100 rounded-2xl p-6 hover:shadow-lg hover:-translate-y-1 transition duration-300 shadow-md">
                  <div className="text-4xl mb-4">🩸</div>
                  <h3 className="text-xl font-bold mb-2 text-rose-600">Menstrual</h3>
                  <p className="text-sm text-gray-600 leading-relaxed font-medium"><span className="text-pink-500 font-bold">Days 1-5</span><br/><br/>Focus on iron-rich foods like dark leafy greens, red meat, and lentils to replace lost blood. Warm, comforting soups and herbal teas help soothe severe cramps.</p>
                </div>
                
                <div className="bg-white/80 backdrop-blur-sm border border-pink-100 rounded-2xl p-6 hover:shadow-lg hover:-translate-y-1 transition duration-300 shadow-md">
                  <div className="text-4xl mb-4">🌱</div>
                  <h3 className="text-xl font-bold mb-2 text-emerald-600">Follicular</h3>
                  <p className="text-sm text-gray-600 leading-relaxed font-medium"><span className="text-pink-500 font-bold">Days 6-14</span><br/><br/>Your energy rises! Eat light, vibrant foods like fresh salads, fermented foods (kimchi, yogurt), and lean proteins to support healthy estrogen levels and gut health.</p>
                </div>
                
                <div className="bg-white/80 backdrop-blur-sm border border-pink-100 rounded-2xl p-6 hover:shadow-lg hover:-translate-y-1 transition duration-300 shadow-md">
                  <div className="text-4xl mb-4">🔥</div>
                  <h3 className="text-xl font-bold mb-2 text-orange-500">Ovulatory</h3>
                  <p className="text-sm text-gray-600 leading-relaxed font-medium"><span className="text-pink-500 font-bold">Days 14-16</span><br/><br/>Enjoy anti-inflammatory foods like berries, quinoa, and almonds. High dietary fiber is key here to help your body flush out excess estrogen during this peak phase.</p>
                </div>
                
                <div className="bg-white/80 backdrop-blur-sm border border-pink-100 rounded-2xl p-6 hover:shadow-lg hover:-translate-y-1 transition duration-300 shadow-md">
                  <div className="text-4xl mb-4">✨</div>
                  <h3 className="text-xl font-bold mb-2 text-indigo-600">Luteal</h3>
                  <p className="text-sm text-gray-600 leading-relaxed font-medium"><span className="text-pink-500 font-bold">Days 17-28</span><br/><br/>Combat PMS by boosting magnesium and complex carbs. Think delicious sweet potatoes, dark chocolate, and pumpkin seeds to effectively stabilize your mood.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-12 max-w-4xl mx-auto bg-white rounded-2xl shadow-lg p-8">
            <h3 className="text-xl font-bold mb-4">About This System</h3>
            <p className="text-gray-600">
              This system uses machine learning to analyze health indicators and
              detect menstrual cycle irregularities. It is designed for academic
              and informational purposes only.
            </p>
          </div>

        </main>
      </div>

      {/* Chatbot */}
      <div className="fixed bottom-5 right-5 z-50">
        <Chatbot />
      </div>
    </>
  );
};

export default Dashboard;