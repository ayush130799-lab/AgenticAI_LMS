from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class QuestionOut(BaseModel):
    id: UUID
    question_type: str
    prompt: str
    options: list[dict]
    difficulty: str
    points: float

    class Config:
        from_attributes = True


class AssessmentListItemOut(BaseModel):
    id: UUID
    title: str
    description: str | None
    assessment_type: str
    passing_score: float
    time_limit_minutes: int | None
    question_count: int
    last_score_percent: float | None = None


class AssessmentOut(BaseModel):
    id: UUID
    title: str
    description: str | None
    assessment_type: str
    passing_score: float
    time_limit_minutes: int | None
    questions: list[QuestionOut] = []

    class Config:
        from_attributes = True


class StartAssessmentRequest(BaseModel):
    assessment_id: UUID


class StartAssessmentResponse(BaseModel):
    attempt_id: UUID
    assessment: AssessmentOut


class SubmitAssessmentRequest(BaseModel):
    attempt_id: UUID
    answers: dict[str, dict]


class SkillResultOut(BaseModel):
    skill_slug: str
    skill_name: str
    score_percent: float
    mastery_after: float


class SubmitAssessmentResponse(BaseModel):
    attempt_id: UUID
    score: float
    passed: bool
    skill_breakdown: list[SkillResultOut]
    weak_concepts: list[str]
    strengths: list[str]
    recommended_next_steps: list[str]


class DiagnosticResultOut(BaseModel):
    attempt_id: UUID
    skill_profile: dict[str, float]
    strengths: list[str]
    weaknesses: list[str]
    prerequisite_gaps: list[str]
    recommended_starting_point: str
    confidence: float
