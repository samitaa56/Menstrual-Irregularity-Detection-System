import axios from "axios";
import { createContext, useContext, useEffect, useState } from "react";
import { API_BASE_URL } from "../config";

const AuthContext = createContext();
const API_URL = API_BASE_URL;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // =========================
  // Restore session on reload
  // =========================
  useEffect(() => {
    const token = localStorage.getItem("access");
    const username = localStorage.getItem("username");

    if (token && username) {
      setUser({ username });
    } else {
      setUser(null);
    }

    setLoading(false);
  }, []);

  // =========================
  // LOGIN
  // =========================
  const login = async (username, password) => {
    try {
      setLoading(true);

      const res = await axios.post(`${API_URL}/auth/login/`, {
        username,
        password,
      });

      localStorage.setItem("access", res.data.access);
      localStorage.setItem("refresh", res.data.refresh);
      localStorage.setItem("username", username);

      setUser({ username });
      return true;
    } catch (error) {
      console.error("Login failed:", error.response?.data || error.message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // SIGNUP
  // =========================
  const signup = async (username, email, password) => {
    try {
      setLoading(true);
      await axios.post(`${API_URL}/signup/`, {
        username,
        email,
        password,
      });
      return true;
    } catch (error) {
      console.error("Signup failed:", error.response?.data || error.message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // LOGOUT
  // =========================
  const logout = () => {
    localStorage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
