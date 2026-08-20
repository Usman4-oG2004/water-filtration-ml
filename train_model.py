import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ── Config ───────────────────────────────────────────────────
DATA_PATH  = "data/water_data.csv"
MODEL_DIR  = "models"
FEATURES   = ["pH", "turbidity", "chlorine", "flow_rate"]
CONTAMINATION = 0.05   # expected anomaly ratio (~5%)

# ── Load data ───────────────────────────────────────────────
print("[1/4] Loading data...")
df = pd.read_csv(DATA_PATH)
X  = df[FEATURES].values

# ── Scale features ────────────────────────────────────────────
print("[2/4] Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── Train Isolation Forest ───────────────────────────────────
print("[3/4] Training Isolation Forest model...")
model = IsolationForest(
    n_estimators=200,
    contamination=CONTAMINATION,
    random_state=42,
    n_jobs=-1
)
model.fit(X_scaled)

# ── Save model + scaler ──────────────────────────────────────
print("[4/4] Saving model and scaler...")
os.makedirs(MODEL_DIR, exist_ok=True)
joblib.dump(model,  f"{MODEL_DIR}/anomaly_model.pkl")
joblib.dump(scaler, f"{MODEL_DIR}/scaler.pkl")

# ── Quick training report ─────────────────────────────────────
preds   = model.predict(X_scaled)  # -1 = anomaly, 1 = normal
flagged = (preds == -1).sum()
print(f"\nTraining complete.")
print(f"  Total samples : {len(df)}")
print(f"  Flagged anomalies : {flagged} ({flagged/len(df)*100:.1f}%)")
print(f"  Model saved   : {MODEL_DIR}/anomaly_model.pkl")
print(f"  Scaler saved  : {MODEL_DIR}/scaler.pkl")

# ── Plot anomaly scores ──────────────────────────────────────
scores = model.decision_function(X_scaled)
plt.figure(figsize=(12, 4))
plt.plot(scores, color="steelblue", linewidth=0.8, label="Anomaly Score")
plt.axhline(0, color="red", linestyle="--", linewidth=1, label="Decision Boundary")
plt.fill_between(range(len(scores)), scores, 0,
                  where=(scores < 0), color="red", alpha=0.3, label="Anomaly Zone")
plt.title("Isolation Forest — Anomaly Scores")
plt.xlabel("Sample Index")
plt.ylabel("Score (negative = anomaly)")
plt.legend()
plt.tight_layout()
os.makedirs("outputs", exist_ok=True)
plt.savefig("outputs/training_scores.png", dpi=150)
plt.close()
print("  Plot saved    : outputs/training_scores.png")
