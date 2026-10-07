from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import StudentSkill
from app.models.curriculum import Skill

from ai_engine.agents.skill import SkillAnalysisAgent

_skill_agent = SkillAnalysisAgent()


async def get_or_create_student_skill(db: AsyncSession, user_id: UUID, skill_id: UUID) -> StudentSkill:
    result = await db.execute(select(StudentSkill).where(StudentSkill.user_id == user_id, StudentSkill.skill_id == skill_id))
    record = result.scalar_one_or_none()
    if record is None:
        record = StudentSkill(user_id=user_id, skill_id=skill_id, mastery=0.0, confidence=0.0, level="beginner", attempts=0)
        db.add(record)
        await db.flush()
    return record


async def apply_evidence(
    db: AsyncSession, user_id: UUID, skill_id: UUID, score_percent: float, source: str, difficulty: str = "medium"
) -> StudentSkill:
    record = await get_or_create_student_skill(db, user_id, skill_id)
    updated = _skill_agent.update_mastery(
        current={"mastery": record.mastery, "confidence": record.confidence, "attempts": record.attempts},
        evidence={"score_percent": score_percent, "difficulty": difficulty, "source": source},
    )
    record.mastery = updated["mastery"]
    record.confidence = updated["confidence"]
    record.level = updated["level"]
    record.attempts = updated["attempts"]
    record.last_assessed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(record)
    return record


async def get_student_skill_profile(db: AsyncSession, user_id: UUID) -> list[dict]:
    result = await db.execute(
        select(StudentSkill, Skill).join(Skill, Skill.id == StudentSkill.skill_id).where(StudentSkill.user_id == user_id)
    )
    out = []
    for student_skill, skill in result.all():
        out.append({
            "skill_slug": skill.slug, "skill_name": skill.name, "category": skill.category,
            "mastery": student_skill.mastery, "confidence": student_skill.confidence,
            "level": student_skill.level, "attempts": student_skill.attempts,
        })
    return out


async def get_all_skills_with_defaults(db: AsyncSession, user_id: UUID) -> list[dict]:
    """Every skill in the graph, defaulting to zero mastery if the student has no record yet."""
    skills_result = await db.execute(select(Skill))
    all_skills = skills_result.scalars().all()
    profile = {row["skill_slug"]: row for row in await get_student_skill_profile(db, user_id)}

    out = []
    for skill in all_skills:
        if skill.slug in profile:
            out.append(profile[skill.slug])
        else:
            out.append({
                "skill_slug": skill.slug, "skill_name": skill.name, "category": skill.category,
                "mastery": 0.0, "confidence": 0.0, "level": "beginner", "attempts": 0,
            })
    return out
