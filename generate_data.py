import pandas as pd
import numpy as np
import os

# ── Reproducibility ──────────────────────────────────────────────
np.random.seed(42)

NUM_SAMPLES  = 1000   # normal readings
NUM_ANOMALIES = 50    # injected anomalies

# ── Generate normal sensor readings ──────────────────────────────
normal_data = pd.DataFrame({
    "pH":         np.random.normal(7.0, 0.3,  NUM_SAMPLES),   # safe: 6.5–8.5
    "turbidity":  np.random.normal(1.5, 0.5,  NUM_SAMPLES),   # safe: 0–5 NTU
    "chlorine":   np.random.normal(1.0, 0.2,  NUM_SAMPLES),   # safe: 0.2–4 mg/L
    "flow_rate":  np.random.normal(50.0, 5.0, NUM_SAMPLES),   # litres/min
    "label": 0  # 0 = normal
})

# ── Inject anomalies (contamination / filter failure) ────────────
anomalies = pd.DataFrame({
    "pH":         np.random.choice(
                      [np.random.uniform(2.0, 5.0),          # acidic spike
                       np.random.uniform(9.5, 12.0)],        # alkaline spike
                      size=NUM_ANOMALIES),
    "turbidity":  np.random.uniform(15.0, 40.0, NUM_ANOMALIES),  # very cloudy
    "chlorine":   np.random.uniform(0.0, 0.05,  NUM_ANOMALIES),  # under-dosed
    "flow_rate":  np.random.uniform(5.0, 15.0,  NUM_ANOMALIES),  # low flow
    "label": 1  # 1 = anomaly
})

# ── Combine, shuffle, save ────────────────────────────────────────
df = pd.concat([normal_data, anomalies], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

os.makedirs("data", exist_ok=True)
df.to_csv("data/water_data.csv", index=False)

print(f"Dataset saved: {len(df)} rows ({NUM_SAMPLES} normal + {NUM_ANOMALIES} anomalies)")
print(df.describe().round(2))
