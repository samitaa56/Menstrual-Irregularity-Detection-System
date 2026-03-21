import React, { useMemo, useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config";

const API_BASE = API_BASE_URL;

function AddCycleHistory() {
    const navigate = useNavigate();

    const [cycleLengthsText, setCycleLengthsText] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [successMsg, setSuccessMsg] = useState("");
    const [cycleCount, setCycleCount] = useState(null);

    // fetch existing cycle count and redirect if already enough
    useEffect(() => {
        const token =
            localStorage.getItem("access") ||
            localStorage.getItem("access_token") ||
            localStorage.getItem("token");
        if (!token) return;

        fetch(`${API_BASE}/cycles/`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((r) => r.json())
            .then((data) => {
                if (Array.isArray(data)) {
                    setCycleCount(data.length);
                    if (data.length >= 2) {
                        // already has history, send back to predict
                        navigate("/predict");
                    }
                }
            })
            .catch((e) => console.error("failed to load cycles", e));
    }, [navigate]);

    // ✅ Better parsing
    const parseCycleLengths = (text) => {
        return text
            .split(",")
            .map((v) => v.trim())
            .filter((v) => v !== "") // remove empty parts like ",,"
            .map((v) => Number(v))
            .filter((v) => Number.isFinite(v) && v >= 15 && v <= 120);
    };

    // ✅ Optional: show preview (helps user)
    const parsedPreview = useMemo(
        () => parseCycleLengths(cycleLengthsText),
        [cycleLengthsText]
    );

    // ✅ Better error extraction from DRF
    const getErrorMessage = (data) => {
        if (!data) return null;

        if (typeof data === "string") return data;
        if (data.error) return data.error;
        if (data.detail) return data.detail;

        // DRF field errors: {cycle_lengths: ["msg"]}
        const firstKey = Object.keys(data)[0];
        if (firstKey) {
            const val = data[firstKey];
            if (Array.isArray(val)) return val[0];
            if (typeof val === "string") return val;
        }

        return null;
    };

    const handleSave = async (e) => {
        e.preventDefault();
        setError("");
        setSuccessMsg("");

        const cycleLengths = parseCycleLengths(cycleLengthsText);

        if (cycleLengths.length < 2) {
            setError("Please enter at least 2 valid cycle lengths (e.g. 28,30).");
            return;
        }

        const token =
            localStorage.getItem("access") ||
            localStorage.getItem("access_token") ||
            localStorage.getItem("token");

        if (!token) {
            setError("You must login first.");
            return;
        }

        setLoading(true);
        try {
            await axios.post(
                `${API_BASE}/cycles/history/`,
                { cycle_lengths: cycleLengths },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                }
            );

            setSuccessMsg("✅ Cycle history saved! Now you can predict.");
            setTimeout(() => navigate("/predict"), 800);
        } catch (err) {
            console.error(err.response?.data || err.message);

            const msg =
                getErrorMessage(err.response?.data) ||
                "Failed to save history. Please try again.";

            setError(msg);

            // ✅ If token expired / invalid, send to login
            if (
                msg.toLowerCase().includes("token") ||
                msg.toLowerCase().includes("authentication")
            ) {
                // optional auto-redirect:
                // setTimeout(() => navigate("/login"), 800);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-pink-50 flex items-center justify-center p-6">
            <div className="bg-white w-full max-w-xl p-8 rounded-xl shadow">
                <h1 className="text-2xl font-bold text-center mb-2">
                    Add Cycle History
                </h1>
                <p className="text-center text-gray-600 mb-6">
                    Enter at least 2 previous cycle lengths. Example: <b>28,30</b>
                </p>

                {error && <p className="text-red-600 text-center mb-4">{error}</p>}
                {successMsg && (
                    <p className="text-green-600 text-center mb-4">{successMsg}</p>
                )}

                {/* ✅ Optional preview */}
                {cycleLengthsText.trim() && (
                    <p className="text-center text-sm text-gray-600 mb-3">
                        Parsed: <b>[{parsedPreview.join(", ")}]</b>
                    </p>
                )}

                <form onSubmit={handleSave} className="space-y-4">
                    <div>
                        <label className="font-semibold text-gray-700 block mb-1">
                            Cycle Lengths (days)
                        </label>
                        <input
                            value={cycleLengthsText}
                            onChange={(e) => setCycleLengthsText(e.target.value)}
                            placeholder="e.g. 28,30,27"
                            className="w-full p-3 border rounded-lg outline-none focus:ring focus:ring-pink-200"
                            required
                        />
                        <p className="text-sm text-gray-500 mt-1">
                            Valid range: 15 to 120 days
                        </p>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full text-white p-3 rounded-lg font-semibold ${loading ? "bg-gray-400" : "bg-green-600 hover:bg-green-700"
                            }`}
                    >
                        {loading ? "Saving..." : "Save History"}
                    </button>

                    <button
                        type="button"
                        onClick={() => navigate("/predict")}
                        className="w-full p-3 rounded-lg font-semibold border"
                    >
                        Back to Predict
                    </button>
                </form>
            </div>
        </div>
    );
}

export default AddCycleHistory;
