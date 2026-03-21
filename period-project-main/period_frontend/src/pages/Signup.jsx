// src/pages/Signup.jsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { signup } from "../services/authService";

const Signup = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [error, setError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [emailError, setEmailError] = useState("");
  const [loading, setLoading] = useState(false);

  // ✅ Email validation function
  const validateEmail = (value) => {
    // Stricter regex ensuring valid domain characters and a top-level domain of at least 2 characters
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(value)) {
      return "Please enter a valid email address (e.g., name@example.com)";
    }
    return "";
  };

  // ✅ Password validation function
  const validatePassword = (value) => {
    if (value.length < 8)
      return "Password must be at least 8 characters long";
    if (!/[A-Za-z]/.test(value))
      return "Password must contain at least one letter";
    if (!/\d/.test(value))
      return "Password must contain at least one number";
    if (!/[@$!%*#?&]/.test(value))
      return "Password must contain at least one special character (@$!%*#?&)";
    return "";
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData({ ...formData, [name]: value });
    setError("");

    if (name === "password") {
      const msg = validatePassword(value);
      setPasswordError(msg);
    }

    if (name === "email") {
      const msg = validateEmail(value);
      setEmailError(msg);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // ✅ Password validation
    const pwdError = validatePassword(formData.password);
    setPasswordError(pwdError);
    if (pwdError) return;

    // ✅ Email validation
    const emError = validateEmail(formData.email);
    setEmailError(emError);
    if (emError) return;

    // ✅ Confirm password check
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);

    const result = await signup(
      formData.username,
      formData.email,
      formData.password
    );

    setLoading(false);

    if (!result.success) {
      setError(result.message || "Unable to create account. Please try a different username or email.");
      return;
    }

    // ✅ Show verification message
    alert(`✅ Account created! \n\nA verification email has been sent to ${formData.email}.\n\nPlease check your email and click the verification link to activate your account before logging in.`);

    navigate("/login");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white p-8 rounded-xl shadow">
        <h2 className="text-3xl font-bold text-center mb-6">
          Create Account
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            className="w-full border p-3 rounded"
            required
          />

          <input
            name="email"
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            className={`w-full border p-3 rounded ${emailError ? "border-red-500" : ""}`}
            required
          />

          {/* 🔴 Email validation error */}
          {emailError && (
            <p className="text-red-600 text-sm">{emailError}</p>
          )}

          <input
            name="password"
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            className={`w-full border p-3 rounded ${passwordError ? "border-red-500" : ""
              }`}
            required
          />

          {/* 🔴 Password rule error */}
          {passwordError && (
            <p className="text-red-600 text-sm">{passwordError}</p>
          )}

          <input
            name="confirmPassword"
            type="password"
            placeholder="Confirm Password"
            value={formData.confirmPassword}
            onChange={handleChange}
            className="w-full border p-3 rounded"
            required
          />

          {error && (
            <p className="text-red-600 text-sm text-center">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-pink-600 text-white p-3 rounded disabled:bg-pink-300"
          >
            {loading ? "Creating..." : "Create Account"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm">
          Already have an account?{" "}
          <Link to="/login" className="text-pink-600 font-medium">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Signup;
