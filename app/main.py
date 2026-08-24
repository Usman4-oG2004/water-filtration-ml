from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import shutil
import database
import models
import auth
import ml_engine

# Support persistent disk paths for cloud deployment (e.g. Render)
STORAGE_DIR = os.getenv("STORAGE_DIR", ".")
UPLOAD_DIR = os.path.join(STORAGE_DIR, "uploads")
PROCESSED_DIR = os.path.join(STORAGE_DIR, "outputs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Water Filtration ML Platform")

# Mount templates and static folders
# Get absolute directory path of app/ folder to avoid routing path bugs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Automatically ensure static directory exists to prevent FastAPI startup crash
static_dir = os.path.join(BASE_DIR, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Helper to pre-create default admin account on startup
@app.on_event("startup")
def startup_populate():
    db = database.SessionLocal()
    admin_user = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin_user:
        hashed_pw = auth.get_password_hash("admin123")
        db.add(models.User(username="admin", hashed_password=hashed_pw, role="admin"))
        db.commit()
    db.close()

# ── PAGE ROUTES ─────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def get_login(request: Request, current_user = Depends(auth.get_current_user)):
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request, current_user = Depends(auth.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})

@app.get("/admin", response_class=HTMLResponse)
async def get_admin_page(request: Request, current_user = Depends(auth.get_current_admin)):
    return templates.TemplateResponse("admin.html", {"request": request, "user": current_user})

# ── AUTH API ENDPOINTS ──────────────────────────────────────────────────────
@app.post("/register")
async def post_register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    existing = db.query(models.User).filter(models.User.username == username).first()
    if existing:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Username already exists"})
    
    hashed = auth.get_password_hash(password)
    user = models.User(username=username, hashed_password=hashed, role="user")
    db.add(user)
    db.commit()
    
    # Auto-login after registration
    token = auth.create_access_token({"sub": username})
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response

@app.post("/login")
async def post_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})
    
    token = auth.create_access_token({"sub": username})
    target_url = "/admin" if user.role == "admin" else "/dashboard"
    response = RedirectResponse(url=target_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response

@app.get("/logout")
async def get_logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

# ── FILE MANAGEMENT ENDPOINTS ───────────────────────────────────────────────
@app.post("/upload")
async def post_upload(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported.")

    # Save raw upload
    import time
    raw_filename = f"user_{current_user.id}_{int(time.time())}_{file.filename}"
    saved_path = os.path.join(UPLOAD_DIR, raw_filename)
    
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Set output processed path
    processed_filename = f"processed_{raw_filename}"
    processed_path = os.path.join(PROCESSED_DIR, processed_filename)
    
    # Process file through ML engine
    success, total_rows, anomalies = ml_engine.process_upload_file(saved_path, processed_path)
    
    if not success:
        raise HTTPException(status_code=500, detail="Error executing machine learning models on Excel file")
        
    # Save record in db
    record = models.UploadRecord(
        user_id=current_user.id,
        filename=file.filename,
        saved_path=saved_path,
        processed_path=processed_path,
        record_count=total_rows,
        anomaly_count=anomalies,
        status="processed"
    )
    db.add(record)
    db.commit()
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/download/{record_id}")
async def get_download(
    record_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    record = db.query(models.UploadRecord).filter(models.UploadRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    # Users can only download their own uploads, unless they are Admin
    if record.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden access")
        
    if not os.path.exists(record.processed_path):
        raise HTTPException(status_code=404, detail="File on disk has been removed")
        
    return FileResponse(
        path=record.processed_path,
        filename=f"ML_Report_{record.filename}",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ── API LOGS ENDPOINTS ──────────────────────────────────────────────────────
@app.get("/api/history")
async def get_history(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if not current_user:
        return []
    records = db.query(models.UploadRecord).filter(models.UploadRecord.user_id == current_user.id).order_by(models.UploadRecord.upload_date.desc()).all()
    return [{
        "id": r.id,
        "filename": r.filename,
        "date": r.upload_date.strftime("%Y-%m-%d %H:%M:%S"),
        "rows": r.record_count,
        "anomalies": r.anomaly_count,
        "status": r.status
    } for r in records]

@app.get("/api/admin/stats")
async def get_admin_stats(
    admin_user: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(database.get_db)
):
    total_users = db.query(models.User).count()
    total_uploads = db.query(models.UploadRecord).count()
    records = db.query(models.UploadRecord).all()
    total_rows = sum(r.record_count for r in records)
    total_anomalies = sum(r.anomaly_count for r in records)
    
    all_uploads = db.query(models.UploadRecord).order_by(models.UploadRecord.upload_date.desc()).all()
    history = [{
        "id": r.id,
        "username": r.owner.username,
        "filename": r.filename,
        "date": r.upload_date.strftime("%Y-%m-%d %H:%M:%S"),
        "rows": r.record_count,
        "anomalies": r.anomaly_count
    } for r in all_uploads]
    
    return {
        "total_users": total_users,
        "total_uploads": total_uploads,
        "total_rows": total_rows,
        "total_anomalies": total_anomalies,
        "history": history
    }
