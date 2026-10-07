import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Skill(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "skills"

    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_skill_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("skills.id"))

    prerequisites: Mapped[list["SkillPrerequisite"]] = relationship(
        foreign_keys="SkillPrerequisite.skill_id", back_populates="skill", cascade="all, delete-orphan"
    )


class SkillPrerequisite(Base, UUIDMixin):
    __tablename__ = "skill_prerequisites"
    __table_args__ = (UniqueConstraint("skill_id", "prerequisite_skill_id", name="uq_skill_prereq"),)

    skill_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    prerequisite_skill_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    required_mastery: Mapped[float] = mapped_column(default=0.6)

    skill: Mapped["Skill"] = relationship(foreign_keys=[skill_id], back_populates="prerequisites")


class Course(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "courses"

    slug: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    learning_outcomes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_hours: Mapped[float] = mapped_column(default=0)
    level: Mapped[str] = mapped_column(String(20), default="beginner")
    icon: Mapped[str | None] = mapped_column(String(50))
    is_published: Mapped[bool] = mapped_column(default=True)

    modules: Mapped[list["Module"]] = relationship(back_populates="course", order_by="Module.order_index", cascade="all, delete-orphan")


class Module(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "modules"
    __table_args__ = (UniqueConstraint("course_id", "slug", name="uq_module_course_slug"),)

    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_hours: Mapped[float] = mapped_column(default=0)

    course: Mapped["Course"] = relationship(back_populates="modules")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="module", order_by="Lesson.order_index", cascade="all, delete-orphan")


class Lesson(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("module_id", "slug", name="uq_lesson_module_slug"),
        CheckConstraint("lesson_type in ('reading','coding','video','project','quiz')", name="ck_lesson_type"),
    )

    module_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    lesson_type: Mapped[str] = mapped_column(String(20), default="reading")
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=20)

    learning_objectives: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    prerequisite_lesson_ids: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), default=list)

    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    examples: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    practice_exercises: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    resources: Mapped[list[dict]] = mapped_column(JSONB, default=list)

    module: Mapped["Module"] = relationship(back_populates="lessons")
    skills: Mapped[list["LessonSkill"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")


class LessonSkill(Base, UUIDMixin):
    __tablename__ = "lesson_skills"
    __table_args__ = (UniqueConstraint("lesson_id", "skill_id", name="uq_lesson_skill"),)

    lesson_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    weight: Mapped[float] = mapped_column(default=1.0)

    lesson: Mapped["Lesson"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship()
