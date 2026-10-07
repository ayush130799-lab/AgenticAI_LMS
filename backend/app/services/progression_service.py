"""Module progression: the single source of truth for module state and access.

Nothing here is stored. A module's state is derived on demand from
  * lesson_progress (which lessons the student completed), and
  * passed module-assessment attempts,
so there is no second progress system to drift out of sync.

Rules
  * A module HAS A GATE only when it has a published module assessment
    (modules without one behave exactly as before - never locked, never gating).
  * The gate is passed by passing the assessment at the course's level, or any harder level.
  * Module N is LOCKED when any earlier module in the same course has a gate that is not passed, unless the
    student has already completed a lesson in it (progress from before gating existed is grandfathered).
    (Admins are never locked, so they can preview content.)
  * A module's assessment is AVAILABLE only when the module is unlocked and every lesson in it is completed.
  * A module is COMPLETED when all its lessons are completed and its gate (if any) is passed.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import Assessment, AssessmentAttempt
from app.models.curriculum import Course, Lesson, Module
from app.models.enrollment import LessonProgress
from app.models.user import User
from app.services.module_assessment_rules import LEVEL_RANK

LESSONS_INCOMPLETE_MESSAGE = "Complete all lessons in this module to unlock the assessment."


def _rank(level: str | None) -> int:
    return LEVEL_RANK.get(level or "beginner", 0)


def _gating_level(levels: list[str], course_level: str | None) -> str:
    """The level that gates the module: the course's level if configured, else the lowest configured."""
    if course_level in levels:
        return course_level  # type: ignore[return-value]
    return min(levels, key=_rank)


async def _compute(db: AsyncSession, user: User | None, course_ids: list[UUID] | None = None) -> dict[UUID, list[dict]]:
    course_query = select(Course.id, Course.level)
    if course_ids is not None:
        course_query = course_query.where(Course.id.in_(course_ids))
    courses = {row[0]: row[1] for row in (await db.execute(course_query)).all()}
    if not courses:
        return {}

    modules = (await db.execute(
        select(Module.id, Module.course_id, Module.title, Module.order_index)
        .where(Module.course_id.in_(list(courses))).order_by(Module.course_id, Module.order_index)
    )).all()
    module_ids = [m[0] for m in modules]

    lessons_by_module: dict[UUID, list[UUID]] = {}
    for lesson_id, module_id in (await db.execute(select(Lesson.id, Lesson.module_id).where(Lesson.module_id.in_(module_ids)))).all():
        lessons_by_module.setdefault(module_id, []).append(lesson_id)

    completed: set[UUID] = set()
    if user is not None:
        completed = {row[0] for row in (await db.execute(
            select(LessonProgress.lesson_id).where(LessonProgress.user_id == user.id, LessonProgress.status == "completed")
        )).all()}

    assessments_by_module: dict[UUID, list[Assessment]] = {}
    for a in (await db.execute(
        select(Assessment).where(
            Assessment.assessment_type == "module_quiz", Assessment.is_published.is_(True), Assessment.module_id.in_(module_ids)
        )
    )).scalars().all():
        assessments_by_module.setdefault(a.module_id, []).append(a)

    attempts_by_assessment: dict[UUID, list[AssessmentAttempt]] = {}
    if user is not None and assessments_by_module:
        assessment_ids = [a.id for group in assessments_by_module.values() for a in group]
        for attempt in (await db.execute(
            select(AssessmentAttempt).where(AssessmentAttempt.user_id == user.id, AssessmentAttempt.assessment_id.in_(assessment_ids))
        )).scalars().all():
            attempts_by_assessment.setdefault(attempt.assessment_id, []).append(attempt)

    is_admin = user is not None and user.role == "admin"
    states: dict[UUID, list[dict]] = {cid: [] for cid in courses}
    gate_open: dict[UUID, bool] = {cid: True for cid in courses}
    blocker_title: dict[UUID, str | None] = {cid: None for cid in courses}

    for module_id, course_id, title, order_index in modules:
        lesson_ids = lessons_by_module.get(module_id, [])
        lessons_done = sum(1 for lid in lesson_ids if lid in completed)
        all_done = lessons_done == len(lesson_ids)
        # Grandfathering: a module where the student already completed a lesson stays open (progress made before
        # gating existed is never taken away). Modules they have not started are gated as normal.
        locked = (not gate_open[course_id]) and not is_admin and lessons_done == 0
        locked_reason = f"Pass the assessment for “{blocker_title[course_id]}” to unlock this module." if locked else None

        module_assessments = assessments_by_module.get(module_id, [])
        assessment_state = None
        gate_passed = True
        if module_assessments:
            levels = sorted({a.level or "beginner" for a in module_assessments}, key=_rank)
            required_level = _gating_level(levels, courses[course_id])
            level_rows = []
            passed_levels: set[str] = set()
            in_progress_id = None
            total_attempts = 0
            best = None
            for a in sorted(module_assessments, key=lambda x: _rank(x.level)):
                attempts = attempts_by_assessment.get(a.id, [])
                graded = [t for t in attempts if t.status == "graded"]
                passed = any(t.passed for t in graded)
                open_attempt = next((t for t in attempts if t.status == "in_progress"), None)
                percentages = [t.percentage for t in graded if t.percentage is not None]
                if passed:
                    passed_levels.add(a.level or "beginner")
                if open_attempt and in_progress_id is None and (a.level or "beginner") == required_level:
                    in_progress_id = open_attempt.id
                total_attempts += len(graded)
                if percentages:
                    best = max(best or 0.0, max(percentages))
                level_rows.append({
                    "assessment_id": a.id, "level": a.level or "beginner", "title": a.title,
                    "required": (a.level or "beginner") == required_level, "passed": passed,
                    "attempts_count": len(graded), "best_percentage": max(percentages) if percentages else None,
                    "in_progress_attempt_id": open_attempt.id if open_attempt else None,
                })
            gate_passed = any(_rank(level) >= _rank(required_level) for level in passed_levels)

            if gate_passed:
                a_status, reason = "passed", None
            elif locked:
                a_status, reason = "locked", locked_reason
            elif not all_done:
                a_status, reason = "locked", LESSONS_INCOMPLETE_MESSAGE
            elif any(r["in_progress_attempt_id"] for r in level_rows):
                a_status, reason = "in_progress", None
            else:
                a_status, reason = "available", None
            assessment_state = {
                "configured": True, "status": a_status, "unavailable_reason": reason,
                "required_level": required_level, "passed": gate_passed, "attempts_count": total_attempts,
                "best_percentage": best, "levels": level_rows,
            }

        if locked:
            module_status = "locked"
        elif all_done and gate_passed:
            module_status = "completed"
        elif lessons_done > 0 or (assessment_state and assessment_state["status"] == "in_progress"):
            module_status = "in_progress"
        else:
            module_status = "available"

        states[course_id].append({
            "module_id": module_id, "course_id": course_id, "title": title, "order_index": order_index,
            "status": module_status, "locked": locked, "locked_reason": locked_reason,
            "lessons_total": len(lesson_ids), "lessons_completed": lessons_done, "all_lessons_completed": all_done,
            "has_assessment": assessment_state is not None, "assessment": assessment_state,
        })

        if assessment_state and not gate_passed:
            gate_open[course_id] = False
            blocker_title[course_id] = blocker_title[course_id] or title
    return states


async def get_course_states(db: AsyncSession, user: User | None, course_id: UUID) -> list[dict]:
    return (await _compute(db, user, [course_id])).get(course_id, [])


async def get_module_state(db: AsyncSession, user: User | None, module_id: UUID) -> dict:
    course_id = (await db.execute(select(Module.course_id).where(Module.id == module_id))).scalar_one_or_none()
    if course_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    for state in await get_course_states(db, user, course_id):
        if state["module_id"] == module_id:
            return state
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")


async def assert_module_accessible(db: AsyncSession, user: User | None, module_id: UUID) -> dict:
    """Raise 403 unless the student may access this module's content. Returns the module state."""
    state = await get_module_state(db, user, module_id)
    if state["locked"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=state["locked_reason"])
    return state


async def locked_module_ids(db: AsyncSession, user: User | None) -> set[UUID]:
    """Ids of every module the student cannot currently open (across all courses)."""
    all_states = await _compute(db, user)
    return {s["module_id"] for course_states in all_states.values() for s in course_states if s["locked"]}


async def get_assessment_and_state(db: AsyncSession, user: User, assessment_id: UUID) -> tuple[Assessment, dict]:
    """Load a published module assessment and its module state, or raise 404."""
    assessment = (await db.execute(select(Assessment).where(Assessment.id == assessment_id))).scalar_one_or_none()
    if assessment is None or assessment.assessment_type != "module_quiz" or not assessment.is_published or assessment.module_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return assessment, await get_module_state(db, user, assessment.module_id)


async def assert_assessment_available(db: AsyncSession, user: User, assessment_id: UUID) -> tuple[Assessment, dict]:
    """Raise 403 (with the reason) unless the student may take this assessment right now."""
    assessment, state = await get_assessment_and_state(db, user, assessment_id)
    if state["locked"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=state["locked_reason"])
    if not state["all_lessons_completed"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=LESSONS_INCOMPLETE_MESSAGE)
    return assessment, state
