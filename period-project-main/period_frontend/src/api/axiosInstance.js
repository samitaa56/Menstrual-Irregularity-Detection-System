import axios from "axios";
import { API_BASE_URL } from "../config";

// Create a single Axios instance
const axiosInstance = axios.create({
  baseURL: API_BASE_URL, // Django backend base URL
  headers: {
    "Content-Type": "application/json",
  },
});

// Optional: Add request interceptor for auth token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token"); // or your auth storage
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Optional: Add response interceptor for global error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default axiosInstance;