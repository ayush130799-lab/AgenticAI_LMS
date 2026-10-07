from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.curriculum import SkillOut
from app.schemas.learning import StudentSkillOut
from app.services import curriculum_service, progress_service, skill_service

router = APIRouter(tags=["skills"])


@router.get("/skills", response_model=list[SkillOut])
async def list_skills(db: AsyncSession = Depends(get_db)):
    return await curriculum_service.list_skills(db)


@router.get("/skills/graph")
async def get_skills_graph(db: AsyncSession = Depends(get_db)):
    """Return nodes and edges representing the curriculum skills dependency graph."""
    from app.models.curriculum import Skill, SkillPrerequisite
    from sqlalchemy import select

    skills_result = await db.execute(select(Skill))
    skills = skills_result.scalars().all()

    prereqs_result = await db.execute(select(SkillPrerequisite))
    prereqs = prereqs_result.scalars().all()

    nodes = [
        {
            "id": str(s.id),
            "slug": s.slug,
            "name": s.name,
            "category": s.category,
            "description": s.description or "",
        }
        for s in skills
    ]

    edges = [
        {
            "source": str(p.prerequisite_skill_id),
            "target": str(p.skill_id),
            "required_mastery": p.required_mastery,
        }
        for p in prereqs
    ]

    return {"nodes": nodes, "edges": edges}


@router.get("/students/me/skills", response_model=list[StudentSkillOut])
async def my_skills(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await skill_service.get_all_skills_with_defaults(db, user.id)


@router.get("/students/me/progress")
async def my_progress(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await progress_service.get_student_progress(db, user.id)
