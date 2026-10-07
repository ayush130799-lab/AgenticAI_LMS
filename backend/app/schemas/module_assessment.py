from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ---- Requests (the client may only send answers/code - never scores, correctness or completion) ----
class SaveAnswersRequest(BaseModel):
    answers: dict[str, dict | None]


class SubmitAttemptRequest(BaseModel):
    # Omitted = grade the answers already autosaved on the attempt.
    answers: dict[str, dict | None] | None = None


class RunCodeRequest(BaseModel):
    code: str = Field(max_length=20_000)


# ---- Module progress -----------------------------------------------------------------
class AssessmentLevelOut(BaseModel):
    assessment_id: UUID
    level: str
    title: str
    required: bool
    passed: bool
    attempts_count: int
    best_percentage: float | None
    in_progress_attempt_id: UUID | None


class ModuleAssessmentStateOut(BaseModel):
    configured: bool
    status: str  # locked | available | in_progress | passed
    unavailable_reason: str | None
    required_level: str
    passed: bool
    attempts_count: int
    best_percentage: float | None
    levels: list[AssessmentLevelOut]


class ModuleProgressOut(BaseModel):
    module_id: UUID
    course_id: UUID
    title: str
    order_index: int
    status: str  # completed | in_progress | available | locked
    locked: bool
    locked_reason: str | None
    lessons_total: int
    lessons_completed: int
    all_lessons_completed: bool
    has_assessment: bool
    assessment: ModuleAssessmentStateOut | None


class ModuleAccessOut(BaseModel):
    module_id: UUID
    accessible: bool
    reason: str | None


class AssessmentSummaryOut(BaseModel):
    id: UUID
    module_id: UUID | None
    title: str
    description: str | None
    level: str | None
    is_published: bool
    total_questions: int
    mcq_count: int
    quiz_count: int
    coding_count: int
    passing_score_percent: float
    required_coding_questions: int
    time_limit_minutes: int | None


# ---- Taking an assessment (no answer key, no explanations, no hidden tests) --------------
class SampleTestOut(BaseModel):
    args: list
    expected: object


class CodingViewOut(BaseModel):
    language: str
    function_name: str
    starter_code: str
    expected_output: str
    sample_tests: list[SampleTestOut]
    hidden_test_count: int
    time_limit_seconds: float
    memory_limit_mb: int


class OptionOut(BaseModel):
    id: str
    text: str


class QuestionViewOut(BaseModel):
    id: UUID
    order: int
    type: str  # mcq | quiz | coding
    quiz_format: str | None
    prompt: str
    difficulty: str
    points: float
    options: list[OptionOut]
    coding: CodingViewOut | None


class AssessmentViewOut(AssessmentSummaryOut):
    questions: list[QuestionViewOut]


class AttemptOut(BaseModel):
    id: UUID
    assessment_id: UUID
    attempt_number: int | None
    status: str
    percentage: float | None
    passed: bool | None
    started_at: datetime
    submitted_at: datetime | None


class StartAttemptOut(BaseModel):
    attempt: AttemptOut
    assessment: AssessmentViewOut
    saved_answers: dict


class RunCodeOut(BaseModel):
    results: list[dict]
    passed_count: int
    total_count: int


# ---- Results ------------------------------------------------------------------------------
class CategoryScoreOut(BaseModel):
    correct: int
    total: int


class ResultOut(BaseModel):
    points_earned: float | None
    points_total: float | None
    percentage: float | None
    passed: bool
    questions_correct: int | None
    questions_total: int | None
    mcq: CategoryScoreOut
    quiz: CategoryScoreOut
    coding: CategoryScoreOut
    passing_percent: float | None
    required_coding: int | None
    score_requirement_met: bool | None
    coding_requirement_met: bool | None
    weak_concepts: list[str]


class QuestionResultOut(BaseModel):
    id: UUID
    order: int
    type: str
    quiz_format: str | None
    prompt: str
    points: float
    points_awarded: float
    is_correct: bool
    your_answer: dict | None
    options: list[OptionOut]
    coding: dict | None
    # Only populated after a PASS:
    explanation: str | None = None
    correct_answer: dict | None = None
    reference_solution: str | None = None


class NextModuleOut(BaseModel):
    module_id: UUID
    title: str
    status: str


class AttemptResultOut(BaseModel):
    attempt: AttemptOut
    assessment: AssessmentSummaryOut
    result: ResultOut | None
    questions: list[QuestionResultOut]
    module: ModuleProgressOut | None
    next_module: NextModuleOut | None = None
