
import os
import json

from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from pydantic import BaseModel, EmailStr, Field

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, desc
from sqlalchemy.exc import IntegrityError

from .database import Base, engine, get_db, SessionLocal
from .models import User, Campaign, Scenario, Choice, GameSession, ChoiceHistory
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    current_user,
    admin_user,
)


# =========================================================
# LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app):
    with SessionLocal() as db:
        seed_database(db)

        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if (
            admin_email
            and admin_password
            and not db.query(User).filter(
                User.email == admin_email.lower()
            ).first()
        ):
            db.add(
                User(
                    email=admin_email.lower(),
                    password_hash=hash_password(admin_password),
                    display_name="Quản trị viên",
                    role="Admin",
                )
            )
            db.commit()

    yield


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="CyberSafe API",
    version="3.0.0",
    description="Backend chiến dịch mô phỏng an toàn thông tin",
    lifespan=lifespan,
)


# =========================================================
# STATIC FILES
# =========================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]
ARCHIVES_DIR = PROJECT_DIR / "archives"

app.mount(
    "/app",
    StaticFiles(directory=PROJECT_DIR / "admin_web", html=True),
    name="webapp",
)

app.mount(
    "/archives",
    StaticFiles(directory=ARCHIVES_DIR),
    name="archives",
)


# =========================================================
# CORS CONFIGURATION
# =========================================================

origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST MODELS
# =========================================================

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=80)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class StartIn(BaseModel):
    campaign_id: int


class ChoiceIn(BaseModel):
    scenario_id: int
    choice_id: int


class StatusIn(BaseModel):
    is_active: bool


# =========================================================
# RESPONSE HELPERS
# =========================================================

def ok(data, message="Thành công"):
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def fail(message, code="INVALID_REQUEST", details=None):
    return {
        "success": False,
        "message": message,
        "error_code": code,
        "details": details or {},
    }


# =========================================================
# EXCEPTION HANDLERS
# =========================================================

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    details = [
        {
            "field": ".".join(str(x) for x in error.get("loc", [])),
            "message": error.get("msg", "Invalid value"),
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content=fail(
            "Dữ liệu gửi lên không hợp lệ",
            "INVALID_INPUT",
            {"errors": details},
        ),
    )


@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException):
    error_code = {
        400: "INVALID_INPUT",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
    }.get(exc.status_code, "REQUEST_FAILED")

    return JSONResponse(
        status_code=exc.status_code,
        content=fail(str(exc.detail), error_code),
    )


# =========================================================
# VALIDATE SEED DATA
# =========================================================

def validate_seed_payload(payload):
    for campaign in payload:
        nodes = campaign["scenarios"]
        nodes_by_code = {node["code"]: node for node in nodes}

        starts = [
            node for node in nodes
            if node["is_start"]
        ]

        if len(starts) != 1:
            raise ValueError(
                f"{campaign['code']}: cần đúng một start node"
            )

        for node in nodes:
            if not 2 <= len(node["choices"]) <= 4:
                raise ValueError(
                    f"{node['code']}: số lựa chọn không hợp lệ"
                )

            for choice in node["choices"]:
                if (
                    not choice["choice_text"]
                    or not choice["consequence_text"]
                    or not choice["explanation_text"]
                ):
                    raise ValueError(
                        f"{node['code']}: thiếu nội dung choice"
                    )

                next_code = choice.get("next_scenario_code")

                if next_code and next_code not in nodes_by_code:
                    raise ValueError(
                        f"{node['code']}: nhánh {next_code} "
                        "không thuộc campaign"
                    )

        # Kiểm tra tất cả node có thể đi tới từ node bắt đầu.
        seen = set()
        stack = [starts[0]["code"]]

        while stack:
            code = stack.pop()

            if code in seen:
                continue

            seen.add(code)

            for choice in nodes_by_code[code]["choices"]:
                next_code = choice.get("next_scenario_code")

                if next_code:
                    stack.append(next_code)

        if seen != set(nodes_by_code):
            unreachable = set(nodes_by_code) - seen

            raise ValueError(
                f"{campaign['code']}: node không thể đi tới: "
                f"{unreachable}"
            )

        # Kiểm tra vòng lặp và bảo đảm các nhánh có thể kết thúc.
        visiting = set()
        done = set()

        def visit(code):
            if code in visiting:
                raise ValueError(
                    f"{campaign['code']}: phát hiện vòng lặp tại {code}"
                )

            if code in done:
                return

            visiting.add(code)

            for choice in nodes_by_code[code]["choices"]:
                next_code = choice.get("next_scenario_code")

                if next_code:
                    visit(next_code)

            visiting.remove(code)
            done.add(code)

        visit(starts[0]["code"])


# =========================================================
# SEED DATABASE
# =========================================================

def seed_database(db: Session):
    seed_path = (
        Path(__file__).resolve().parents[2]
        / "seed_data"
        / "campaigns.json"
    )

    if not seed_path.exists():
        return

    payload = json.loads(
        seed_path.read_text(encoding="utf-8")
    )

    validate_seed_payload(payload)

    if db.query(Campaign).count():
        return

    for item in payload:
        campaign = Campaign(
            code=item["code"],
            title=item["title"],
            description=item["description"],
            topic=item["topic"],
            order_no=item["order_no"],
            is_active=True,
        )

        db.add(campaign)
        db.flush()

        scenario_map = {}

        for node in item["scenarios"]:
            scenario = Scenario(
                campaign_id=campaign.id,
                code=node["code"],
                title=node["title"],
                body=node["body"],
                learning_objective=node["learning_objective"],
                cia_dimension=node["cia_dimension"],
                is_start=node["is_start"],
            )

            db.add(scenario)
            db.flush()

            scenario_map[node["code"]] = scenario

        for node in item["scenarios"]:
            scenario = scenario_map[node["code"]]

            for choice in node["choices"]:
                next_code = choice.get("next_scenario_code")

                db.add(
                    Choice(
                        scenario_id=scenario.id,
                        code=choice["code"],
                        choice_text=choice["choice_text"],
                        consequence_text=choice["consequence_text"],
                        explanation_text=choice["explanation_text"],
                        safety_points=choice["safety_points"],
                        risk_points=choice["risk_points"],
                        error_category=choice["error_category"],
                        next_scenario_id=(
                            scenario_map[next_code].id
                            if next_code else None
                        ),
                    )
                )

    db.commit()


# =========================================================
# GAME SCORING
# =========================================================

def score_session(session):
    total = (
        session.total_safety_points
        + session.total_risk_points
    )

    session.safety_score = (
        round(session.total_safety_points / total * 100, 2)
        if total else 0.0
    )

    session.risk_score = (
        round(session.total_risk_points / total * 100, 2)
        if total else 0.0
    )


def rank_for(score):
    if score >= 90:
        return "Chuyên gia an toàn"

    if score >= 75:
        return "Người dùng cảnh giác"

    if score >= 50:
        return "Đang tiến bộ"

    return "Cần rèn luyện thêm"


# =========================================================
# GAME SESSION RESPONSE
# =========================================================

def session_payload(db: Session, session):
    scenario = (
        db.query(Scenario)
        .options(joinedload(Scenario.choices))
        .filter(Scenario.id == session.current_scenario_id)
        .first()
    )

    pending = None

    if session.status == "FEEDBACK" and session.pending_history_id:
        history = db.get(
            ChoiceHistory,
            session.pending_history_id,
        )

        choice = (
            db.get(Choice, history.choice_id)
            if history else None
        )

        if choice:
            pending = {
                "choice_id": choice.id,
                "choice_code": choice.code,
                "consequence": choice.consequence_text,
                "explanation": choice.explanation_text,
                "safety_points": choice.safety_points,
                "risk_points": choice.risk_points,
                "error_category": choice.error_category,
            }

    current_scenario = None

    if session.status != "COMPLETED" and scenario:
        current_scenario = {
            "id": scenario.id,
            "code": scenario.code,
            "title": scenario.title,
            "body": scenario.body,
            "learning_objective": scenario.learning_objective,
            "cia_dimension": scenario.cia_dimension,
            "choices": [
                {
                    "id": choice.id,
                    "code": choice.code,
                    "text": choice.choice_text,
                }
                for choice in sorted(
                    scenario.choices,
                    key=lambda item: item.code,
                )
            ],
        }

    return {
        "id": session.id,
        "campaign_id": session.campaign_id,
        "status": session.status,
        "current_scenario": current_scenario,
        "feedback": pending,
        "decision_count": session.decision_count,
        "safety_score": session.safety_score,
        "risk_score": session.risk_score,
    }


# =========================================================
# GENERAL API
# =========================================================

@app.get("/")
def root():
    return ok({
        "name": "CyberSafe",
        "version": "3.0.0",
        "docs": "/docs",
    })


@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    db.execute(select(1))

    return ok({
        "status": "healthy",
        "database": "connected",
    })


# =========================================================
# AUTHENTICATION
# =========================================================

@app.post("/api/auth/register", status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower().strip()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "Email đã được sử dụng")

    user = User(
        email=email,
        password_hash=hash_password(data.password),
        display_name=data.display_name.strip(),
        role="Player",
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email đã được sử dụng")

    token = create_access_token(user)

    return ok(
        {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "role": user.role,
            },
        },
        "Đăng ký thành công",
    )


@app.post("/api/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.email == data.email.lower().strip())
        .first()
    )

    if not user or not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            401,
            "Email hoặc mật khẩu không chính xác",
        )

    if not user.is_active:
        raise HTTPException(
            403,
            "Tài khoản đã bị vô hiệu hóa",
        )

    return ok(
        {
            "access_token": create_access_token(user),
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "role": user.role,
            },
        },
        "Đăng nhập thành công",
    )


@app.get("/api/auth/me")
def me(user: User = Depends(current_user)):
    return ok({
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role,
        "is_active": user.is_active,
    })


# =========================================================
# CAMPAIGNS
# =========================================================

@app.get("/api/campaigns")
def campaigns(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    rows = (
        db.query(Campaign)
        .filter(Campaign.is_active == True)
        .order_by(Campaign.order_no)
        .all()
    )

    output = []

    for campaign in rows:
        count = (
            db.query(Scenario)
            .filter(Scenario.campaign_id == campaign.id)
            .count()
        )

        active = (
            db.query(GameSession)
            .filter(
                GameSession.user_id == user.id,
                GameSession.campaign_id == campaign.id,
                GameSession.status != "COMPLETED",
            )
            .first()
        )

        completed = (
            db.query(GameSession)
            .filter(
                GameSession.user_id == user.id,
                GameSession.campaign_id == campaign.id,
                GameSession.status == "COMPLETED",
            )
            .count()
        )

        output.append({
            "id": campaign.id,
            "code": campaign.code,
            "title": campaign.title,
            "description": campaign.description,
            "topic": campaign.topic,
            "scenario_count": count,
            "active_session_id": active.id if active else None,
            "completed_attempts": completed,
        })

    return ok(output)


@app.get("/api/campaigns/{campaign_id}")
def campaign_detail(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    campaign = db.get(Campaign, campaign_id)

    if not campaign or not campaign.is_active:
        raise HTTPException(
            404,
            "Không tìm thấy chiến dịch",
        )

    return ok({
        "id": campaign.id,
        "code": campaign.code,
        "title": campaign.title,
        "description": campaign.description,
        "topic": campaign.topic,
        "scenario_count": (
            db.query(Scenario)
            .filter(Scenario.campaign_id == campaign.id)
            .count()
        ),
    })


# =========================================================
# GAME SESSIONS
# =========================================================

@app.post("/api/game/sessions")
def start_session(
    data: StartIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    campaign = db.get(Campaign, data.campaign_id)

    if not campaign or not campaign.is_active:
        raise HTTPException(
            404,
            "Chiến dịch không tồn tại",
        )

    existing = (
        db.query(GameSession)
        .filter(
            GameSession.user_id == user.id,
            GameSession.campaign_id == campaign.id,
            GameSession.status.in_(["PLAYING", "FEEDBACK"]),
        )
        .first()
    )

    if existing:
        return ok(
            session_payload(db, existing),
            "Tiếp tục phiên đang chơi",
        )

    start = (
        db.query(Scenario)
        .filter(
            Scenario.campaign_id == campaign.id,
            Scenario.is_start == True,
        )
        .first()
    )

    if not start:
        raise HTTPException(
            500,
            "Chiến dịch chưa có tình huống bắt đầu",
        )

    session = GameSession(
        user_id=user.id,
        campaign_id=campaign.id,
        current_scenario_id=start.id,
        status="PLAYING",
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return ok(
        session_payload(db, session),
        "Đã bắt đầu chiến dịch",
    )


@app.get("/api/game/sessions/{session_id}")
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    session = db.get(GameSession, session_id)

    if not session or session.user_id != user.id:
        raise HTTPException(
            404,
            "Không tìm thấy phiên chơi",
        )

    return ok(session_payload(db, session))


@app.post("/api/game/sessions/{session_id}/choices")
def submit_choice(
    session_id: int,
    data: ChoiceIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    session = (
        db.query(GameSession)
        .filter(
            GameSession.id == session_id,
            GameSession.user_id == user.id,
        )
        .with_for_update()
        .first()
    )

    if not session:
        raise HTTPException(404, "Không tìm thấy phiên chơi")

    if session.status != "PLAYING":
        raise HTTPException(
            409,
            "Phiên không ở trạng thái nhận lựa chọn",
        )

    if session.current_scenario_id != data.scenario_id:
        raise HTTPException(
            409,
            "Tình huống hiện tại đã thay đổi",
        )

    choice = (
        db.query(Choice)
        .filter(
            Choice.id == data.choice_id,
            Choice.scenario_id == data.scenario_id,
        )
        .first()
    )

    if not choice:
        raise HTTPException(
            400,
            "Lựa chọn không thuộc tình huống hiện tại",
        )

    step = session.decision_count + 1

    existing_history = (
        db.query(ChoiceHistory)
        .filter(
            ChoiceHistory.session_id == session.id,
            ChoiceHistory.step_no == step,
        )
        .first()
    )

    if existing_history:
        raise HTTPException(
            409,
            "Lựa chọn đã được ghi nhận",
        )

    history = ChoiceHistory(
        session_id=session.id,
        step_no=step,
        scenario_id=data.scenario_id,
        choice_id=choice.id,
        safety_points=choice.safety_points,
        risk_points=choice.risk_points,
        error_category=choice.error_category,
    )

    db.add(history)
    db.flush()

    session.total_safety_points += choice.safety_points
    session.total_risk_points += choice.risk_points
    session.decision_count = step
    session.pending_next_scenario_id = choice.next_scenario_id
    session.pending_history_id = history.id
    session.status = "FEEDBACK"

    score_session(session)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            409,
            "Lựa chọn đã được ghi nhận ở một yêu cầu khác",
        )

    db.refresh(session)

    return ok(
        session_payload(db, session),
        "Đã ghi nhận lựa chọn",
    )


@app.post("/api/game/sessions/{session_id}/continue")
def continue_session(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    session = (
        db.query(GameSession)
        .filter(
            GameSession.id == session_id,
            GameSession.user_id == user.id,
        )
        .with_for_update()
        .first()
    )

    if not session:
        raise HTTPException(404, "Không tìm thấy phiên chơi")

    if session.status != "FEEDBACK":
        raise HTTPException(
            409,
            "Phiên không ở trạng thái feedback",
        )

    next_scenario = session.pending_next_scenario_id

    session.pending_next_scenario_id = None
    session.pending_history_id = None

    if next_scenario is None:
        session.status = "COMPLETED"
        session.completed_at = datetime.now(timezone.utc)

    else:
        session.current_scenario_id = next_scenario
        session.status = "PLAYING"

    score_session(session)

    db.commit()
    db.refresh(session)

    message = (
        "Chiến dịch đã hoàn thành"
        if session.status == "COMPLETED"
        else "Tiếp tục chiến dịch"
    )

    return ok(
        session_payload(db, session),
        message,
    )


@app.get("/api/game/sessions/{session_id}/result")
def result(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    session = db.get(GameSession, session_id)

    if not session or session.user_id != user.id:
        raise HTTPException(
            404,
            "Không tìm thấy phiên chơi",
        )

    if session.status != "COMPLETED":
        raise HTTPException(
            409,
            "Chiến dịch chưa hoàn thành",
        )

    return ok({
        "session_id": session.id,
        "campaign_id": session.campaign_id,
        "status": session.status,
        "decision_count": session.decision_count,
        "total_safety_points": session.total_safety_points,
        "total_risk_points": session.total_risk_points,
        "safety_score": session.safety_score,
        "risk_score": session.risk_score,
        "rank": rank_for(session.safety_score),
        "completed_at": (
            session.completed_at.isoformat()
            if session.completed_at else None
        ),
    })


# =========================================================
# PLAYER DASHBOARD
# =========================================================

@app.get("/api/me/dashboard")
def player_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    sessions = (
        db.query(GameSession)
        .filter(GameSession.user_id == user.id)
        .all()
    )

    completed = [
        session for session in sessions
        if session.status == "COMPLETED"
    ]

    errors = (
        db.query(
            ChoiceHistory.error_category,
            func.count(ChoiceHistory.id),
        )
        .join(
            GameSession,
            ChoiceHistory.session_id == GameSession.id,
        )
        .filter(
            GameSession.user_id == user.id,
            ChoiceHistory.error_category.isnot(None),
        )
        .group_by(ChoiceHistory.error_category)
        .all()
    )

    return ok({
        "campaigns_completed": len({
            session.campaign_id for session in completed
        }),
        "sessions_completed": len(completed),
        "sessions_in_progress": sum(
            session.status != "COMPLETED"
            for session in sessions
        ),
        "average_safety_score": (
            round(
                sum(session.safety_score for session in completed)
                / len(completed),
                2,
            )
            if completed else 0
        ),
        "best_safety_score": max(
            (session.safety_score for session in completed),
            default=0,
        ),
        "error_groups": [
            {
                "category": category,
                "count": count,
            }
            for category, count in errors
        ],
    })


@app.get("/api/me/history")
def player_history(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    rows = (
        db.query(GameSession)
        .filter(GameSession.user_id == user.id)
        .order_by(GameSession.created_at.desc())
        .limit(100)
        .all()
    )

    output = []

    for session in rows:
        campaign = db.get(Campaign, session.campaign_id)

        output.append({
            "session_id": session.id,
            "campaign": campaign.title if campaign else None,
            "status": session.status,
            "safety_score": session.safety_score,
            "risk_score": session.risk_score,
            "decision_count": session.decision_count,
            "created_at": session.created_at.isoformat(),
            "completed_at": (
                session.completed_at.isoformat()
                if session.completed_at else None
            ),
        })

    return ok(output)


@app.get("/api/me/errors")
def player_errors(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    rows = (
        db.query(
            ChoiceHistory.error_category,
            func.count(ChoiceHistory.id),
        )
        .join(
            GameSession,
            ChoiceHistory.session_id == GameSession.id,
        )
        .filter(
            GameSession.user_id == user.id,
            ChoiceHistory.error_category.isnot(None),
        )
        .group_by(ChoiceHistory.error_category)
        .order_by(desc(func.count(ChoiceHistory.id)))
        .all()
    )

    return ok([
        {
            "error_category": category,
            "count": count,
        }
        for category, count in rows
    ])


# =========================================================
# LEADERBOARD
# =========================================================

@app.get("/api/leaderboard/{campaign_id}")
def leaderboard(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    if not db.get(Campaign, campaign_id):
        raise HTTPException(
            404,
            "Chiến dịch không tồn tại",
        )

    rows = (
        db.query(GameSession, User)
        .join(User, User.id == GameSession.user_id)
        .filter(
            GameSession.campaign_id == campaign_id,
            GameSession.status == "COMPLETED",
        )
        .order_by(
            GameSession.safety_score.desc(),
            GameSession.risk_score.asc(),
            GameSession.completed_at.asc(),
        )
        .all()
    )

    best = {}

    for session, user_item in rows:
        if user_item.id not in best:
            best[user_item.id] = {
                "display_name": user_item.display_name,
                "safety_score": session.safety_score,
                "risk_score": session.risk_score,
                "completed_at": (
                    session.completed_at.isoformat()
                    if session.completed_at else None
                ),
            }

    return ok(
        sorted(
            best.values(),
            key=lambda item: (
                -item["safety_score"],
                item["risk_score"],
                item["completed_at"] or "",
            ),
        )[:10]
    )


# =========================================================
# ADMIN - USERS
# =========================================================

@app.get("/api/admin/users")
def admin_users(
    q: str = "",
    offset: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_user),
):
    query = db.query(User)

    if q:
        query = query.filter(
            (User.email.ilike(f"%{q}%"))
            | (User.display_name.ilike(f"%{q}%"))
        )

    total = query.count()

    users = (
        query.order_by(User.created_at.desc())
        .offset(max(offset, 0))
        .limit(min(max(limit, 1), 100))
        .all()
    )

    return ok({
        "total": total,
        "items": [
            {
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ],
    })


@app.get("/api/admin/users/{user_id}")
def admin_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_user),
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            404,
            "Không tìm thấy người dùng",
        )

    return ok({
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
    })


@app.patch("/api/admin/users/{user_id}/status")
def admin_user_status(
    user_id: int,
    data: StatusIn,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_user),
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            404,
            "Không tìm thấy người dùng",
        )

    if user.id == admin.id and not data.is_active:
        raise HTTPException(
            400,
            "Không thể tự vô hiệu hóa tài khoản đang đăng nhập",
        )

    user.is_active = data.is_active
    db.commit()

    return ok(
        {
            "id": user.id,
            "is_active": user.is_active,
        },
        "Đã cập nhật trạng thái tài khoản",
    )


# =========================================================
# ADMIN - ANALYTICS
# =========================================================

@app.get("/api/admin/analytics/overview")
def admin_overview(
    db: Session = Depends(get_db),
    admin: User = Depends(admin_user),
):
    total_users = db.query(User).count()

    active_users = (
        db.query(User)
        .filter(User.is_active == True)
        .count()
    )

    total_sessions = db.query(GameSession).count()

    completed = (
        db.query(GameSession)
        .filter(GameSession.status == "COMPLETED")
        .count()
    )

    average_score = (
        db.query(func.avg(GameSession.safety_score))
        .filter(GameSession.status == "COMPLETED")
        .scalar()
        or 0
    )

    campaign_stats = []

    for campaign in db.query(Campaign).order_by(Campaign.order_no):
        total = (
            db.query(GameSession)
            .filter(GameSession.campaign_id == campaign.id)
            .count()
        )

        done = (
            db.query(GameSession)
            .filter(
                GameSession.campaign_id == campaign.id,
                GameSession.status == "COMPLETED",
            )
            .count()
        )

        campaign_stats.append({
            "campaign": campaign.title,
            "sessions": total,
            "completed": done,
        })

    errors = (
        db.query(
            ChoiceHistory.error_category,
            func.count(ChoiceHistory.id),
        )
        .filter(ChoiceHistory.error_category.isnot(None))
        .group_by(ChoiceHistory.error_category)
        .order_by(desc(func.count(ChoiceHistory.id)))
        .all()
    )

    return ok({
        "users_total": total_users,
        "users_active": active_users,
        "sessions_total": total_sessions,
        "sessions_completed": completed,
        "completion_rate": (
            round(completed / total_sessions * 100, 2)
            if total_sessions else 0
        ),
        "average_safety_score": round(float(average_score), 2),
        "campaigns": campaign_stats,
        "common_errors": [
            {
                "category": category,
                "count": count,
            }
            for category, count in errors
        ],
    })
