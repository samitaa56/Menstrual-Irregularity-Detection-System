import React, { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../config";

const Reports = () => {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchReports = async () => {
            try {
                const token = localStorage.getItem("access");

                const res = await axios.get(
                    `${API_BASE_URL}/reports/`,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    }
                );

                setReports(res.data);
            } catch (err) {
                console.error("Failed to load reports", err);
            } finally {
                setLoading(false);
            }
        };

        fetchReports();
    }, []);

    // Logic to determine cycle status (timing-based)
    const getCycleStatus = (avg, variation) => {
        if (avg === null || avg === undefined) return null;
        const inRange = avg >= 21 && avg <= 35;
        // Updated threshold to 7 days for clinical regularity
        const stable = (variation ?? 999) <= 7;
        return inRange && stable ? "Regular Cycle" : "Irregular Cycle";
    };

    // Logic to determine health insight
    const getInsight = (cycleStatus, prediction) => {
        if (cycleStatus === "Regular Cycle" && prediction === "Irregular") {
            return "Your cycle timing is regular, but your reported symptoms suggest a potential health irregularity.";
        }
        if (cycleStatus === "Irregular Cycle" && prediction === "Regular") {
            return "Your cycle timing is outside the normal range, though symptoms didn't match clinical irregularity patterns.";
        }
        return null;
    };

    // Logic to determine pain label from score
    const getPainLabel = (score) => {
        if (score === null || score === undefined) return "N/A";
        if (score <= 1) return "Low";
        if (score <= 3) return "Moderate";
        return "Severe";
    };

    // BMI category with color coding
    const getBmiInfo = (bmi) => {
        if (bmi === null || bmi === undefined) return { label: "N/A", color: "text-gray-500" };
        if (bmi < 18.5) return { label: `${bmi} – Underweight`, color: "text-blue-600" };
        if (bmi < 25) return { label: `${bmi} – Healthy Weight`, color: "text-green-600" };
        if (bmi < 30) return { label: `${bmi} – Overweight`, color: "text-yellow-600" };
        if (bmi < 35) return { label: `${bmi} – Obese (Class I)`, color: "text-orange-500" };
        if (bmi < 40) return { label: `${bmi} – Obese (Class II)`, color: "text-red-500" };
        return { label: `${bmi} – Severe Obesity`, color: "text-red-700" };
    };

    if (loading) {
        return <p className="text-center mt-10">Loading reports...</p>;
    }

    if (reports.length === 0) {
        return <p className="text-center mt-10">No reports found</p>;
    }

    return (
        <div className="min-h-screen bg-pink-50 p-6">
            <h1 className="text-3xl font-bold text-center mb-8">
                Previous Reports
            </h1>

            <div className="max-w-4xl mx-auto space-y-8">
                {reports.map((r, index) => {
                    const cycleStatus = getCycleStatus(r.avg_cycle_length, r.cycle_length_variation);
                    const insight = getInsight(cycleStatus, r.irregularity_prediction);
                    const cycleNumber = index + 1; // Sequential numbering: 1, 2, 3...

                    return (
                        <div key={r.id} className="bg-white rounded-2xl shadow-lg overflow-hidden border border-pink-100">
                            {/* HEADER */}
                            <div className="bg-pink-600 p-4 text-white flex justify-between items-center">
                                <h2 className="text-xl font-bold">Cycle #{cycleNumber}</h2>
                                <span className="opacity-90">{new Date(r.created_at).toLocaleDateString()}</span>
                            </div>

                            <div className="p-6 space-y-6">
                                {/* TOP SUMMARY */}
                                <div className="flex flex-wrap gap-4 border-b border-gray-100 pb-4">
                                    <div className="flex-1 min-w-[150px]">
                                        <p className="text-xs text-gray-500 uppercase font-bold tracking-wider">Cycle Timing</p>
                                        <p className={`text-lg font-semibold ${cycleStatus === "Regular Cycle" ? "text-green-600" : "text-red-600"}`}>
                                            {cycleStatus || "N/A"}
                                        </p>
                                    </div>
                                    <div className="flex-1 min-w-[150px]">
                                        <p className="text-xs text-gray-500 uppercase font-bold tracking-wider">Health Status (AI)</p>
                                        <p className={`text-lg font-semibold ${r.irregularity_prediction === "Irregular" ? "text-red-600" : "text-green-600"}`}>
                                            {r.irregularity_prediction || "N/A"}
                                        </p>
                                    </div>
                                </div>

                                {/* INSIGHT BOX */}
                                {insight && (
                                    <div className="bg-blue-50 p-4 rounded-xl border-l-4 border-blue-400 text-blue-800 text-sm italic">
                                        <strong>Health Insight:</strong> {insight}
                                    </div>
                                )}

                                {/* DATA GRIDS */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                    {/* COLUMN 1: YOUR ENTRIES */}
                                    <div>
                                        <h3 className="text-sm font-bold text-gray-400 uppercase mb-3 border-b border-gray-50 pb-1">Your Entries</h3>
                                        <div className="space-y-2 text-sm">
                                            <p className="flex justify-between"><span>Age:</span> <span className="font-medium">{r.age ?? "N/A"}</span></p>
                                            <p className="flex justify-between"><span>Height:</span> <span className="font-medium">{r.height ?? "N/A"} cm</span></p>
                                            <p className="flex justify-between"><span>Weight:</span> <span className="font-medium">{r.weight ?? "N/A"} kg</span></p>
                                            <p className="flex justify-between"><span>Life Stage:</span> <span className="font-medium capitalize">{r.life_stage ?? "N/A"}</span></p>
                                            <p className="flex justify-between"><span>Bleeding Duration:</span> <span className="font-medium">{r.avg_bleeding_days ?? "N/A"} days</span></p>
                                            <p className="flex justify-between"><span>Menstrual Pain Level:</span> <span className="font-medium capitalize">{getPainLabel(r.pain_score)}</span></p>
                                            <p className="flex justify-between"><span>Missed Periods (last 12 months):</span> <span className="font-medium">{r.missed_periods ?? "N/A"}</span></p>
                                        </div>
                                    </div>

                                    {/* COLUMN 2: CLINICAL METRICS (Calculated) */}
                                    <div>
                                        <h3 className="text-sm font-bold text-gray-400 uppercase mb-3 border-b border-gray-50 pb-1">Analysis Metrics</h3>
                                        <div className="space-y-2 text-sm text-gray-600">
                                            <p className="flex justify-between"><span>Calculated BMI:</span> <span className={`font-medium ${getBmiInfo(r.bmi).color}`}>{getBmiInfo(r.bmi).label}</span></p>
                                            <p className="flex justify-between"><span>Avg Cycle Length:</span> <span className="font-medium text-black">{r.avg_cycle_length ?? "N/A"} d</span></p>
                                            <p className="flex justify-between"><span>Next Cycle Prediction:</span> <span className="font-medium text-black">{r.next_cycle_prediction ?? "N/A"} d</span></p>
                                        </div>
                                    </div>
                                </div>

                                {/* SYMPTOMS */}
                                <div className="pt-4 border-t border-gray-50">
                                    <h3 className="text-sm font-bold text-gray-400 uppercase mb-2">Recorded Symptoms</h3>
                                    {r.symptoms.length === 0 ? (
                                        <p className="text-xs text-gray-400 italic">No symptoms recorded for this cycle.</p>
                                    ) : (
                                        <div className="flex flex-wrap gap-2">
                                            {r.symptoms.map((s, i) => (
                                                <span key={i} className="bg-pink-50 text-pink-700 px-3 py-1 rounded-full text-xs font-medium border border-pink-100">
                                                    {s.symptom_name} ({s.severity})
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* FOOTER NOTE FOR MANUAL RECORDS */}
                            {!r.irregularity_prediction && (
                                <div className="bg-gray-50 p-2 text-center text-[10px] text-gray-400 uppercase tracking-widest">
                                    Manual History Record • No AI Analysis
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default Reports;
