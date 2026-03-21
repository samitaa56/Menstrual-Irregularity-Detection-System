import axios from "axios";
import { API_BASE_URL } from "../config";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// -------------------------
// Predict Irregularity API
// -------------------------
export const predictIrregularity = async (data) => {
  try {
    const token = localStorage.getItem("access");

    const headers = token
      ? { Authorization: `Bearer ${token}` }
      : {};

    const res = await apiClient.post("/predict/", data, { headers });

    return res.data;
  } catch (err) {
    console.error("❌ Predict Error:", err.response?.data || err.message);

    // 🔥 Show real backend error if available
    const message =
      err.response?.data?.error ||
      JSON.stringify(err.response?.data) ||
      "Prediction failed. Please check inputs or backend.";

    throw new Error(message);
  }
};

export default apiClient;
