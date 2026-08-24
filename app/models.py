from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user") # 'admin' or 'user'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    uploads = relationship("UploadRecord", back_populates="owner", cascade="all, delete-orphan")

class UploadRecord(Base):
    __tablename__ = "upload_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    saved_path = Column(String, nullable=False)
    processed_path = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    record_count = Column(Integer, default=0)
    anomaly_count = Column(Integer, default=0)
    status = Column(String, default="pending") # 'pending', 'processed', 'failed'

    # Relationships
    owner = relationship("User", back_populates="uploads")
