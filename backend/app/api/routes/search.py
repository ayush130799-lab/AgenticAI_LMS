from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_optional_user
from app.db.session import get_db
from app.models.curriculum import Course, Lesson, Module, Skill
from app.models.user import User

router = APIRouter(tags=["search"])


@router.get("/search")
async def global_search(
    q: str = Query(min_length=2, max_length=200),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    """
    Full-text search across courses, lessons, and skills.
    Returns up to 5 results per category.
    """
    term = f"%{q.lower()}%"

    courses_result = await db.execute(
        select(Course.id, Course.slug, Course.title, Course.subtitle, Course.level)
        .where(or_(Course.title.ilike(term), Course.subtitle.ilike(term), Course.description.ilike(term)))
        .order_by(Course.order_index)
        .limit(5)
    )
    courses = [
        {"type": "course", "id": str(r.id), "slug": r.slug, "title": r.title,
         "subtitle": r.subtitle or "", "badge": r.level, "href": f"/courses/{r.id}"}
        for r in courses_result.all()
    ]

    # Join lessons with modules to get course_id for links
    lessons_result = await db.execute(
        select(Lesson.id, Lesson.slug, Lesson.title, Lesson.description, Lesson.lesson_type, Module.course_id)
        .join(Module, Module.id == Lesson.module_id)
        .where(or_(Lesson.title.ilike(term), Lesson.description.ilike(term)))
        .order_by(Lesson.order_index)
        .limit(5)
    )
    lessons = [
        {"type": "lesson", "id": str(r.id), "slug": r.slug, "title": r.title,
         "subtitle": r.description, "badge": r.lesson_type, "href": f"/lessons/{r.id}"}
        for r in lessons_result.all()
    ]

    skills_result = await db.execute(
        select(Skill.id, Skill.slug, Skill.name, Skill.description, Skill.category)
        .where(or_(Skill.name.ilike(term), Skill.description.ilike(term)))
        .limit(5)
    )
    skills = [
        {"type": "skill", "id": str(r.id), "slug": r.slug, "title": r.name,
         "subtitle": r.description or "", "badge": r.category, "href": "/skills"}
        for r in skills_result.all()
    ]

    return {"results": courses + lessons + skills, "query": q}
