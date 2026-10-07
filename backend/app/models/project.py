import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.curriculum import Skill


class Project(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "projects"

    slug: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    overview: Mapped[str] = mapped_column(Text, nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    prerequisites: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    learning_outcomes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    requirements: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    architecture: Mapped[str] = mapped_column(Text, default="")
    milestones: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    tasks: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    expected_output: Mapped[str] = mapped_column(Text, default="")
    evaluation_criteria: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    resources: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    estimated_hours: Mapped[float] = mapped_column(default=8)
    difficulty: Mapped[str] = mapped_column(String(20), default="intermediate")

    skills: Mapped[list["ProjectSkill"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ProjectSkill(Base, UUIDMixin):
    __tablename__ = "project_skills"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    weight: Mapped[float] = mapped_column(default=1.0)

    project: Mapped["Project"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship()


class ProjectSubmission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "project_submissions"
    __table_args__ = (
        CheckConstraint("status in ('submitted','under_review','evaluated')", name="ck_submission_status"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    repo_url: Mapped[str | None] = mapped_column(String(500))
    submission_notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(default="submitted")
    ai_feedback: Mapped[dict] = mapped_column(JSONB, default=dict)
    score: Mapped[float | None] = mapped_column()
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
