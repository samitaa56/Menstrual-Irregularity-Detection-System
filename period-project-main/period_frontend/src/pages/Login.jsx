import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Chatbot from "../components/Chatbot";
import axiosInstance from "../api/axiosInstance"; // ✅ single Axios

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // ✅ general error (login fail)
  const [error, setError] = useState("");

  // ✅ password rule error (instant)
  const [passwordError, setPasswordError] = useState("");

  // ✅ show / hide password
  const [showPassword, setShowPassword] = useState(false);

  const navigate = useNavigate();
  const { login, loading } = useAuth();

  // ✅ Chatbot messages
  const [chatMessages, setChatMessages] = useState([]);

  // ✅ Password validation (special char required)
  const validatePassword = (value) => {
    if (value === "") return "";
    if (value.length < 8) return "Password must be at least 8 characters long";
    if (!/[A-Za-z]/.test(value)) return "Password must contain at least one letter";
    if (!/\d/.test(value)) return "Password must contain at least one number";
    if (!/[@$!%*#?&]/.test(value))
      return "Password must contain at least one special character (@$!%*#?&)";
    return "";
  };

  const handlePasswordChange = (e) => {
    const value = e.target.value;
    setPassword(value);

    const msg = validatePassword(value);
    setPasswordError(msg);

    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const msg = validatePassword(password);
    setPasswordError(msg);
    if (msg) {
      setError("Please fix the password format.");
      return;
    }

    const success = await login(username, password);

    if (success) {
      navigate("/dashboard", { replace: true });
    } else {
      setError("Invalid username or password. Make sure your email is verified before logging in. Check your email for the verification link.");
    }
  };

  // ✅ Optional: call backend directly using Axios without touching useAuth
  const callLoginAPI = async () => {
    try {
      const response = await axiosInstance.post("login/", { username, password });
      console.log("Axios Login response:", response.data);
      localStorage.setItem("token", response.data.token);
    } catch (err) {
      console.error("Axios Login error:", err.response?.data || err.message);
    }
  };

  // ✅ Chatbot send message
  const sendChatMessage = async (message) => {
    if (!message) return;

    const newMessages = [...chatMessages, { from: "user", text: message }];
    setChatMessages(newMessages);

    try {
      const response = await axiosInstance.post("chatbot/chat/", { message });
      console.log("CHATBOT RESPONSE:", response.data);
      const botReply = response.data.reply || response.data.response || "No reply from chatbot";
      setChatMessages([...newMessages, { from: "bot", text: botReply }]);
    } catch (err) {
      console.error("Chatbot error:", err.response?.data || err.message);
      setChatMessages([...newMessages, { from: "bot", text: "Error connecting to chatbot" }]);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side: Classy Awareness Section */}
      <div className="hidden md:flex md:w-1/2 bg-gradient-to-br from-pink-50 via-rose-50 to-pink-100 p-12 flex-col justify-center text-gray-900 relative overflow-hidden shadow-[inset_-10px_0_30px_rgba(0,0,0,0.02)]">
        {/* Decorative elements */}
        <div className="absolute top-0 left-0 w-64 h-64 bg-pink-300 opacity-20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-rose-300 opacity-20 rounded-full blur-3xl translate-x-1/3 translate-y-1/3"></div>

        <div className="relative z-10 max-w-lg mx-auto">
          <span className="inline-block py-1 px-4 rounded-full bg-pink-200/50 border border-pink-300 text-pink-700 text-sm font-bold tracking-wider uppercase mb-6 shadow-sm">Welcome to MCIDS</span>
          <h1 className="text-4xl lg:text-5xl font-extrabold leading-tight mb-6 tracking-tight text-gray-900">
            Empower Your Menstrual Health
          </h1>
          <p className="text-lg text-gray-600 mb-12 leading-relaxed font-medium">
            Gain personalized insights into your cycle, detect irregularities early, and explore cycle-synced diet plans designed to perfectly nourish your body at every single phase.
          </p>
          
          <div className="space-y-6">
            <div className="bg-white/60 backdrop-blur-md border border-pink-200 p-6 rounded-2xl shadow-lg hover:bg-white/90 hover:-translate-y-1 transition duration-300">
              <h3 className="text-xl font-bold mb-3 flex items-center text-rose-600">
                <span className="text-2xl mr-3">🩸</span> Menstruation Phase Guidance
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed font-medium">Focus heavily on iron-rich foods like dark leafy greens, lentils, and dark chocolate to replenish nutrients and soothe cramping naturally.</p>
            </div>
            <div className="bg-white/60 backdrop-blur-md border border-pink-200 p-6 rounded-2xl shadow-lg hover:bg-white/90 hover:-translate-y-1 transition duration-300">
              <h3 className="text-xl font-bold mb-3 flex items-center text-indigo-600">
                <span className="text-2xl mr-3">✨</span> Luteal Phase (PMS) Care
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed font-medium">Increase your magnesium intake with nuts, seeds, and bananas to manage mood swings, stabilize energy, and reduce uncomfortable bloating.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right side: Login Form */}
      <div className="w-full md:w-1/2 flex flex-col items-center justify-center bg-gray-50 px-6 sm:px-12 py-12">
        <form
          onSubmit={handleSubmit}
          className="bg-white p-10 rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] w-full max-w-md border border-gray-100"
        >
          <div className="mb-10 text-center">
            <div className="w-16 h-16 mx-auto bg-gradient-to-br from-pink-500 to-rose-600 rounded-2xl mb-6 flex items-center justify-center shadow-lg shadow-pink-500/30">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-3xl font-extrabold text-gray-900 mb-2">Welcome Back</h2>
            <p className="text-gray-500 font-medium">Sign in to continue your health journey.</p>
          </div>

          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-xl text-sm mb-8 text-center border border-red-100 font-medium">
              {error}
            </div>
          )}

          <div className="mb-6">
            <label className="block text-sm font-bold text-gray-700 mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
                setError("");
              }}
              className="w-full px-4 py-3.5 border border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-500/20 focus:border-pink-500 outline-none transition-all font-medium"
              placeholder="Enter your username"
              required
            />
          </div>

          <div className="mb-8">
            <label className="block text-sm font-bold text-gray-700 mb-2">Password</label>

            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={handlePasswordChange}
                className={`w-full px-4 py-3.5 border border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-500/20 focus:border-pink-500 outline-none transition-all pr-12 font-medium ${passwordError ? "border-red-500 focus:ring-red-500/20 focus:border-red-500" : ""
                  }`}
                placeholder="••••••••"
                required
              />

              <button
                type="button"
                onClick={() => setShowPassword((p) => !p)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-bold text-gray-400 hover:text-pink-600 transition"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>

            {passwordError && (
              <p className="text-red-500 text-xs mt-2 font-semibold">{passwordError}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-4 rounded-xl font-bold text-white text-lg transition-all ${loading ? "bg-pink-300 cursor-not-allowed shadow-none" : "bg-gradient-to-r from-pink-600 to-rose-600 hover:shadow-lg hover:shadow-pink-500/40 hover:-translate-y-0.5 active:translate-y-0"
              }`}
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>

          <p className="text-center text-sm mt-8 text-gray-600 font-medium">
            Don't have an account?{" "}
            <span
              className="text-pink-600 font-bold hover:underline cursor-pointer"
              onClick={() => navigate("/signup")}
            >
              Sign up
            </span>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Login;