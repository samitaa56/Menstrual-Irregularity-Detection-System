import React, { useState, useEffect } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config";

const API_BASE = API_BASE_URL; // keep in sync with other files

function PredictForm() {
  const navigate = useNavigate();
  const username = localStorage.getItem("username");

  const [formData, setFormData] = useState({
    age: "", height: "", weight: "", life_stage: "", tracking_duration: "",
    pain_level: "", avg_bleeding_days: "", flow_intensity: "", intermenstrual_episodes: "0",
    missed_periods: "0",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [cycleCount, setCycleCount] = useState(null);

  useEffect(() => {
    const token =
      localStorage.getItem("access") ||
      localStorage.getItem("access_token") ||
      localStorage.getItem("token");
    if (!token) return;

    fetch(`${API_BASE}/cycles/?include_history=true`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data)) setCycleCount(data.length);
      })
      .catch((e) => console.error("failed to fetch cycles", e));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    let updatedForm = { ...formData, [name]: value };

    // Automatically set life_stage based on age
    if (name === "age") {
      const ageNum = parseInt(value, 10);
      if (!isNaN(ageNum)) {
        if (ageNum < 20) {
          updatedForm.life_stage = "Adolescent";
        } else if (ageNum >= 20 && ageNum < 40) {
          updatedForm.life_stage = "Reproductive";
        } else if (ageNum >= 40) {
          updatedForm.life_stage = "Perimenopause";
        } else {
          updatedForm.life_stage = "";
        }
      } else {
        updatedForm.life_stage = "";
      }
    }
    setFormData(updatedForm);
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // don't let them try predicting if history is insufficient
    if (cycleCount !== null && cycleCount < 2) {
      setError("You need at least 2 saved cycles before making a prediction. Please add history first.");
      return;
    }

    setLoading(true);
    setError("");
    setError("");

    try {
      const bleedingDays = Number(formData.avg_bleeding_days);
      if (bleedingDays < 1 || bleedingDays > 10) throw new Error("Bleeding days must be 1–10");

      const painMap = { low: 1, moderate: 3, severe: 7 };
      const flowMap = { light: 1, moderate: 3, heavy: 7 };

      // Base payload
      const payload = {
        age: Number(formData.age),
        height: Number(formData.height),
        weight: Number(formData.weight),
        life_stage: formData.life_stage,
        tracking_duration: Number(formData.tracking_duration) || 0,
        pain_score: painMap[formData.pain_level.toLowerCase()],
        avg_bleeding_days: bleedingDays,
        bleeding_volume_score: flowMap[formData.flow_intensity.toLowerCase()],
        intermenstrual_episodes: Number(formData.intermenstrual_episodes) || 0,
        missed_periods: Number(formData.missed_periods) || 0,
      };

      console.log("Sending payload:", payload);
      const res = await api.post("/predict/", payload);
      navigate("/results", { state: { result: res.data, inputData: payload } });
    } catch (err) {
      console.error(err);
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.response?.data) {
        setError(JSON.stringify(err.response.data));
      } else {
        setError(err.message || "Prediction failed.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-pink-50 p-6 flex justify-center">
      <div className="max-w-4xl w-full bg-white p-10 rounded-xl shadow-lg">
        {username && <p className="text-left text-gray-600 mb-2">Welcome, <span className="font-semibold">{username}</span></p>}
        <h1 className="text-3xl font-bold text-center mb-8">Predict Menstrual Irregularity</h1>

        {/* show guidance when user has too few cycles */}
        {cycleCount !== null && cycleCount < 2 && (
          <p className="text-yellow-700 text-center mb-4 font-semibold">
            You currently have {cycleCount} saved cycle{cycleCount === 1 ? "" : "s"}.
            please <a href="/cycles/history" className="underline text-blue-600">add at least two cycles</a> for more accurate predictions.
          </p>
        )}

        {error && <p className="text-red-600 text-center mb-4 font-semibold">{error}</p>}
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex flex-col">
            <label className="font-semibold text-gray-700 mb-1">Age</label>
            <input name="age" type="number" min="8" max="55" value={formData.age} onChange={handleChange} placeholder="Age (e.g., 10-55)" className="p-3 border rounded-lg focus:ring focus:ring-pink-300 outline-none" required />
          </div>
          <Input label="Height (cm)" name="height" value={formData.height} onChange={handleChange} />
          <Input label="Weight (kg)" name="weight" value={formData.weight} onChange={handleChange} />
          <Select label="Life Stage" name="life_stage" value={formData.life_stage} onChange={handleChange} options={["Adolescent", "Reproductive", "Perimenopause"]} disabled={true} />


          <Select label="Menstrual Pain Level" name="pain_level" value={formData.pain_level} onChange={handleChange} options={["Low", "Moderate", "Severe"]} />
          <Input label="Average Bleeding Days" name="avg_bleeding_days" value={formData.avg_bleeding_days} onChange={handleChange} />
          <Select label="Menstrual Flow Intensity" name="flow_intensity" value={formData.flow_intensity} onChange={handleChange} options={["Light", "Moderate", "Heavy"]} />
          <Input label="Missed Periods (last 12 months)" name="missed_periods" value={formData.missed_periods} onChange={handleChange} placeholder="e.g. 0, 1, 2..." />

          <button type="submit" disabled={loading} className="col-span-full bg-pink-600 text-white p-4 rounded-xl font-bold text-lg hover:bg-pink-700 transition shadow-md disabled:opacity-50">
            {loading ? "Calculating..." : "Predict"}
          </button>
        </form>
      </div>
    </div>
  );
}

const Input = ({ label, name, value, onChange, placeholder }) => (
  <div className="flex flex-col">
    <label className="font-semibold text-gray-700 mb-1">{label}</label>
    <input name={name} value={value} onChange={onChange} placeholder={placeholder || label} className="p-3 border rounded-lg focus:ring focus:ring-pink-300 outline-none" required />
  </div>
);

const Select = ({ label, name, value, onChange, options, disabled }) => (
  <div className="flex flex-col">
    <label className="font-semibold text-gray-700 mb-1">{label}</label>
    <select name={name} value={value} onChange={onChange} disabled={disabled} className="p-3 border rounded-lg focus:ring focus:ring-pink-300 outline-none disabled:bg-gray-100 disabled:text-gray-600 disabled:cursor-not-allowed" required={!disabled}>
      <option value="">{disabled ? "Determined by Age..." : "Select"}</option>
      {options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
    </select>
  </div>
);

export default PredictForm;