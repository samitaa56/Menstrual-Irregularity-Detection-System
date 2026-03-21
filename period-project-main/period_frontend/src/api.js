// src/api.js
import axios from "axios";

import { API_BASE_URL } from "./config";

const api = axios.create({
    baseURL: API_BASE_URL,
});

// Attach JWT Token if exists
api.interceptors.request.use((config) => {
    const token = localStorage.getItem("access");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;
