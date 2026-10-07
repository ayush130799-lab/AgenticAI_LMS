from uuid import UUID

from pydantic import BaseModel


class CourseAdminIn(BaseModel):
    slug: str
    title: str
    subtitle: str | None = None
    description: str
    learning_outcomes: list[str] = []
    order_index: int = 0
    estimated_hours: float = 0
    level: str = "beginner"
    icon: str | None = None
    is_published: bool = True


class ModuleAdminIn(BaseModel):
    course_id: UUID
    slug: str
    title: str
    description: str
    order_index: int = 0
    estimated_hours: float = 0


class LessonAdminIn(BaseModel):
    module_id: UUID
    slug: str
    title: str
    description: str
    lesson_type: str = "reading"
    order_index: int = 0
    estimated_minutes: int = 20
    learning_objectives: list[str] = []
    content_markdown: str
    examples: list[dict] = []
    practice_exercises: list[dict] = []
    resources: list[dict] = []
    skill_slugs: list[str] = []


class SkillAdminIn(BaseModel):
    slug: str
    name: str
    description: str | None = None
    category: str
    parent_slug: str | None = None


class ProjectAdminIn(BaseModel):
    slug: str
    title: str
    overview: str
    objective: str
    prerequisites: list[str] = []
    learning_outcomes: list[str] = []
    requirements: list[str] = []
    architecture: str = ""
    milestones: list[dict] = []
    tasks: list[dict] = []
    expected_output: str = ""
    evaluation_criteria: list[dict] = []
    resources: list[dict] = []
    order_index: int = 0
    estimated_hours: float = 8
    difficulty: str = "intermediate"
    skill_slugs: list[str] = []


class QuestionAdminIn(BaseModel):
    question_type: str
    prompt: str
    options: list[dict] = []
    correct_answer: dict = {}
    explanation: str | None = None
    difficulty: str = "medium"
    points: float = 1.0
    order_index: int = 0
    skill_slug: str | None = None


class AssessmentAdminIn(BaseModel):
    title: str
    description: str | None = None
    assessment_type: str
    module_id: UUID | None = None
    course_id: UUID | None = None
    passing_score: float = 0.7
    time_limit_minutes: int | None = None
    questions: list[QuestionAdminIn] = []


class AdminUserOut(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class ModuleAssessmentAdminIn(BaseModel):
    """A standard module assessment: exactly 3 MCQ + 2 quiz + 2 coding (validated on save and on publish)."""

    module_id: UUID
    level: str
    title: str
    description: str | None = None
    passing_score: float = 80  # percent
    required_coding_questions: int = 1
    time_limit_minutes: int | None = None
    questions: list[dict]
    publish: bool = False
