import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role in ('student','admin')", name="ck_users_role"),)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="student")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    profile: Mapped["StudentProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")


class StudentProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "student_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    programming_experience: Mapped[str | None] = mapped_column(String(20))
    python_experience: Mapped[str | None] = mapped_column(String(20))
    ai_ml_experience: Mapped[str | None] = mapped_column(String(20))
    llm_experience: Mapped[str | None] = mapped_column(String(20))
    rag_experience: Mapped[str | None] = mapped_column(String(20))
    agent_experience: Mapped[str | None] = mapped_column(String(20))
    langchain_experience: Mapped[str | None] = mapped_column(String(20))
    langgraph_experience: Mapped[str | None] = mapped_column(String(20))

    career_goal: Mapped[str | None] = mapped_column(String(255))
    target_role: Mapped[str | None] = mapped_column(String(255))
    available_hours_per_week: Mapped[int | None] = mapped_column(Integer)
    preferred_pace: Mapped[str | None] = mapped_column(String(20))

    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    diagnostic_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    current_streak_days: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[str | None] = mapped_column(String(10))

    bio: Mapped[str | None] = mapped_column(Text)
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)

    user: Mapped["User"] = relationship(back_populates="profile")
