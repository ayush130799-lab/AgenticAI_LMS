from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SkillOut(BaseModel):
    id: UUID
    slug: str
    name: str
    description: str | None
    category: str
    parent_skill_id: UUID | None

    class Config:
        from_attributes = True


class LessonSummaryOut(BaseModel):
    id: UUID
    slug: str
    title: str
    description: str
    lesson_type: str
    order_index: int
    estimated_minutes: int
    progress_status: str | None = None

    class Config:
        from_attributes = True


class LessonDetailOut(LessonSummaryOut):
    learning_objectives: list[str]
    content_markdown: str
    examples: list[dict]
    practice_exercises: list[dict]
    resources: list[dict]
    skills: list[SkillOut] = []
    module_id: UUID
    course_id: UUID
    progress_status: str | None = None
    is_bookmarked: bool = False


class PracticeRunRequest(BaseModel):
    code: str = Field(max_length=20_000)


class PracticeRunOut(BaseModel):
    status: str  # ok | error | timeout
    stdout: str
    stderr: str
    error: str | None
    duration_ms: int


def _not_blank(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("must not be blank")
    return value


class NoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10_000)

    _strip = field_validator("content")(_not_blank)


class NoteOut(BaseModel):
    id: UUID
    lesson_id: UUID
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class HighlightCreate(BaseModel):
    text: str = Field(min_length=1, max_length=2_000)
    # Column is VARCHAR(20): a colour name ("yellow") or a hex value ("#fde68a").
    color: str = Field(default="yellow", pattern=r"^[A-Za-z0-9#_-]{1,20}$")

    _strip = field_validator("text")(_not_blank)


class HighlightOut(BaseModel):
    id: UUID
    lesson_id: UUID
    text: str
    color: str
    created_at: datetime

    class Config:
        from_attributes = True


class BookmarkOut(BaseModel):
    bookmarked: bool


class ModuleSummaryOut(BaseModel):
    id: UUID
    slug: str
    title: str
    description: str
    order_index: int
    estimated_hours: float
    lesson_count: int = 0
    completed_lesson_count: int = 0
    # Progression (server-derived; see progression_service). Defaults keep unauthenticated/legacy payloads valid.
    status: str | None = None  # completed | in_progress | available | locked
    locked: bool = False
    locked_reason: str | None = None
    all_lessons_completed: bool = False
    has_assessment: bool = False
    assessment_status: str | None = None  # locked | available | in_progress | passed
    assessment_unavailable_reason: str | None = None
    assessment_best_percentage: float | None = None

    class Config:
        from_attributes = True


class ModuleDetailOut(ModuleSummaryOut):
    lessons: list[LessonSummaryOut] = []


class CourseSummaryOut(BaseModel):
    id: UUID
    slug: str
    title: str
    subtitle: str | None
    description: str
    order_index: int
    estimated_hours: float
    level: str
    icon: str | None
    module_count: int = 0
    lesson_count: int = 0
    progress_percent: float | None = None

    class Config:
        from_attributes = True


class CourseDetailOut(CourseSummaryOut):
    modules_completed: int = 0
    learning_outcomes: list[str]
    modules: list[ModuleDetailOut] = []
