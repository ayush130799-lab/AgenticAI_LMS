import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.curriculum import Course, Lesson, LessonSkill, Module, Skill, SkillPrerequisite
from app.models.enrollment import LessonProgress
from app.models.learning import LearningPlan, Recommendation
from app.models.user import StudentProfile
from app.models.user import User
from app.services import progression_service, skill_service

from ai_engine.agents.planner import PlannerAgent

_planner_agent = PlannerAgent()
logger = logging.getLogger(__name__)


async def refresh_plan_after_evidence(db: AsyncSession, user_id: UUID) -> None:
    """Regenerate the learning plan/recommendations after new mastery evidence.

    Best-effort: a planner failure must never fail the assessment/project submission that triggered it.
    """
    try:
        await generate_learning_plan(db, user_id)
    except Exception:
        await db.rollback()
        logger.exception("Could not refresh learning plan for user %s", user_id)


async def _build_curriculum_summary(db: AsyncSession, user_id: UUID) -> list[dict]:
    result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.modules).selectinload(Module.lessons).selectinload(Lesson.skills).selectinload(LessonSkill.skill)
        )
        .order_by(Course.order_index)
    )
    courses = result.scalars().all()

    completed_result = await db.execute(
        select(LessonProgress.lesson_id).where(LessonProgress.user_id == user_id, LessonProgress.status == "completed")
    )
    completed_ids = {row[0] for row in completed_result.all()}
    locked_modules = await progression_service.locked_module_ids(db, await db.get(User, user_id))

    summary = []
    for course in courses:
        for module in sorted(course.modules, key=lambda m: m.order_index):
            if module.id in locked_modules:
                continue  # recommending a lesson the student cannot open would be a dead end
            for lesson in sorted(module.lessons, key=lambda l: l.order_index):
                summary.append({
                    "course_slug": course.slug, "course_title": course.title,
                    "module_slug": module.slug, "module_title": module.title,
                    "lesson_id": str(lesson.id), "lesson_slug": lesson.slug, "lesson_title": lesson.title,
                    "skills": [ls.skill.slug for ls in lesson.skills],
                    "completed": lesson.id in completed_ids,
                })
    return summary


async def refresh_plan_in_background(user_id: UUID) -> None:
    """For FastAPI BackgroundTasks: refresh recommendations after the response has been sent.

    Planning can involve an LLM call taking many seconds; a student's submission must never wait on it.
    Uses its own session because the request's session is closed by then.
    """
    from app.db import session as session_module  # looked up at call time so tests can swap the factory

    async with session_module.AsyncSessionLocal() as db:
        await refresh_plan_after_evidence(db, user_id)


async def generate_learning_plan(db: AsyncSession, user_id: UUID) -> LearningPlan:
    skills = await skill_service.get_all_skills_with_defaults(db, user_id)
    profile_result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == user_id))
    profile = profile_result.scalar_one_or_none()

    prereq_rows = await db.execute(
        select(Skill.slug, SkillPrerequisite.prerequisite_skill_id, SkillPrerequisite.required_mastery)
        .join(SkillPrerequisite, SkillPrerequisite.skill_id == Skill.id)
    )
    slug_by_id = {row[0]: row[1] for row in (await db.execute(select(Skill.id, Skill.slug))).all()}
    skill_prereqs: dict[str, list[tuple[str, float]]] = {}
    for skill_slug, prereq_id, required in prereq_rows.all():
        skill_prereqs.setdefault(skill_slug, []).append((slug_by_id[prereq_id], required))

    # The planner reads {slug, name, ...}; the skill service returns {skill_slug, skill_name, ...}.
    agent_skills = [
        {
            "slug": s["skill_slug"], "name": s["skill_name"], "category": s["category"], "mastery": s["mastery"],
            "confidence": s["confidence"], "level": s["level"], "attempts": s["attempts"],
        }
        for s in skills
    ]

    student_context = {
        "skills": agent_skills,
        "skill_prereqs": skill_prereqs,
        "career_goal": profile.career_goal if profile else None,
        "target_role": profile.target_role if profile else None,
        "pace": profile.preferred_pace if profile else None,
        "recent_activity": [],
    }
    curriculum_summary = await _build_curriculum_summary(db, user_id)

    plan = _planner_agent.generate_plan(student_context=student_context, curriculum_summary=curriculum_summary)

    # deactivate previous plans
    prev_result = await db.execute(select(LearningPlan).where(LearningPlan.user_id == user_id, LearningPlan.is_active.is_(True)))
    for prev in prev_result.scalars().all():
        prev.is_active = False

    new_plan = LearningPlan(
        user_id=user_id, summary=plan["summary"], reasoning=plan["reasoning"],
        recommended_path=plan["recommended_path"], is_active=True,
    )
    db.add(new_plan)

    # replace standing recommendations with the fresh set
    old_recs = await db.execute(select(Recommendation).where(Recommendation.user_id == user_id, Recommendation.is_dismissed.is_(False)))
    for rec in old_recs.scalars().all():
        rec.is_dismissed = True

    for idx, step in enumerate(plan["recommended_path"]):
        db.add(Recommendation(
            user_id=user_id, recommendation_type=step["step_type"], target_id=step.get("target_id") or None,
            target_type="lesson" if step["step_type"] in ("lesson", "revision", "practice") else step["step_type"],
            title=step["title"], reason=step["reason"], priority=len(plan["recommended_path"]) - idx,
        ))

    await db.commit()
    await db.refresh(new_plan)
    return new_plan


async def get_active_plan(db: AsyncSession, user_id: UUID) -> LearningPlan | None:
    result = await db.execute(select(LearningPlan).where(LearningPlan.user_id == user_id, LearningPlan.is_active.is_(True)))
    return result.scalars().first()


async def list_recommendations(db: AsyncSession, user_id: UUID) -> list[Recommendation]:
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.user_id == user_id, Recommendation.is_dismissed.is_(False))
        .order_by(Recommendation.priority.desc())
    )
    return result.scalars().all()
