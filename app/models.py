from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, ForeignKey,
    TIMESTAMP, UniqueConstraint, func
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    sessions = relationship("SessionModel", back_populates="user")


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    ended_at = Column(TIMESTAMP(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    raw_text = Column(Text, nullable=False)
    intent_domain = Column(String(32), nullable=True)
    intent_subtopic = Column(String(64), nullable=True)
    intent_confidence = Column(Float, nullable=True)
    classified_json = Column(JSONB, nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    attempt_type = Column(String(16), nullable=False)  # 'quiz' | 'code'
    submission = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class MasteryScore(Base):
    __tablename__ = "mastery_score"
    __table_args__ = (UniqueConstraint("user_id", "domain", "subtopic"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    domain = Column(String(32), nullable=False)
    subtopic = Column(String(64), nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    attempts_count = Column(Integer, nullable=False, default=0)
    last_updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())


class LessonContent(Base):
    """Redesign: static, curated lesson library backing the Lessons tab.
    Populated by app/content_loader.py from content/lessons/ markdown
    files at startup -- the files are the source of truth, this table is
    just a queryable index over them. Never written to at request time."""
    __tablename__ = "lesson_content"
    __table_args__ = (UniqueConstraint("domain", "subtopic", "language"),)

    id = Column(Integer, primary_key=True)
    domain = Column(String(32), nullable=False)
    subtopic = Column(String(64), nullable=False)
    language = Column(String(32), nullable=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    source_note = Column(String(255), nullable=True)


class StudyPlan(Base):
    """Redesign: a saved roadmap from a goal-statement chat message
    ("I want to learn X"), checked off against LessonContent/mastery."""
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    items = relationship("StudyPlanItem", back_populates="plan", cascade="all, delete-orphan")


class StudyPlanItem(Base):
    __tablename__ = "study_plan_items"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False)
    domain = Column(String(32), nullable=False)
    subtopic = Column(String(64), nullable=False)
    language = Column(String(32), nullable=True)
    order = Column(Integer, nullable=False, default=0)

    plan = relationship("StudyPlan", back_populates="items")


class Feedback(Base):
    """Phase 6 / Week 13: pilot feedback -- captured both functional bugs
    and UI/UX friction, per the Week 13 brief. Written from the in-app
    feedback widget (frontend/src/components/FeedbackWidget.js) so a
    learner never has to leave the app to report something."""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(16), nullable=False)  # 'bug' | 'ux_friction' | 'other'
    view = Column(String(32), nullable=True)  # which screen it happened on: chat/practice/progress
    severity = Column(String(16), nullable=True)  # 'blocker' | 'annoying' | 'minor'
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
