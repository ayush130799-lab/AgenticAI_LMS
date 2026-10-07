import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Assessment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "assessments"
    __table_args__ = (
        CheckConstraint(
            "assessment_type in ('diagnostic','module_quiz','course_exam','skill_check')",
            name="ck_assessment_type",
        ),
        CheckConstraint("level is null or level in ('beginner','intermediate','advanced')", name="ck_assessment_level"),
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    assessment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    module_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"))
    course_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"))
    passing_score: Mapped[float] = mapped_column(default=0.7)  # fraction 0-1 (module assessments: 0.8)
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer)
    # Module assessments (assessment_type == "module_quiz") only:
    level: Mapped[str | None] = mapped_column(String(20))
    required_coding_questions: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))

    questions: Mapped[list["Question"]] = relationship(back_populates="assessment", order_by="Question.order_index", cascade="all, delete-orphan")


class Question(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "questions"
    __table_args__ = (
        CheckConstraint(
            "question_type in ('mcq','multi_select','short_answer','coding','scenario','quiz')",
            name="ck_question_type",
        ),
    )

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("skills.id"))
    question_type: Mapped[str] = mapped_column(String(20), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    correct_answer: Mapped[dict] = mapped_column(JSONB, default=dict)
    explanation: Mapped[str | None] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(20), default="medium")
    points: Mapped[float] = mapped_column(default=1.0)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    # question_type "quiz": true_false | multi_select | scenario | short_answer
    quiz_format: Mapped[str | None] = mapped_column(String(20))
    # question_type "coding": language, starter_code, function_name, test_cases, expected_output, limits, solution
    coding_config: Mapped[dict | None] = mapped_column(JSONB)

    assessment: Mapped["Assessment"] = relationship(back_populates="questions")


class AssessmentAttempt(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "assessment_attempts"
    __table_args__ = (
        CheckConstraint("status in ('in_progress','submitted','graded')", name="ck_attempt_status"),
        UniqueConstraint("user_id", "assessment_id", "attempt_number", name="uq_attempt_number"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assessment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    answers: Mapped[dict] = mapped_column(JSONB, default=dict)
    score: Mapped[float | None] = mapped_column()
    skill_breakdown: Mapped[dict] = mapped_column(JSONB, default=dict)
    weak_concepts: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    status: Mapped[str] = mapped_column(default="in_progress")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Module assessment attempts (all NULL for the older assessment flow):
    attempt_number: Mapped[int | None] = mapped_column(Integer)
    percentage: Mapped[float | None] = mapped_column(Float)
    passed: Mapped[bool | None] = mapped_column(Boolean)
    mcq_score: Mapped[float | None] = mapped_column(Float)
    quiz_score: Mapped[float | None] = mapped_column(Float)
    coding_score: Mapped[float | None] = mapped_column(Float)
    coding_results: Mapped[dict | None] = mapped_column(JSONB)
    result_detail: Mapped[dict | None] = mapped_column(JSONB)

    answer_rows: Mapped[list["AssessmentAnswer"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")


class AssessmentAnswer(Base, UUIDMixin, TimestampMixin):
    """One graded answer of a module assessment attempt."""

    __tablename__ = "assessment_answers"
    __table_args__ = (UniqueConstraint("attempt_id", "question_id", name="uq_answer_attempt_question"),)

    attempt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assessment_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    answer: Mapped[dict | None] = mapped_column(JSONB)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    points_awarded: Mapped[float] = mapped_column(Float, default=0.0)
    coding_result: Mapped[dict | None] = mapped_column(JSONB)

    attempt: Mapped["AssessmentAttempt"] = relationship(back_populates="answer_rows")


class StudentSkill(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "student_skills"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_student_skill"),)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    mastery: Mapped[float] = mapped_column(default=0.0)
    confidence: Mapped[float] = mapped_column(default=0.0)
    level: Mapped[str] = mapped_column(String(20), default="beginner")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_assessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
