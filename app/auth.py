from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import database
import models

# Security configurations
SECRET_KEY = "SUPER_SECRET_WATER_FILTRATION_KEY_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Helper to read JWT from Cookie instead of Authorization Header (easier for standard HTML forms)
async def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    # Cookie value might be 'Bearer token_value'
    if token.startswith("Bearer "):
        token = token[7:]
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_411_LENGTH_REQUIRED, # redirect/fail helper
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
        
    user = db.query(models.User).filter(models.User.username == username).first()
    return user

async def get_current_admin(user: Optional[models.User] = Depends(get_current_user)):
    if not user or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have administrative privileges",
        )
    return user
