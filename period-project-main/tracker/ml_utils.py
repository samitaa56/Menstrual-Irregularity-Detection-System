import numpy as np  # type: ignore
import time
import logging

logger = logging.getLogger(__name__)

try:
    import joblib  # type: ignore
except ImportError:
    joblib = None  # type: ignore

from pathlib import Path

try:
    from django.conf import settings  # type: ignore
except ImportError:
    class _Settings:
        BASE_DIR = Path(__file__).resolve().parents[2]
    settings = _Settings()


# ---------- Safe TensorFlow import ----------
try:
    from tensorflow.keras.models import load_model  # type: ignore
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
RF_TYPE_MODEL_PATH = ML_DIR / "rf_type_model.pkl"
IRREGULARITY_TYPE_ENCODER_PATH = ML_DIR / "irregularity_type_encoder.pkl"

# ---------- GLOBAL MODEL CACHE ----------
_rf_model = None
_scaler = None
_life_stage_encoder = None
_lstm_model = None
_ts_scaler = None
_rf_type_model = None
_irregularity_type_encoder = None


# ---------- UTIL ----------
def _check_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"❌ Missing model file: {path}")


# ---------- LOAD MODELS ONCE ----------
def load_models_once():
    global _rf_model, _scaler, _life_stage_encoder, _lstm_model, _ts_scaler
    global _rf_type_model, _irregularity_type_encoder

    if _rf_model is not None:
        return

    start_time = time.time()
    logger.info("🚀 Loading AI models...")

    try:
        _check_file(RF_MODEL_PATH)
        _check_file(SCALER_PATH)
        _check_file(LIFE_STAGE_ENCODER_PATH)
        _check_file(TS_SCALER_PATH)
        _check_file(RF_TYPE_MODEL_PATH)
        _check_file(IRREGULARITY_TYPE_ENCODER_PATH)

        if joblib is None:
            raise ImportError("joblib is required to load model files but is not installed.")

        _rf_model = joblib.load(RF_MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
        _life_stage_encoder = joblib.load(LIFE_STAGE_ENCODER_PATH)
        _ts_scaler = joblib.load(TS_SCALER_PATH)
        _rf_type_model = joblib.load(RF_TYPE_MODEL_PATH)
        _irregularity_type_encoder = joblib.load(IRREGULARITY_TYPE_ENCODER_PATH)

        if load_model:
            _check_file(LSTM_MODEL_PATH)
            _lstm_model = load_model(LSTM_MODEL_PATH, compile=False)
        else:
            _lstm_model = None
            logger.warning("⚠ TensorFlow (load_model) not available - LSTM fallback active.")

        end_time = time.time()
        logger.info(f"✅ AI models loaded successfully in {end_time - start_time:.2f}s")
    except Exception as e:
        logger.error(f"❌ Error loading AI models: {e}")
        _rf_model = False


# ---------- FEATURE VECTOR ----------
def build_feature_vector(data: dict):
    load_models_once()
    assert _life_stage_encoder is not None
    assert _scaler is not None

    try:
        life_stage_clean = str(data["life_stage"]).strip().lower()
        if life_stage_clean == "perimenopause":
            life_stage_clean = "perimenopausal"
        life_stage_enc = _life_stage_encoder.transform([life_stage_clean])[0]
    except Exception as e:
        logger.error(f"Life stage encoding error for '{data.get('life_stage')}': {e}")
        life_stage_enc = _life_stage_encoder.transform(["reproductive"])[0]

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


# ---------- RF PREDICTION ----------
def predict_irregularity(data: dict) -> dict:
    load_models_once()

    avg_cycle = int(data.get("avg_cycle_length", 0))
    variation = int(data.get("cycle_length_variation", 0))
    bleeding_days = int(data.get("avg_bleeding_days", 0))
    bleeding_volume = int(data.get("bleeding_volume_score", 0))
    intermenstrual = int(data.get("intermenstrual_episodes", 0))
    missed = int(data.get("missed_periods", 0))

    has_menorrhagia = bleeding_days >= 8 or bleeding_volume >= 7
    has_intermenstrual = intermenstrual > 0
    has_amenorrhea = missed >= 3

    if 21 <= avg_cycle <= 35 and variation <= 7:
        if has_menorrhagia or has_intermenstrual or has_amenorrhea:
            X = build_feature_vector(data)
            assert _rf_model is not None
            prob = float(_rf_model.predict_proba(X)[0][1])
            THRESHOLD = 0.50
            label = "Irregular" if prob >= THRESHOLD else "Regular"
            winning_conf = prob if label == "Irregular" else (1.0 - prob)
            return {
                "prediction_status": label,
                "chance_of_irregularity": float(round(prob, 4)),
                "confidence": float(round(winning_conf, 4)),
            }
        else:
            return {
                "prediction_status": "Regular",
                "chance_of_irregularity": 0.10,
                "confidence": 0.95,
            }

    X = build_feature_vector(data)
    assert _rf_model is not None
    prob = float(_rf_model.predict_proba(X)[0][1])

    THRESHOLD = 0.60
    label = "Irregular" if prob >= THRESHOLD else "Regular"
    winning_conf = prob if label == "Irregular" else (1.0 - prob)

    return {
        "prediction_status": label,
        "chance_of_irregularity": float(round(prob, 4)),
        "confidence": float(round(winning_conf, 4)),
    }


# ---------- PREDICT IRREGULARITY TYPE ----------
def predict_irregularity_type(data: dict) -> str:
    load_models_once()

    if _rf_type_model is None or _irregularity_type_encoder is None:
        return predict_irregularity_type_rule_based(data)

    try:
        X = build_feature_vector(data)
        predicted_idx = int(_rf_type_model.predict(X)[0])
        ml_type = _irregularity_type_encoder.inverse_transform([predicted_idx])[0]

        rule_based_str = predict_irregularity_type_rule_based(data)

        if rule_based_str == "Unspecified Irregularity":
            return ml_type

        rule_based_types = [t.strip() for t in rule_based_str.split(",")]

        if ml_type not in rule_based_types and ml_type != "Unspecified Irregularity":
            rule_based_types.append(ml_type)

        return ", ".join(rule_based_types)

    except Exception as e:
        logger.error(f"Error predicting irregularity type: {e}")
        return predict_irregularity_type_rule_based(data)


# ---------- RULE-BASED IRREGULARITY TYPE (FALLBACK) ----------
def predict_irregularity_type_rule_based(data: dict) -> str:
    avg_cycle = int(data.get("avg_cycle_length", 28))
    bleeding_days = int(data.get("avg_bleeding_days", 5))
    bleeding_volume = int(data.get("bleeding_volume_score", 3))
    intermenstrual = int(data.get("intermenstrual_episodes", 0))
    missed_periods = int(data.get("missed_periods", 0))

    irregularities = []

    if avg_cycle >= 90 or missed_periods >= 3:
        irregularities.append("Amenorrhea")
    elif avg_cycle > 35:
        irregularities.append("Oligomenorrhea")
    elif avg_cycle < 21:
        irregularities.append("Polymenorrhea")

    if bleeding_days >= 8 or bleeding_volume >= 7:
        irregularities.append("Menorrhagia")

    if intermenstrual > 0:
        irregularities.append("Intermenstrual Bleeding")

    if not irregularities:
        return "Unspecified Irregularity"

    return ", ".join(irregularities)


# ---------- LSTM NEXT CYCLE ----------
def predict_next_cycle_length(avg_cycle_length: float, cycle_history: list = None):
    load_models_once()

    avg_cycle_length = float(avg_cycle_length)
    history = cycle_history if cycle_history is not None else []

    if len(history) >= 2:
        last_5 = (history[-5:] if len(history) >= 5
                  else [avg_cycle_length] * (5 - len(history)) + history)
        seq = np.array(last_5).reshape(-1, 1)
    else:
        seq = np.array([avg_cycle_length] * 5).reshape(-1, 1)

    if _lstm_model is None:
        if cycle_history:
            return float(seq[-1][0] * 0.6 + avg_cycle_length * 0.4)
        return float(avg_cycle_length)

    assert _ts_scaler is not None
    seq_scaled = _ts_scaler.transform(seq)
    seq_scaled = seq_scaled.reshape(1, 5, 1)

    pred_scaled = _lstm_model.predict(seq_scaled, verbose=0)
    return float(_ts_scaler.inverse_transform(pred_scaled)[0][0])


# ---------- COMBINED OUTPUT ----------
def predict_both(data: dict) -> dict:
    start_time = time.time()

    # ============================================================
    # 🔍 DEBUG — paste terminal output to verify models are working
    # ============================================================
    print("\n" + "="*50)
    print("🔍 DEBUG: predict_both called")
    print(f"   RF Model loaded:         {_rf_model is not None and _rf_model is not False}")
    print(f"   LSTM Model loaded:       {_lstm_model is not None}")
    print(f"   Type Model loaded:       {_rf_type_model is not None}")
    print(f"   Scaler loaded:           {_scaler is not None}")
    print(f"   Type Encoder loaded:     {_irregularity_type_encoder is not None}")
    print(f"   avg_cycle_length:        {data.get('avg_cycle_length')}")
    print(f"   cycle_length_variation:  {data.get('cycle_length_variation')}")
    print(f"   avg_bleeding_days:       {data.get('avg_bleeding_days')}")
    print(f"   bleeding_volume_score:   {data.get('bleeding_volume_score')}")
    print(f"   missed_periods:          {data.get('missed_periods')}")
    print(f"   intermenstrual_episodes: {data.get('intermenstrual_episodes')}")
    print(f"   pain_score:              {data.get('pain_score')}")
    print(f"   life_stage:              {data.get('life_stage')}")
    print(f"   age:                     {data.get('age')}")
    print(f"   bmi:                     {data.get('bmi')}")
    print("="*50)
    # ============================================================

    rf_result = predict_irregularity(data)

    print(f"🤖 RF Result:              {rf_result}")

    if rf_result["prediction_status"] == "Irregular":
        irregularity_type = predict_irregularity_type(data)
        print(f"🏷️  Irregularity Type:      {irregularity_type}")
        if irregularity_type == "Unspecified Irregularity":
            irregularity_type = None
    else:
        irregularity_type = None
        print(f"🏷️  Irregularity Type:      None (Regular cycle)")

    cycle_history = data.get("history_used", [])
    next_cycle = predict_next_cycle_length(data["avg_cycle_length"], cycle_history)

    print(f"📅 Next Cycle Prediction:  {next_cycle}")
    print(f"   LSTM used:               {_lstm_model is not None}")
    print("="*50 + "\n")

    end_time = time.time()
    logger.info(f"⏱ Prediction completed in {end_time - start_time:.4f}s")

    return {
        "prediction_status": rf_result["prediction_status"],
        "chance_of_irregularity": rf_result["chance_of_irregularity"],
        "confidence": rf_result["confidence"],
        "irregularity_type": irregularity_type,
        "next_cycle_prediction": float(round(next_cycle, 2)) if next_cycle else None,
    }


# ✅ Pre-load models at module import
try:
    load_models_once()
except:
    pass