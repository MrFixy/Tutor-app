from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, TIMESTAMP, UniqueConstraint, func
)
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
    """A stored AI Engineering tutor exchange."""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    raw_text = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class LessonContent(Base):
    """Indexed copy of curated AI Engineering Markdown lesson files."""
    __tablename__ = "lesson_content"
    __table_args__ = (UniqueConstraint("domain", "subtopic", "language"),)

    id = Column(Integer, primary_key=True)
    domain = Column(String(32), nullable=False)
    subtopic = Column(String(255), nullable=False)
    language = Column(String(32), nullable=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    source_note = Column(String(255), nullable=True)


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    items = relationship("StudyPlanItem", back_populates="plan", cascade="all, delete-orphan")


class StudyPlanItem(Base):
    """A selected AI Engineering phase in a saved learning roadmap.

    The mapped column names keep existing pilot databases compatible; old
    rows from removed tracks are ignored by study_plan.list_plans().
    """
    __tablename__ = "study_plan_items"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False)
    curriculum = Column("domain", String(32), nullable=False, default="phases")
    phase_slug = Column("subtopic", String(255), nullable=False)
    order = Column(Integer, nullable=False, default=0)

    plan = relationship("StudyPlan", back_populates="items")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(16), nullable=False)
    view = Column(String(32), nullable=True)
    severity = Column(String(16), nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
