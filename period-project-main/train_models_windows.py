# ===============================
# TRAIN MODELS (WINDOWS)
# ===============================

import os
import numpy as np
import pandas as pd
import joblib

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Skip TensorFlow for now due to compatibility issues
TENSORFLOW_AVAILABLE = False
print("⚠ Skipping TensorFlow - will train only Random Forest models")

# -------------------------------
# PATHS
# -------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = r"C:\Users\Acer\Desktop\menstrual_irregularity_dataset.csv"


ML_DIR = os.path.join(BASE_DIR, "tracker", "ml_models")
os.makedirs(ML_DIR, exist_ok=True)

# -------------------------------
# LOAD DATA
# -------------------------------

df = pd.read_csv(DATASET_PATH)

# -------------------------------
# TARGET CREATION
# -------------------------------

irregular_cols = [
    "Oligomenorrhea",
    "Polymenorrhea",
    "Menorrhagia",
    "Amenorrhea",
    "Intermenstrual",
]

irregular_cols = [c for c in irregular_cols if c in df.columns]

# Create binary target for irregularity detection
df["target_irregular"] = (df[irregular_cols].sum(axis=1) > 0).astype(int)

# Create multi-class target for irregularity type prediction
def get_irregularity_type(row):
    """Determine the primary irregularity type"""
    if row["Oligomenorrhea"] == 1:
        return "Oligomenorrhea"
    elif row["Polymenorrhea"] == 1:
        return "Polymenorrhea"
    elif row["Menorrhagia"] == 1:
        return "Menorrhagia"
    elif row["Amenorrhea"] == 1:
        return "Amenorrhea"
    elif row["Intermenstrual"] == 1:
        return "Intermenstrual"
    else:
        return "Regular"

df["irregularity_type"] = df.apply(get_irregularity_type, axis=1)

# Create label encoder for irregularity types
irregularity_encoder = LabelEncoder()
df["irregularity_type_enc"] = irregularity_encoder.fit_transform(df["irregularity_type"])

# -------------------------------
# ENCODE LIFE STAGE
# -------------------------------

life_encoder = LabelEncoder()
df["life_stage_enc"] = life_encoder.fit_transform(
    df["life_stage"].astype(str)
)

# -------------------------------
# FEATURES
# -------------------------------

FEATURE_COLS = [
    "age",
    "bmi",
    "life_stage_enc",
    "tracking_duration_months",
    "pain_score",
    "avg_cycle_length",
    "cycle_length_variation",
    "avg_bleeding_days",
    "bleeding_volume_score",
    "intermenstrual_episodes",
    "cycle_variation_coeff",
    "pattern_disruption_score",
]

X = df[FEATURE_COLS].fillna(df[FEATURE_COLS].median())
y = df["target_irregular"]

# -------------------------------
# SCALE FEATURES
# -------------------------------

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -------------------------------
# RANDOM FOREST
# -------------------------------

rf = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

rf.fit(X_scaled, y)

# -------------------------------
# SAVE RF MODELS
# -------------------------------

joblib.dump(rf, os.path.join(ML_DIR, "rf_model.pkl"))
joblib.dump(scaler, os.path.join(ML_DIR, "scaler.pkl"))
joblib.dump(life_encoder, os.path.join(ML_DIR, "life_stage_encoder.pkl"))

# -------------------------------
# RANDOM FOREST FOR IRREGULARITY TYPE
# -------------------------------

# Only train on irregular cycles for type classification
irregular_df = df[df["target_irregular"] == 1].copy()
X_irregular = irregular_df[FEATURE_COLS].fillna(irregular_df[FEATURE_COLS].median())
y_irregular_type = irregular_df["irregularity_type_enc"]

# Scale features for irregularity type model
X_irregular_scaled = scaler.fit_transform(X_irregular)

rf_type = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

rf_type.fit(X_irregular_scaled, y_irregular_type)

# -------------------------------
# SAVE IRREGULARITY TYPE MODELS
# -------------------------------

joblib.dump(rf_type, os.path.join(ML_DIR, "rf_type_model.pkl"))
joblib.dump(irregularity_encoder, os.path.join(ML_DIR, "irregularity_type_encoder.pkl"))

# -------------------------------
# LSTM (CYCLE LENGTH)
# -------------------------------

if TENSORFLOW_AVAILABLE:
    try:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense

        cycle_series = df["avg_cycle_length"].dropna().values

        X_seq = []
        y_seq = []

        for i in range(len(cycle_series) - 5):
            X_seq.append(cycle_series[i:i+5])
            y_seq.append(cycle_series[i+5])

        X_seq = np.array(X_seq)
        y_seq = np.array(y_seq)

        ts_scaler = StandardScaler()
        X_seq_scaled = ts_scaler.fit_transform(
            X_seq.reshape(-1, 1)
        ).reshape(X_seq.shape[0], 5, 1)

        y_seq_scaled = ts_scaler.transform(y_seq.reshape(-1, 1))

        lstm_model = Sequential([
            LSTM(32, input_shape=(5, 1)),
            Dense(1)
        ])

        lstm_model.compile(optimizer="adam", loss="mse")
        lstm_model.fit(
            X_seq_scaled,
            y_seq_scaled,
            epochs=10,
            batch_size=32,
            verbose=1
        )

        # -------------------------------
        # SAVE LSTM
        # -------------------------------

        lstm_model.save(os.path.join(ML_DIR, "lstm_model.h5"))
        joblib.dump(ts_scaler, os.path.join(ML_DIR, "ts_scaler.pkl"))
        print("✅ LSTM model trained and saved")
    except Exception as e:
        print(f"❌ LSTM training failed: {e}")
        print("Continuing without LSTM model...")
else:
    print("⚠ TensorFlow not available - skipping LSTM training")

print("\n✅ ALL MODELS TRAINED AND SAVED SUCCESSFULLY")
