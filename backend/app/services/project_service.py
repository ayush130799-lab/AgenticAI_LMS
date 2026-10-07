from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import ActivityLog
from app.models.curriculum import Skill
from app.models.project import Project, ProjectSkill, ProjectSubmission
from app.services import planner_service, skill_service

from ai_engine.agents.project_mentor import ProjectMentorAgent

_mentor_agent = ProjectMentorAgent()


async def list_projects(db: AsyncSession, user_id: UUID) -> list[dict]:
    result = await db.execute(select(Project).order_by(Project.order_index))
    projects = result.scalars().all()

    submissions_result = await db.execute(select(ProjectSubmission).where(ProjectSubmission.user_id == user_id))
    latest_status = {}
    for sub in submissions_result.scalars().all():
        latest_status[sub.project_id] = sub.status

    return [
        {
            "id": p.id, "slug": p.slug, "title": p.title, "overview": p.overview, "difficulty": p.difficulty,
            "estimated_hours": p.estimated_hours, "order_index": p.order_index,
            "submission_status": latest_status.get(p.id),
        }
        for p in projects
    ]


async def get_project_detail(db: AsyncSession, project_id: UUID, user_id: UUID) -> dict:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    submission_result = await db.execute(
        select(ProjectSubmission).where(ProjectSubmission.project_id == project_id, ProjectSubmission.user_id == user_id)
        .order_by(ProjectSubmission.submitted_at.desc())
    )
    submission = submission_result.scalars().first()

    return {
        "id": project.id, "slug": project.slug, "title": project.title, "overview": project.overview,
        "difficulty": project.difficulty, "estimated_hours": project.estimated_hours, "order_index": project.order_index,
        "submission_status": submission.status if submission else None,
        "objective": project.objective, "prerequisites": project.prerequisites,
        "learning_outcomes": project.learning_outcomes, "requirements": project.requirements,
        "architecture": project.architecture, "milestones": project.milestones, "tasks": project.tasks,
        "expected_output": project.expected_output, "evaluation_criteria": project.evaluation_criteria,
        "resources": project.resources,
    }


async def submit_project(db: AsyncSession, user_id: UUID, project_id: UUID, repo_url: str | None, notes: str | None) -> ProjectSubmission:
    project_result = await db.execute(
        select(Project).where(Project.id == project_id).options(selectinload(Project.skills).selectinload(ProjectSkill.skill))
    )
    project = project_result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    submission = ProjectSubmission(
        user_id=user_id, project_id=project_id, repo_url=repo_url, submission_notes=notes,
        status="under_review", submitted_at=datetime.now(timezone.utc),
    )
    db.add(submission)
    await db.flush()

    project_dict = {
        "title": project.title, "objective": project.objective, "requirements": project.requirements,
        "tasks": project.tasks, "evaluation_criteria": project.evaluation_criteria,
        "skills": [{"slug": ps.skill.slug, "weight": ps.weight} for ps in project.skills],
    }
    review = _mentor_agent.review(project=project_dict, submission={"repo_url": repo_url, "submission_notes": notes or ""})

    submission.status = "evaluated"
    submission.score = review["score"]
    submission.ai_feedback = {
        "feedback": review["feedback"], "strengths": review["strengths"], "improvements": review["improvements"],
    }
    submission.evaluated_at = datetime.now(timezone.utc)

    db.add(ActivityLog(user_id=user_id, action="project_submitted", entity_type="project", entity_id=project_id, metadata_json={"title": project.title}))

    for skill_slug, score_percent in review["skill_updates"].items():
        skill_result = await db.execute(select(Skill).where(Skill.slug == skill_slug))
        skill = skill_result.scalar_one_or_none()
        if skill:
            await skill_service.apply_evidence(db, user_id, skill.id, score_percent, source="project", difficulty="hard")

    await db.commit()
    await db.refresh(submission)
    await planner_service.refresh_plan_after_evidence(db, user_id)
    return submission
