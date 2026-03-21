import axios from "axios";
import { API_BASE_URL } from "../config";

const API_URL = API_BASE_URL;

export const signup = async (username, email, password) => {
    try {
        await axios.post(`${API_URL}/signup/`, {
            username,
            email,
            password,
        });
        return { success: true };
    } catch (error) {
        if (!error.response) {
            // No response from server = Network Error
            return { 
                success: false, 
                message: "Network Error: Cannot connect to the server. Please ensure the backend is running with 'runserver 0.0.0.0:8000' and your IP is correct in config.js." 
            };
        }

        const message = error.response?.data?.error || 
                        error.response?.data?.email?.[0] || 
                        error.response?.data?.username?.[0] || 
                        "Unable to create account. Please try again.";
        console.error("Signup error:", message);
        return { success: false, message };
    }
};
