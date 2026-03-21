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

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

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

df["target_irregular"] = (df[irregular_cols].sum(axis=1) > 0).astype(int)

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
# LSTM (CYCLE LENGTH)
# -------------------------------

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

print("\n✅ ALL MODELS TRAINED AND SAVED SUCCESSFULLY")
