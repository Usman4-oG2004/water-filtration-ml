import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# ── Config ───────────────────────────────────────────────────
DATA_PATH = "data/Pb and Lanthanoids_data.xlsx"
MODEL_DIR = "models"
OUTPUT_DIR = "outputs"

# ── Data Cleaning Helpers ─────────────────────────────────────
def clean_val(val):
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).strip().replace('%', '')
    if '–' in val_str:
        parts = val_str.split('–')
        try: return np.mean([float(p) for p in parts])
        except: pass
    if '-' in val_str:
        parts = val_str.split('-')
        try: return np.mean([float(p) for p in parts])
        except: pass
    # Extract first numeric float
    import re
    nums = re.findall(r'[-+]?\d*\.\d+|\d+', val_str)
    if nums:
        return float(nums[0])
    return np.nan

def clean_removal(val):
    v = clean_val(val)
    if pd.isna(v):
        return np.nan
    if v > 1.0:
        return v / 100.0
    return v

def train_and_validate(sheet_name, target_col, features, output_prefix):
    print(f"\n==========================================")
    print(f"Training Model for Sheet: {sheet_name}")
    print(f"==========================================")
    
    # Load dataset
    df = pd.read_excel(DATA_PATH, sheet_name=sheet_name)
    
    # Clean features
    df['pH_clean'] = df['pH'].apply(clean_val)
    df['temp_clean'] = df['Production Temp. (°C)' if 'Temp' in df.columns or 'Production Temp.' in df.columns else 'Production Temperature (°C)'].apply(clean_val)
    df['time_clean'] = df['Adsorption Time (min)'].apply(clean_val).fillna(df['Contact Time (min)'].apply(clean_val))
    df['target_clean'] = df[target_col].apply(clean_removal)
    
    # Drop rows with NaNs in key features
    df_clean = df[['pH_clean', 'temp_clean', 'time_clean', 'target_clean']].dropna()
    print(f"Loaded {len(df)} rows. Cleaned down to {len(df_clean)} rows.")
    
    X = df_clean[['pH_clean', 'temp_clean', 'time_clean']].values
    y = df_clean['target_clean'].values
    
    # Cross Validation
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    r2_scores, maes, rmses = [], [], []
    
    for fold, (train_idx, test_idx) in enumerate(kf.split(X)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Scale
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Fit Random Forest
        rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X_train_scaled, y_train)
        
        # Predict
        preds = rf.predict(X_test_scaled)
        
        # Metrics
        r2_scores.append(r2_score(y_test, preds))
        maes.append(mean_absolute_error(y_test, preds))
        rmses.append(np.sqrt(mean_squared_error(y_test, preds)))
        
    print(f"5-Fold Cross Validation Metrics:")
    print(f"  R² Score:  {np.mean(r2_scores):.3f} (±{np.std(r2_scores):.3f})")
    print(f"  MAE:       {np.mean(maes):.3f} (±{np.std(maes):.3f})")
    print(f"  RMSE:      {np.mean(rmses):.3f} (±{np.std(rmses):.3f})")
    
    # Train final model on all data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_scaled, y)
    
    # Save model and scaler
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, f"{MODEL_DIR}/{output_prefix}_model.pkl")
    joblib.dump(scaler, f"{MODEL_DIR}/{output_prefix}_scaler.pkl")
    print(f"Saved model to {MODEL_DIR}/{output_prefix}_model.pkl")

if __name__ == "__main__":
    if not os.path.exists(DATA_PATH):
        print(f"Error: dataset not found at {DATA_PATH}. Place Excel file in data/ folder first.")
        # Create data directory if missing
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    else:
        train_and_validate("Pb", "Final Pb Removal", ['pH_clean', 'temp_clean', 'time_clean'], "pb")
        train_and_validate("Lanthanides", "Final Lanthanoid /REE Removal (%)", ['pH_clean', 'temp_clean', 'time_clean'], "ree")
