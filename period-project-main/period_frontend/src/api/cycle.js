import axios from "axios";
import { API_BASE_URL } from "../config";

const API = API_BASE_URL;

// ⭐ Save Cycle Data (Prediction + Input)
export const saveCycleData = async (data, token) => {
    try {
        const response = await axios.post(`${API}/save-cycle/`, data, {
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
        });
        return response.data;
    } catch (error) {
        console.error("❌ Error saving cycle:", error.response?.data || error);
        throw error;
    }
};

// ⭐ Get List of Saved Cycles (Dropdown in SymptomsPage)
export const getCycles = async (token) => {
    try {
        const response = await axios.get(`${API}/cycles/`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        return response.data;
    } catch (error) {
        console.error("❌ Error fetching cycles:", error.response?.data || error);
        throw error;
    }
};
