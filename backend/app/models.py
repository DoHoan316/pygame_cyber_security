from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, Float, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def utcnow(): return datetime.now(timezone.utc)

class User(Base):
    __tablename__='users'
    id: Mapped[int]=mapped_column(primary_key=True)
    email: Mapped[str]=mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    display_name: Mapped[str]=mapped_column(String(80))
    role: Mapped[str]=mapped_column(String(20), default='Player')
    is_active: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utcnow)
    sessions: Mapped[list['GameSession']]=relationship(back_populates='user')

class Campaign(Base):
    __tablename__='campaigns'
    id: Mapped[int]=mapped_column(primary_key=True)
    code: Mapped[str]=mapped_column(String(40), unique=True, index=True)
    title: Mapped[str]=mapped_column(String(180))
    description: Mapped[str]=mapped_column(Text)
    topic: Mapped[str]=mapped_column(String(120))
    order_no: Mapped[int]=mapped_column(Integer)
    is_active: Mapped[bool]=mapped_column(Boolean, default=True)
    scenarios: Mapped[list['Scenario']]=relationship(back_populates='campaign', cascade='all, delete-orphan')

class Scenario(Base):
    __tablename__='scenarios'
    id: Mapped[int]=mapped_column(primary_key=True)
    campaign_id: Mapped[int]=mapped_column(ForeignKey('campaigns.id'), index=True)
    code: Mapped[str]=mapped_column(String(50), unique=True, index=True)
    title: Mapped[str]=mapped_column(String(220))
    body: Mapped[str]=mapped_column(Text)
    learning_objective: Mapped[str]=mapped_column(Text)
    cia_dimension: Mapped[str]=mapped_column(String(120))
    is_start: Mapped[bool]=mapped_column(Boolean, default=False)
    campaign: Mapped[Campaign]=relationship(back_populates='scenarios')
    choices: Mapped[list['Choice']]=relationship(back_populates='scenario', cascade='all, delete-orphan', foreign_keys='Choice.scenario_id')

class Choice(Base):
    __tablename__='choices'
    id: Mapped[int]=mapped_column(primary_key=True)
    scenario_id: Mapped[int]=mapped_column(ForeignKey('scenarios.id'), index=True)
    code: Mapped[str]=mapped_column(String(8))
    choice_text: Mapped[str]=mapped_column(Text)
    consequence_text: Mapped[str]=mapped_column(Text)
    explanation_text: Mapped[str]=mapped_column(Text)
    safety_points: Mapped[int]=mapped_column(Integer, default=0)
    risk_points: Mapped[int]=mapped_column(Integer, default=0)
    error_category: Mapped[str|None]=mapped_column(String(60), nullable=True)
    next_scenario_id: Mapped[int|None]=mapped_column(ForeignKey('scenarios.id'), nullable=True)
    scenario: Mapped[Scenario]=relationship(back_populates='choices', foreign_keys=[scenario_id])

class GameSession(Base):
    __tablename__='game_sessions'
    __table_args__=(Index('ix_session_user_campaign_status','user_id','campaign_id','status'),)
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey('users.id'), index=True)
    campaign_id: Mapped[int]=mapped_column(ForeignKey('campaigns.id'), index=True)
    status: Mapped[str]=mapped_column(String(20), default='PLAYING')
    current_scenario_id: Mapped[int]=mapped_column(ForeignKey('scenarios.id'))
    pending_next_scenario_id: Mapped[int|None]=mapped_column(ForeignKey('scenarios.id'), nullable=True)
    pending_history_id: Mapped[int|None]=mapped_column(Integer, nullable=True)
    total_safety_points: Mapped[int]=mapped_column(Integer, default=0)
    total_risk_points: Mapped[int]=mapped_column(Integer, default=0)
    decision_count: Mapped[int]=mapped_column(Integer, default=0)
    safety_score: Mapped[float]=mapped_column(Float, default=0)
    risk_score: Mapped[float]=mapped_column(Float, default=0)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    completed_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)
    user: Mapped[User]=relationship(back_populates='sessions')

class ChoiceHistory(Base):
    __tablename__='choice_history'
    __table_args__=(UniqueConstraint('session_id','step_no',name='uq_history_session_step'),)
    id: Mapped[int]=mapped_column(primary_key=True)
    session_id: Mapped[int]=mapped_column(ForeignKey('game_sessions.id'), index=True)
    step_no: Mapped[int]=mapped_column(Integer)
    scenario_id: Mapped[int]=mapped_column(ForeignKey('scenarios.id'))
    choice_id: Mapped[int]=mapped_column(ForeignKey('choices.id'))
    safety_points: Mapped[int]=mapped_column(Integer)
    risk_points: Mapped[int]=mapped_column(Integer)
    error_category: Mapped[str|None]=mapped_column(String(60), nullable=True)
    selected_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utcnow)
