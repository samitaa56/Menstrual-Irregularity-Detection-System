import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { API_BASE_URL } from "../config";

const API_BASE = API_BASE_URL;

export default function VerifyEmail() {
    const { token } = useParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState("waiting"); // waiting, verifying, success, error
    const [message, setMessage] = useState("Do you want to continue with the verification and activate your account?");

    const handleVerify = async () => {
        if (!token) {
            setStatus("error");
            setMessage("No verification token found in the URL. Please check your email link.");
            return;
        }

        const cleanToken = token.trim();
        console.log(`[VerifyEmail] Triggering verification for token: "${cleanToken}"`);

        setStatus("verifying");
        setMessage("Verifying your email...");
        try {
            const response = await axios.get(
                `${API_BASE}/verify-email/${cleanToken}/`
            );

            setStatus("success");
            setMessage(response.data.message || "Email verified successfully! Redirecting to login...");

            // Redirect to login after 2 seconds
            setTimeout(() => {
                navigate("/login");
            }, 2000);
        } catch (error) {
            setStatus("error");
            console.error("Verification error object:", error);
            
            if (!error.response) {
                setMessage(`Network Error: Cannot reach the server at ${API_BASE}. Please ensure you are connected to the same Wi-Fi and the backend is running.`);
                return;
            }

            const backendError = error.response?.data?.error;
            const backendDetails = error.response?.data?.details;
            const statusText = error.response?.statusText || "Unknown Error";
            const statusCode = error.response?.status;
            
            const errorMsg = backendDetails || backendError ||
                `Server Error (${statusCode}: ${statusText}). The link may have expired or is incorrect.`;
            setMessage(errorMsg);
        }
    };

    const handleCancel = () => {
        navigate("/login");
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-50 to-purple-50">
            <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full mx-4">
                <h1 className="text-3xl font-bold text-center text-pink-600 mb-6">
                    {status === "waiting" && "Confirm Verification"}
                    {status === "verifying" && "Verifying Email"}
                    {status === "success" && "✅ Verified!"}
                    {status === "error" && "❌ Verification Failed"}
                </h1>

                <div className="text-center mb-6">
                    {status === "verifying" && (
                        <div className="flex justify-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div>
                        </div>
                    )}

                    <p className={`text-lg mt-4 ${status === "success" ? "text-green-600" :
                        status === "error" ? "text-red-600" :
                            "text-gray-700"
                        }`}>
                        {message}
                    </p>
                </div>

                {status === "waiting" && (
                    <div className="flex gap-4 mt-6">
                        <button
                            onClick={handleVerify}
                            className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg transition shadow-md"
                        >
                            Yes, Verify
                        </button>
                        <button
                            onClick={handleCancel}
                            className="flex-1 bg-gray-400 hover:bg-gray-500 text-white font-bold py-3 px-4 rounded-lg transition shadow-md"
                        >
                            No, Cancel
                        </button>
                    </div>
                )}

                {status === "error" && (
                    <div className="mt-6">
                        <button
                            onClick={() => navigate("/signup")}
                            className="w-full bg-pink-600 hover:bg-pink-700 text-white font-bold py-2 px-4 rounded-lg transition"
                        >
                            Back to Signup
                        </button>
                    </div>
                )}

                {status === "success" && (
                    <p className="text-center text-gray-600 text-sm">
                        Redirecting to login in 2 seconds...
                    </p>
                )}
            </div>
        </div>
    );
}
