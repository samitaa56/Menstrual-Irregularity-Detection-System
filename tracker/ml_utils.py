import numpy as np
import joblib
from pathlib import Path
from django.conf import settings

# ---------- Safe TensorFlow import ----------
try:
    from tensorflow.keras.models import load_model
except Exception as e:
    load_model = None
    print("⚠ TensorFlow not available:", e)

# ---------- PATHS ----------
BASE_DIR = Path(settings.BASE_DIR)
ML_DIR = BASE_DIR / "tracker" / "ml_models"

RF_MODEL_PATH = ML_DIR / "rf_model.pkl"
SCALER_PATH = ML_DIR / "scaler.pkl"
LIFE_STAGE_ENCODER_PATH = ML_DIR / "life_stage_encoder.pkl"
LSTM_MODEL_PATH = ML_DIR / "lstm_model.h5"
TS_SCALER_PATH = ML_DIR / "ts_scaler.pkl"

# ---------- GLOBAL MODEL CACHE ----------
_rf_model = None
_scaler = None
_life_stage_encoder = None
_lstm_model = None
_ts_scaler = None


# ---------- UTIL ----------
def _check_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"❌ Missing model file: {path}")


# ---------- LOAD MODELS ONCE ----------
def load_models_once():
    global _rf_model, _scaler, _life_stage_encoder, _lstm_model, _ts_scaler

    if _rf_model is not None:
        return

    _check_file(RF_MODEL_PATH)
    _check_file(SCALER_PATH)
    _check_file(LIFE_STAGE_ENCODER_PATH)
    _check_file(TS_SCALER_PATH)

    if load_model:
        _check_file(LSTM_MODEL_PATH)

    _rf_model = joblib.load(RF_MODEL_PATH)
    _scaler = joblib.load(SCALER_PATH)
    _life_stage_encoder = joblib.load(LIFE_STAGE_ENCODER_PATH)
    _ts_scaler = joblib.load(TS_SCALER_PATH)

    if load_model:
        _lstm_model = load_model(LSTM_MODEL_PATH, compile=False)
    else:
        _lstm_model = None


# ---------- FEATURE VECTOR ----------
def build_feature_vector(data: dict):
    load_models_once()

    try:
        life_stage_clean = str(data["life_stage"]).strip().lower()
        life_stage_enc = _life_stage_encoder.transform([life_stage_clean])[0]
    except Exception:
        raise ValueError("Invalid life_stage value")

    values = [
        int(data["age"]),
        float(data["bmi"]),
        float(life_stage_enc),
        int(data["tracking_duration"]),
        int(data["pain_score"]),
        int(data["avg_cycle_length"]),
        int(data["cycle_length_variation"]),
        int(data["avg_bleeding_days"]),
        int(data["bleeding_volume_score"]),
        int(data["intermenstrual_episodes"]),
        float(data["cycle_variation_coefficient"]),
        int(data["pattern_disruption_score"]),
    ]

    X = np.array(values, dtype=float).reshape(1, -1)
    return _scaler.transform(X)


# ---------- RF PREDICTION (FIXED LOGIC) ----------
def predict_irregularity(data: dict) -> dict:
    load_models_once()

    X = build_feature_vector(data)

    # Raw probability from RF
    prob = float(_rf_model.predict_proba(X)[0][1])

    # -----------------------------
    # ✅ IMPORTANT FIX
    # -----------------------------
    # Old: threshold = 0.50  ❌ (too sensitive)
    # New: threshold = 0.65  ✅ (realistic)
    THRESHOLD = 0.65

    label = "Irregular" if prob >= THRESHOLD else "Regular"

    # Clamp probability for UI stability
    prob = max(0.30, min(prob, 0.95))

    return {
        "label": label,
        "probability": round(prob, 4),
    }


# ---------- LSTM NEXT CYCLE ----------
def predict_next_cycle_length(avg_cycle_length: float):
    load_models_once()

    if _lstm_model is None:
        return None

    avg_cycle_length = float(avg_cycle_length)

    seq = np.array([
        avg_cycle_length - 2,
        avg_cycle_length - 1,
        avg_cycle_length,
        avg_cycle_length + 1,
        avg_cycle_length + 2,
    ]).reshape(-1, 1)

    seq_scaled = _ts_scaler.transform(seq)
    seq_scaled = seq_scaled.reshape(1, 5, 1)

    pred_scaled = _lstm_model.predict(seq_scaled, verbose=0)
    return float(_ts_scaler.inverse_transform(pred_scaled)[0][0])


# ---------- COMBINED OUTPUT ----------
def predict_both(data: dict) -> dict:
    rf_result = predict_irregularity(data)
    next_cycle = predict_next_cycle_length(data["avg_cycle_length"])

    return {
        "irregularity_prediction": rf_result["label"],
        "irregularity_probability": rf_result["probability"],
        "next_cycle_prediction": round(next_cycle, 2) if next_cycle else None,
    }
