from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content import Bookmark
from app.models.curriculum import Course, Lesson, LessonSkill, Module, Skill
from app.models.enrollment import Enrollment, LessonProgress
from app.models.user import User
from app.services import progression_service


async def _lesson_counts_by_course(db: AsyncSession) -> dict[UUID, int]:
    result = await db.execute(
        select(Module.course_id, func.count(Lesson.id)).join(Lesson, Lesson.module_id == Module.id).group_by(Module.course_id)
    )
    return {row[0]: row[1] for row in result.all()}


async def _completed_counts_by_course(db: AsyncSession, user_id: UUID) -> dict[UUID, int]:
    result = await db.execute(
        select(Module.course_id, func.count(LessonProgress.id))
        .join(Lesson, Lesson.module_id == Module.id)
        .join(LessonProgress, (LessonProgress.lesson_id == Lesson.id) & (LessonProgress.user_id == user_id) & (LessonProgress.status == "completed"))
        .group_by(Module.course_id)
    )
    return {row[0]: row[1] for row in result.all()}


async def list_courses(db: AsyncSession, user: User | None) -> list[dict]:
    result = await db.execute(select(Course).where(Course.is_published.is_(True)).order_by(Course.order_index))
    courses = result.scalars().all()

    lesson_counts = await _lesson_counts_by_course(db)
    completed_counts = await _completed_counts_by_course(db, user.id) if user else {}

    module_counts_result = await db.execute(select(Module.course_id, func.count(Module.id)).group_by(Module.course_id))
    module_counts = {row[0]: row[1] for row in module_counts_result.all()}

    out = []
    for c in courses:
        total = lesson_counts.get(c.id, 0)
        done = completed_counts.get(c.id, 0)
        out.append({
            "id": c.id, "slug": c.slug, "title": c.title, "subtitle": c.subtitle,
            "description": c.description, "order_index": c.order_index, "estimated_hours": c.estimated_hours,
            "level": c.level, "icon": c.icon,
            "module_count": module_counts.get(c.id, 0), "lesson_count": total,
            "progress_percent": round(100 * done / total, 1) if user and total else (0.0 if user else None),
        })
    return out


async def get_course_detail(db: AsyncSession, course_id: UUID, user: User | None) -> dict:
    result = await db.execute(
        select(Course).where(Course.id == course_id).options(selectinload(Course.modules).selectinload(Module.lessons))
    )
    course = result.scalar_one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    progress_by_lesson: dict[UUID, str] = {}
    if user:
        lesson_ids = [l.id for m in course.modules for l in m.lessons]
        if lesson_ids:
            prog = await db.execute(
                select(LessonProgress.lesson_id, LessonProgress.status).where(
                    LessonProgress.user_id == user.id, LessonProgress.lesson_id.in_(lesson_ids)
                )
            )
            progress_by_lesson = {row[0]: row[1] for row in prog.all()}

    module_states = {st["module_id"]: st for st in await progression_service.get_course_states(db, user, course_id)}
    modules_out = []
    total_lessons = 0
    completed_lessons = 0
    for m in sorted(course.modules, key=lambda x: x.order_index):
        lessons_out = []
        module_completed = 0
        for l in sorted(m.lessons, key=lambda x: x.order_index):
            total_lessons += 1
            status_ = progress_by_lesson.get(l.id, "not_started")
            if status_ == "completed":
                completed_lessons += 1
                module_completed += 1
            lessons_out.append({
                "id": l.id, "slug": l.slug, "title": l.title, "description": l.description,
                "lesson_type": l.lesson_type, "order_index": l.order_index, "estimated_minutes": l.estimated_minutes,
                "progress_status": status_ if user else None,
            })
        modules_out.append({
            "id": m.id, "slug": m.slug, "title": m.title, "description": m.description,
            "order_index": m.order_index, "estimated_hours": m.estimated_hours,
            "lesson_count": len(lessons_out), "completed_lesson_count": module_completed,
            "lessons": lessons_out,
            **_progression_fields(module_states.get(m.id)),
        })

    return {
        "id": course.id, "slug": course.slug, "title": course.title, "subtitle": course.subtitle,
        "description": course.description, "order_index": course.order_index, "estimated_hours": course.estimated_hours,
        "level": course.level, "icon": course.icon, "learning_outcomes": course.learning_outcomes,
        "module_count": len(modules_out), "lesson_count": total_lessons,
        "progress_percent": round(100 * completed_lessons / total_lessons, 1) if user and total_lessons else (0.0 if user else None),
        "modules_completed": sum(1 for m in modules_out if m.get("status") == "completed"),
        "modules": modules_out,
    }


def _progression_fields(state: dict | None) -> dict:
    if state is None:
        return {}
    assessment = state["assessment"] or {}
    return {
        "status": state["status"], "locked": state["locked"], "locked_reason": state["locked_reason"],
        "all_lessons_completed": state["all_lessons_completed"], "has_assessment": state["has_assessment"],
        "assessment_status": assessment.get("status"), "assessment_unavailable_reason": assessment.get("unavailable_reason"),
        "assessment_best_percentage": assessment.get("best_percentage"),
    }


async def get_lesson_detail(db: AsyncSession, lesson_id: UUID, user: User | None) -> dict:
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id).options(selectinload(Lesson.skills).selectinload(LessonSkill.skill))
    )
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    progress_status = None
    is_bookmarked = False
    if user:
        prog = await db.execute(
            select(LessonProgress.status).where(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson_id)
        )
        row = prog.scalar_one_or_none()
        progress_status = row or "not_started"
        bm = await db.execute(
            select(Bookmark.id).where(Bookmark.user_id == user.id, Bookmark.lesson_id == lesson_id)
        )
        is_bookmarked = bm.scalar_one_or_none() is not None

    course_id = (await db.execute(select(Module.course_id).where(Module.id == lesson.module_id))).scalar_one()

    return {
        "id": lesson.id, "slug": lesson.slug, "title": lesson.title, "description": lesson.description,
        "lesson_type": lesson.lesson_type, "order_index": lesson.order_index, "estimated_minutes": lesson.estimated_minutes,
        "learning_objectives": lesson.learning_objectives, "content_markdown": lesson.content_markdown,
        "examples": lesson.examples, "practice_exercises": lesson.practice_exercises, "resources": lesson.resources,
        "module_id": lesson.module_id, "course_id": course_id, "progress_status": progress_status,
        "is_bookmarked": is_bookmarked,
        "skills": [
            {"id": ls.skill.id, "slug": ls.skill.slug, "name": ls.skill.name, "description": ls.skill.description,
             "category": ls.skill.category, "parent_skill_id": ls.skill.parent_skill_id}
            for ls in lesson.skills
        ],
    }


async def list_skills(db: AsyncSession) -> list[Skill]:
    result = await db.execute(select(Skill))
    return result.scalars().all()


async def ensure_enrollment(db: AsyncSession, user_id: UUID, course_id: UUID) -> None:
    existing = await db.execute(select(Enrollment).where(Enrollment.user_id == user_id, Enrollment.course_id == course_id))
    if existing.scalar_one_or_none() is None:
        db.add(Enrollment(user_id=user_id, course_id=course_id))
        await db.commit()
