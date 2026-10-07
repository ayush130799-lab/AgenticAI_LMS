from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProjectSummaryOut(BaseModel):
    id: UUID
    slug: str
    title: str
    overview: str
    difficulty: str
    estimated_hours: float
    order_index: int
    submission_status: str | None = None

    class Config:
        from_attributes = True


class ProjectDetailOut(ProjectSummaryOut):
    objective: str
    prerequisites: list[str]
    learning_outcomes: list[str]
    requirements: list[str]
    architecture: str
    milestones: list[dict]
    tasks: list[dict]
    expected_output: str
    evaluation_criteria: list[dict]
    resources: list[dict]


class ProjectSubmitRequest(BaseModel):
    repo_url: str | None = None
    submission_notes: str | None = None


class ProjectSubmissionOut(BaseModel):
    id: UUID
    status: str
    ai_feedback: dict
    score: float | None
    submitted_at: datetime

    class Config:
        from_attributes = True


class TutorChatRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None
    lesson_id: UUID | None = None


class TutorChatResponse(BaseModel):
    conversation_id: UUID
    reply: str
    citations: list[dict]
