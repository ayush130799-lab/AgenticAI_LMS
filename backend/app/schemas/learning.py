from uuid import UUID

from pydantic import BaseModel, field_validator


class StudentSkillOut(BaseModel):
    skill_slug: str
    skill_name: str
    category: str
    mastery: float
    confidence: float
    level: str
    attempts: int


class RecommendationOut(BaseModel):
    id: UUID
    recommendation_type: str
    target_id: UUID | None
    target_type: str | None
    title: str
    reason: str
    priority: int

    class Config:
        from_attributes = True


class LearningPlanStepOut(BaseModel):
    step_type: str
    target_id: str | None
    title: str
    reason: str
    skill_focus: list[str] = []

    @field_validator("skill_focus", mode="before")
    @classmethod
    def _drop_empty_skills(cls, value):
        # Older stored plans may contain null skill entries; drop them rather than fail the whole plan.
        return [v for v in (value or []) if v]


class LearningPlanOut(BaseModel):
    id: UUID
    summary: str
    reasoning: str
    recommended_path: list[LearningPlanStepOut]

    class Config:
        from_attributes = True


class DashboardOut(BaseModel):
    full_name: str
    curriculum_progress_percent: float
    overall_skill_mastery_percent: float
    current_course: dict | None
    continue_lesson: dict | None
    pending_module_assessment: dict | None = None
    skills: list[StudentSkillOut]
    weak_skills: list[StudentSkillOut]
    recent_assessment: dict | None
    upcoming_assessment: dict | None
    active_projects: list[dict]
    learning_streak_days: int
    recommendations: list[RecommendationOut]


class OnboardingRequest(BaseModel):
    programming_experience: str
    python_experience: str
    ai_ml_experience: str
    llm_experience: str
    rag_experience: str
    agent_experience: str
    langchain_experience: str
    langgraph_experience: str
    career_goal: str
    target_role: str
    available_hours_per_week: int
    preferred_pace: str
