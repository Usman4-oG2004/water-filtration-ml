import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import joblib
import os

# ── Config ───────────────────────────────────────────────────
DATA_PATH  = "data/water_data.csv"
MODEL_PATH = "models/anomaly_model.pkl"
SCALER_PATH= "models/scaler.pkl"
OUT_DIR    = "outputs"
FEATURES   = ["pH", "turbidity", "chlorine", "flow_rate"]

# ── Load model, scaler, data ─────────────────────────────────
print("[1/4] Loading model, scaler and data...")
model  = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
df     = pd.read_csv(DATA_PATH)
X      = df[FEATURES].values
X_scaled = scaler.transform(X)

# ── Run detection ───────────────────────────────────────────
print("[2/4] Running anomaly detection...")
preds  = model.predict(X_scaled)        # 1 = normal, -1 = anomaly
scores = model.decision_function(X_scaled)

df["prediction"] = preds
df["anomaly_score"] = scores
df["status"] = df["prediction"].map({1: "NORMAL", -1: "ANOMALY"})

# ── Save results CSV ─────────────────────────────────────────
print("[3/4] Saving results...")
os.makedirs(OUT_DIR, exist_ok=True)
results_path = f"{OUT_DIR}/results.csv"
df.to_csv(results_path, index=False)

anomalies_df = df[df["status"] == "ANOMALY"]
print(f"\nDetection Summary")
print(f"  Total samples   : {len(df)}")
print(f"  Anomalies found : {len(anomalies_df)} ({len(anomalies_df)/len(df)*100:.1f}%)")
print(f"  Results saved   : {results_path}")
print("\nTop 5 anomalies detected:")
print(anomalies_df[["pH","turbidity","chlorine","flow_rate","anomaly_score","status"]]
      .sort_values("anomaly_score")
      .head(5)
      .to_string(index=False))

# ── Visualise results ─────────────────────────────────────────
print("[4/4] Generating visualisation...")

normal    = df[df["status"] == "NORMAL"]
anomalies = df[df["status"] == "ANOMALY"]

fig = plt.figure(figsize=(16, 10))
gs  = gridspec.GridSpec(2, 2, figure=fig)

# Plot 1 — pH vs Turbidity
ax1 = fig.add_subplot(gs[0, 0])
ax1.scatter(normal["pH"],    normal["turbidity"],    c="steelblue", s=15, alpha=0.5, label="Normal")
ax1.scatter(anomalies["pH"], anomalies["turbidity"], c="red",       s=40, alpha=0.8, label="Anomaly", marker="x")
ax1.set_xlabel("pH")
ax1.set_ylabel("Turbidity (NTU)")
ax1.set_title("pH vs Turbidity")
ax1.legend()

# Plot 2 — Chlorine vs Flow Rate
ax2 = fig.add_subplot(gs[0, 1])
ax2.scatter(normal["chlorine"],    normal["flow_rate"],    c="steelblue", s=15, alpha=0.5, label="Normal")
ax2.scatter(anomalies["chlorine"], anomalies["flow_rate"], c="red",       s=40, alpha=0.8, label="Anomaly", marker="x")
ax2.set_xlabel("Chlorine (mg/L)")
ax2.set_ylabel("Flow Rate (L/min)")
ax2.set_title("Chlorine vs Flow Rate")
ax2.legend()

# Plot 3 — Anomaly score over time
ax3 = fig.add_subplot(gs[1, :])
ax3.plot(df.index, df["anomaly_score"], color="steelblue", linewidth=0.8, label="Anomaly Score")
ax3.axhline(0, color="red", linestyle="--", linewidth=1, label="Decision Boundary")
ax3.fill_between(df.index, df["anomaly_score"], 0,
                  where=(df["anomaly_score"] < 0), color="red", alpha=0.3, label="Anomaly Zone")
ax3.set_xlabel("Sample Index (Time)")
ax3.set_ylabel("Score")
ax3.set_title("Anomaly Score Over Time")
ax3.legend()

plt.suptitle("Water Quality Anomaly Detection Results", fontsize=14, fontweight="bold")
plt.tight_layout()
plot_path = f"{OUT_DIR}/anomaly_detection_report.png"
plt.savefig(plot_path, dpi=150)
plt.close()
print(f"  Plot saved: {plot_path}")
print("\nDone. Review outputs/ folder for full results.")
