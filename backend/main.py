from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import hashlib

from . import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Cyber Security Simulation API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuthRequest(BaseModel):
    username: str
    password: str

class ScoreSubmitRequest(BaseModel):
    user_id: int
    scenario_id: str
    score_earned: int
    risk_level: str
    mistake_tag: Optional[str] = None

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def calculate_rank(score: int) -> str:
    if score >= 2200:
        return "Bậc Thầy An Ninh Mạng"
    elif score >= 1400:
        return "Chuyên Gia Bảo Mật"
    elif score >= 700:
        return "Chiến Binh Phòng Thủ"
    elif score >= 250:
        return "Người Dùng Cảnh Giác"
    return "Tân Binh An Ninh"

@app.get("/")
def root():
    return {"message": "Cyber Security Game Backend v2.0 đang hoạt động!"}

@app.post("/api/auth/login")
def login_or_register(req: AuthRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == req.username).first()
    pw_hashed = hash_pw(req.password)

    if not user:
        user = models.User(username=req.username, password_hash=pw_hashed)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {
            "status": "registered",
            "user_id": user.id,
            "username": user.username,
            "total_score": user.total_score,
            "rank": user.security_hygiene_rank
        }

    if user.password_hash != pw_hashed:
        raise HTTPException(status_code=401, detail="Sai mật khẩu!")

    return {
        "status": "success",
        "user_id": user.id,
        "username": user.username,
        "total_score": user.total_score,
        "rank": user.security_hygiene_rank
    }

@app.post("/api/progress/submit")
def submit_progress(req: ScoreSubmitRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    log = models.ProgressLog(
        user_id=req.user_id,
        scenario_id=req.scenario_id,
        score_earned=req.score_earned,
        risk_level=req.risk_level,
        mistake_tag=req.mistake_tag
    )
    db.add(log)

    user.total_score = max(0, user.total_score + req.score_earned)
    user.security_hygiene_rank = calculate_rank(user.total_score)
    db.commit()
    db.refresh(user)

    return {
        "status": "saved",
        "total_score": user.total_score,
        "rank": user.security_hygiene_rank
    }

@app.get("/api/leaderboard")
def get_leaderboard(db: Session = Depends(database.get_db)):
    top_users = db.query(models.User).order_by(models.User.total_score.desc()).limit(10).all()
    return [
        {
            "username": u.username,
            "total_score": u.total_score,
            "rank": u.security_hygiene_rank
        }
        for u in top_users
    ]
