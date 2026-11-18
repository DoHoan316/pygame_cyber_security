from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(20), default="player")
    total_score = Column(Integer, default=0)
    security_hygiene_rank = Column(String(40), default="Tân Binh An Ninh")
    created_at = Column(DateTime, default=datetime.utcnow)

    progress_records = relationship("ProgressLog", back_populates="user")

class ProgressLog(Base):
    __tablename__ = "progress_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    scenario_id = Column(String(50), nullable=False)
    score_earned = Column(Integer, default=0)
    risk_level = Column(String(30), default="AN TOÀN")
    mistake_tag = Column(String(120), nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="progress_records")
