import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { API_BASE_URL } from "../config";

const API_URL = API_BASE_URL;

// ✅ Cycle status (rule-based, not AI)
const getCycleStatus = (avgCycleLength, variation) => {
  if (avgCycleLength === null || avgCycleLength === undefined)
    return "Insufficient Data";

  const inRange = avgCycleLength >= 21 && avgCycleLength <= 35;
  const stable = (variation ?? 999) <= 7;

  return inRange && stable ? "Regular Cycle" : "Irregular Cycle";
};

const MEDICAL_DEFINITIONS = {
  Amenorrhea: "Missed periods for 3 or more months. This can be caused by stress, significant weight changes, or underlying conditions like PCOS.",
  Polymenorrhea: "Menstrual cycles that occur more frequently than every 21 days.",
  Oligomenorrhea: "Infrequent periods where the cycle length is longer than 35 days (fewer than 9 periods a year).",
  Menorrhagia: "Heavy or prolonged menstrual bleeding, typically lasting more than 7 days or requiring very frequent pad/tampon changes.",
  "Intermenstrual Bleeding": "Bleeding or spotting that occurs between your regular menstrual periods.",
};

const Results = () => {
  const { state } = useLocation();
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  /* ===============================
     Safety Check
  =============================== */
  if (!state?.result || !state?.inputData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg text-red-600">No results found</p>
      </div>
    );
  }

  /* ===============================
     Extract backend results
  =============================== */
  const {
    prediction_status: irregularity_prediction,
    chance_of_irregularity,
    irregularity_type = null,
    avg_cycle_length,
    cycle_length_variation,
    cycle_variation_coefficient,
    pattern_disruption_score,
    next_cycle_prediction,
    cycle_status: backendCycleStatus,
  } = state.result;

  const cycleStatus =
    backendCycleStatus || getCycleStatus(avg_cycle_length, cycle_length_variation);

  const roundedNextCycle =
    next_cycle_prediction === null || next_cycle_prediction === undefined
      ? null
      : Math.round(
        Array.isArray(next_cycle_prediction)
          ? next_cycle_prediction[0]
          : next_cycle_prediction
      );

  const inputData = state.inputData;

  const token =
    localStorage.getItem("access") ||
    localStorage.getItem("access_token") ||
    localStorage.getItem("token");

  /* ===============================
     Save Cycle
  =============================== */
  const handleSaveCycle = async () => {
    setSaving(true);
    setError("");

    if (!token) {
      setError("Authentication token missing. Please login again.");
      setSaving(false);
      return;
    }

    const savePayload = {
      age: inputData.age,
      height: inputData.height || state.result.height,
      weight: inputData.weight || state.result.weight,
      bmi: inputData.bmi || state.result.bmi,
      life_stage: inputData.life_stage,
      tracking_duration: inputData.tracking_duration,
      pain_score: inputData.pain_score,

      avg_cycle_length,
      cycle_length_variation,
      cycle_variation_coefficient,
      pattern_disruption_score,

      avg_bleeding_days: inputData.avg_bleeding_days,
      bleeding_volume_score: inputData.bleeding_volume_score,
      missed_periods: inputData.missed_periods || 0,

      irregularity_prediction,
      irregularity_probability: chance_of_irregularity,
      irregularity_type,
      next_cycle_prediction: roundedNextCycle,
    };

    try {
      await axios.post(`${API_URL}/cycles/save/`, savePayload, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      navigate("/symptoms");
    } catch (err) {
      console.error(err.response?.data || err.message);
      if (err.response && err.response.data) {
        const data = err.response.data;
        if (data.error) setError(data.error);
        else if (data.detail) setError(data.detail);
        else setError(JSON.stringify(data));
      } else {
        setError("Failed to save cycle");
      }
    } finally {
      setSaving(false);
    }
  };

  /* ===============================
     Insights Logic
  =============================== */
  const getInsight = () => {
    if (irregularity_prediction !== "Irregular") {
      return "Your metrics look great! Keep maintaining a balanced diet, staying hydrated, and tracking your cycles regularly.";
    }

    if (irregularity_type === "Amenorrhea") {
      return "Amenorrhea (missed periods) can be influenced by stress, diet, or deeper hormonal imbalances like PCOS. Consider consulting a healthcare provider if this persists, and focus on stress-reduction techniques.";
    }
    if (irregularity_type === "Oligomenorrhea") {
      return "Oligomenorrhea means your cycles are longer than normal. Ensure you are getting adequate nutrition and screen for potential thyroid or PCOS factors with a doctor.";
    }
    if (irregularity_type === "Polymenorrhea") {
      return "Frequent periods can lead to iron deficiency (anemia). Be sure to increase your intake of iron-rich foods like spinach, lentils, and red meat.";
    }
    if (irregularity_type === "Menorrhagia") {
      return "Heavy bleeding depletes iron quickly. Rest during your heaviest days, stay hydrated, and eat dark leafy greens. Consult a doctor to rule out fibroids or polyps.";
    }
    if (irregularity_type === "Intermenstrual Bleeding") {
      return "Spotting between periods can happen due to ovulation or hormonal fluctuations, but if it happens frequently, it is highly recommended to get a routine checkup.";
    }

    if (cycleStatus === "Regular Cycle") {
      return "Your cycle timing is regular, but your reported symptoms suggest a potential symptom-based irregularity. Consider noting your fatigue or pain levels closely.";
    }

    return "Your analysis indicates an irregularity. Focus on holistic rest, balanced nutrition, and consider discussing these results with a healthcare professional.";
  };

  const insight = getInsight();

  /* ===============================
     UI
  =============================== */
  return (
    <div className="min-h-screen bg-pink-50 p-6 flex justify-center items-start pt-12">
      <div className="max-w-xl w-full bg-white p-10 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-pink-100">
        <div className="flex items-center justify-center mb-6">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center shadow-lg ${irregularity_prediction === "Irregular" ? "bg-rose-100 text-rose-500" : "bg-emerald-100 text-emerald-500"}`}>
            {irregularity_prediction === "Irregular" ? (
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            ) : (
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
        </div>

        <h1 className="text-3xl font-extrabold mb-8 text-center text-gray-900 tracking-tight">
          AI Prediction Results
        </h1>

        <div className="bg-gray-50 rounded-xl p-6 mb-6 border border-gray-100 space-y-4 shadow-[inset_0_2px_10px_rgb(0,0,0,0.02)]">
          {/* Cycle Status */}
          <div className="flex justify-between items-center border-b border-gray-200 pb-3">
            <span className="font-semibold text-gray-700 flex items-center">
              Cycle Status
              <span title="Based on your PAST data history timing." className="ml-2 cursor-help text-gray-400">ⓘ</span>
            </span>
            <span className={`font-bold px-3 py-1 rounded-full text-sm ${cycleStatus === "Regular Cycle" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
              {cycleStatus}
            </span>
          </div>

          {/* AI Health Status */}
          <div className="flex justify-between items-center border-b border-gray-200 pb-3">
            <span className="font-semibold text-gray-700 flex items-center">
              AI Health Status
              <span title="AI Prediction of your current cycle health." className="ml-2 cursor-help text-gray-400">ⓘ</span>
            </span>
            <span className={`font-bold px-3 py-1 rounded-full text-sm ${irregularity_prediction === "Irregular" ? "bg-rose-100 text-rose-700" : "bg-emerald-100 text-emerald-700"}`}>
              {irregularity_prediction}
            </span>
          </div>

          {/* ✅ FIXED: Only show irregularity types when prediction is Irregular */}
          {irregularity_type && irregularity_prediction === "Irregular" && (
            <div className="flex flex-col pt-2 mt-2">
              <span className="font-semibold text-gray-700 mb-2">Detected Cycle Irregularity Types:</span>
              <div className="space-y-3">
                {irregularity_type.split(',').map((typeLabel, index) => {
                  const type = typeLabel.trim();
                  return (
                    <div
                      key={index}
                      className="font-semibold p-4 rounded-lg shadow-sm border flex flex-col sm:flex-row sm:items-center justify-between transition-colors bg-gradient-to-r from-rose-50 to-pink-50 border-rose-200 text-rose-800"
                    >
                      <span className="text-lg tracking-wide">{type}</span>
                      {MEDICAL_DEFINITIONS[type] && (
                        <p className="text-sm mt-2 sm:mt-0 sm:ml-4 sm:max-w-xs md:max-w-md rounded p-2 leading-relaxed bg-white/60 text-rose-700">
                          {MEDICAL_DEFINITIONS[type]}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Next Cycle */}
        <p className="mb-4">
          <strong>
            Predicted Next Cycle
            <span
              title="This is an AI estimate for your upcoming cycle. For irregular patterns, we provide an expected range based on your variation history."
              className="ml-1 cursor-help text-gray-500"
            >
              ⓘ
            </span>
            :
          </strong>{" "}
          {roundedNextCycle === null ? (
            "N/A"
          ) : (
            <span className="font-semibold text-gray-800">
              {roundedNextCycle} days
            </span>
          )}
        </p>

        {error && <p className="text-red-600 text-center my-3">{error}</p>}

        <button
          onClick={handleSaveCycle}
          disabled={saving}
          className="w-full bg-green-600 text-white py-2 rounded mb-3 hover:bg-green-700 disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save Cycle"}
        </button>

        <button
          onClick={() => navigate("/predict")}
          className="w-full bg-pink-600 text-white py-2 rounded hover:bg-pink-700"
        >
          Predict Again
        </button>
      </div>
    </div>
  );
};

export default Results;
