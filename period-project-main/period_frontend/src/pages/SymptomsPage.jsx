import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config";

const API_URL = API_BASE_URL;

const SymptomsPage = () => {
    const navigate = useNavigate();

    const [cycles, setCycles] = useState([]);
    const [cycleId, setCycleId] = useState("");
    const [severity, setSeverity] = useState("mild");
    const [selectedSymptoms, setSelectedSymptoms] = useState([]);
    const [date, setDate] = useState(
        new Date().toISOString().split("T")[0] // ✅ REQUIRED
    );
    const [message, setMessage] = useState("");

    const symptomOptions = [
        { key: "Cramps", icon: "🤕" },
        { key: "Headache", icon: "🤯" },
        { key: "Bloating", icon: "🤰" },
        { key: "Acne", icon: "🌸" },
        { key: "Back Pain", icon: "💢" },
        { key: "Fatigue", icon: "😴" },
        { key: "Nausea", icon: "🤢" },
        { key: "Mood Swings", icon: "😡" },
    ];

    const token = localStorage.getItem("access");

    // =========================
    // Fetch cycles
    // =========================
    useEffect(() => {
        const fetchCycles = async () => {
            try {
                const res = await axios.get(`${API_URL}/cycles/`, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                setCycles(res.data);
            } catch {
                setMessage("❌ Failed to load cycles");
            }
        };

        fetchCycles();
    }, [token]);

    const toggleSymptom = (symptom) => {
        setSelectedSymptoms((prev) =>
            prev.includes(symptom)
                ? prev.filter((s) => s !== symptom)
                : [...prev, symptom]
        );
    };

    // =========================
    // Save symptoms
    // =========================
    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage("");

        if (!cycleId) return setMessage("⚠ Please select a cycle");
        if (!date) return setMessage("⚠ Please select date");
        if (selectedSymptoms.length === 0)
            return setMessage("⚠ Select at least one symptom");

        try {
            await Promise.all(
                selectedSymptoms.map((symptom) =>
                    axios.post(
                        `${API_URL}/symptoms/`,
                        {
                            cycle: cycleId,
                            date: date,                 // ✅ REQUIRED
                            symptom_name: symptom,      // ✅ MATCHES MODEL
                            severity: severity,
                        },
                        {
                            headers: {
                                Authorization: `Bearer ${token}`,
                                "Content-Type": "application/json",
                            },
                        }
                    )
                )
            );

            setMessage("✅ Symptoms saved successfully!");
            setSelectedSymptoms([]);
            setTimeout(() => navigate("/dashboard"), 1200);
        } catch (err) {
            console.error(err.response?.data || err.message);
            setMessage("❌ Failed to save symptoms");
        }
    };

    return (
        <div className="min-h-screen bg-pink-50 p-6">
            <div className="max-w-xl mx-auto bg-white shadow-lg rounded-xl p-8">
                <h2 className="text-3xl font-bold text-pink-600 text-center mb-6">
                    Track Symptoms
                </h2>

                {message && (
                    <div className="mb-4 p-3 text-center bg-pink-100 text-pink-800 rounded">
                        {message}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">

                    {/* Cycle */}
                    <select
                        className="w-full border rounded p-2"
                        value={cycleId}
                        onChange={(e) => setCycleId(e.target.value)}
                    >
                        <option value="">-- Select Cycle --</option>
                        {cycles.map((cycle) => (
                            <option key={cycle.id} value={cycle.id}>
                                {cycle.label}
                            </option>
                        ))}
                    </select>

                    {/* Date */}
                    <input
                        type="date"
                        className="w-full border rounded p-2"
                        value={date}
                        onChange={(e) => setDate(e.target.value)}
                    />

                    {/* Symptoms */}
                    <div className="grid grid-cols-2 gap-2">
                        {symptomOptions.map((sym) => (
                            <label key={sym.key} className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    checked={selectedSymptoms.includes(sym.key)}
                                    onChange={() => toggleSymptom(sym.key)}
                                />
                                {sym.icon} {sym.key}
                            </label>
                        ))}
                    </div>

                    {/* Severity */}
                    <div className="space-y-1">
                        <label className="text-sm font-semibold text-gray-700">
                            Select Symptom Severity:
                        </label>
                        <select
                            className="w-full border rounded p-2"
                            value={severity}
                            onChange={(e) => setSeverity(e.target.value)}
                        >
                            <option value="mild">Mild</option>
                            <option value="moderate">Moderate</option>
                            <option value="severe">Severe</option>
                        </select>
                    </div>

                    <button className="w-full bg-pink-600 text-white py-3 rounded">
                        Save Symptoms
                    </button>
                </form>
            </div>
        </div>
    );
};

export default SymptomsPage;
