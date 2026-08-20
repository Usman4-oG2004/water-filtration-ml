# 💧 Water Filtration ML — Anomaly Detection System

A Python-based machine learning project that detects anomalies in water quality sensor data. The system flags unsafe water conditions **before** they escalate, using unsupervised learning on real-time sensor readings.

---

## 🔍 What This Project Does

- Simulates real water sensor data (pH, turbidity, chlorine, flow rate)
- Trains an **Isolation Forest** model to detect abnormal readings
- Visualizes normal vs anomalous data points
- Exports results to a CSV report

---

## 🧱 Project Structure

```
water-filtration-ml/
├── data/
│   └── water_data.csv        # Simulated sensor dataset
├── models/
│   └── anomaly_model.pkl     # Trained ML model
├── outputs/
│   └── results.csv           # Anomaly detection results
├── generate_data.py          # Script to generate sensor data
├── train_model.py            # Script to train the ML model
├── detect_anomalies.py       # Script to run detection
├── requirements.txt          # Python dependencies
└── README.md
```

---

## ⚙️ Tech Stack

- Python 3.x
- pandas
- scikit-learn
- matplotlib
- joblib

---

## 🚀 Getting Started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate sensor data
python generate_data.py

# 3. Train the model
python train_model.py

# 4. Run anomaly detection
python detect_anomalies.py
```

---

## 👤 Author
Muhammad Usman — [GitHub](https://github.com/Usman4-oG2004)
