# 💧 Water Filtration & REE Recovery ML Web Application

A full-stack Python web application featuring secure user registration, multi-user workspaces, an administrative control panel, and machine learning prediction engines that analyze water filtration parameters and rare earth element (REE) recovery.

---

## 🚀 Key Features

- **Dynamic Excel Processing:** Drag-and-drop spreadsheets (`.xlsx`) to automatically run Random Forest model predictions and download annotated reports.
- **User Workspaces:** Sandy and other clients can register accounts to manage their own upload history, log downloads, and simulation parameters.
- **Live Simulator:** Dynamic sliders for HTC carbonization temperature, solution pH, biomass dosage, and contact time with animated Chart.js curves.
- **Admin Audit Logs:** A central dashboard tracking global system statistics (total uploads, users, processed rows, and anomalies) and full history audit logs.
- **Branch Protection & CI/CD:** Protected main/develop branches with automated GitHub Actions for Pylint checks and multi-version testing.

---

## 🧱 Codebase Structure

```
water-filtration-ml/
├── app/
│   ├── main.py             # FastAPI server entry point & API endpoints
│   ├── database.py         # SQLite connection session maker
│   ├── models.py           # SQLAlchemy database tables (User, UploadRecord)
│   ├── auth.py             # JWT cryptography and session dependencies
│   ├── ml_engine.py        # High-dimensional Excel cleaning and predictions
│   ├── templates/          # Tailwind CSS styled HTML views
│   │   ├── login.html      # Self-registration & sign-in screen
│   │   ├── dashboard.html  # Sandy's workspace (uploader, charts, simulator)
│   │   └── admin.html      # Administrative portal (audit logs, stats)
│   └── static/             # Assets (CSS/JS)
├── data/
│   └── Pb and Lanthanoids_data.xlsx  # Real experimental dataset
├── train_regressor.py       # Random Forest regression training script
├── requirements.txt         # Project dependencies
└── README.md
```

---

## ⚙️ Quick Start (Running Locally)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web Server
Launch the FastAPI application using Uvicorn:
```bash
uvicorn app.main:app --reload
```

### 3. Access the Platform
Open your browser and navigate to:
👉 **`http://127.0.0.1:8000`**

### 4. Admin Access
Log in with the default admin account created automatically on startup:
- **Username:** `admin`
- **Password:** `admin123`

---

## 👥 Contributors
- **Ali Hassan** — Machine Learning Architecture & Dashboard Design
- **Muhammad Usman** — Core Development, Database Systems, & CI/CD Pipelines
