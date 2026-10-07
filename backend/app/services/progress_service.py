from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import ActivityLog
from app.models.content import Certificate
from app.models.curriculum import Course, Lesson, Module
from app.models.enrollment import Enrollment, LessonProgress
from app.models.user import StudentProfile


async def _bump_streak(db: AsyncSession, user_id: UUID) -> None:
    result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        return

    today = date.today().isoformat()
    if profile.last_activity_date == today:
        return

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    if profile.last_activity_date == yesterday:
        profile.current_streak_days += 1
    else:
        profile.current_streak_days = 1

    profile.longest_streak_days = max(profile.longest_streak_days, profile.current_streak_days)
    profile.last_activity_date = today
    await db.commit()


async def mark_lesson_complete(db: AsyncSession, user_id: UUID, lesson_id: UUID) -> str:
    lesson_result = await db.execute(
        select(Lesson, Module.course_id).join(Module, Module.id == Lesson.module_id).where(Lesson.id == lesson_id)
    )
    row = lesson_result.first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    lesson, course_id = row

    existing = await db.execute(select(Enrollment).where(Enrollment.user_id == user_id, Enrollment.course_id == course_id))
    if existing.scalar_one_or_none() is None:
        db.add(Enrollment(user_id=user_id, course_id=course_id))

    progress_result = await db.execute(
        select(LessonProgress).where(LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson_id)
    )
    progress = progress_result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if progress is None:
        progress = LessonProgress(user_id=user_id, lesson_id=lesson_id, status="completed", completed_at=now)
        db.add(progress)
    else:
        progress.status = "completed"
        progress.completed_at = now

    db.add(ActivityLog(user_id=user_id, action="lesson_completed", entity_type="lesson", entity_id=lesson_id, metadata_json={"title": lesson.title}))
    await db.commit()
    await _bump_streak(db, user_id)
    # Auto-issue certificate if the student has now completed every lesson in the course
    await _maybe_issue_certificate(db, user_id, course_id)
    return "completed"


async def _maybe_issue_certificate(db: AsyncSession, user_id: UUID, course_id: UUID) -> None:
    """Issue a certificate when the student finishes every lesson in a course (idempotent)."""
    # Check if already issued
    existing = await db.execute(
        select(Certificate.id).where(Certificate.user_id == user_id, Certificate.course_id == course_id)
    )
    if existing.scalar_one_or_none() is not None:
        return

    # Count total lessons vs completed lessons for this course
    total = (await db.execute(
        select(func.count(Lesson.id)).join(Module, Module.id == Lesson.module_id).where(Module.course_id == course_id)
    )).scalar_one()
    if total == 0:
        return
    done = (await db.execute(
        select(func.count(LessonProgress.id))
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .where(Module.course_id == course_id, LessonProgress.user_id == user_id, LessonProgress.status == "completed")
    )).scalar_one()

    if done < total:
        return

    # All lessons done — mint the certificate
    cert_num = f"CERT-{str(user_id)[:8].upper()}-{str(course_id)[:8].upper()}"
    cert = Certificate(
        user_id=user_id,
        course_id=course_id,
        certificate_number=cert_num,
        issued_at=datetime.now(timezone.utc),
    )
    db.add(cert)
    db.add(ActivityLog(
        user_id=user_id, action="certificate_issued", entity_type="course", entity_id=course_id,
        metadata_json={"certificate_number": cert_num}
    ))
    await db.commit()


async def get_student_progress(db: AsyncSession, user_id: UUID) -> dict:
    total_result = await db.execute(select(Lesson.id))
    total_lessons = len(total_result.all())

    completed_result = await db.execute(
        select(LessonProgress.id).where(LessonProgress.user_id == user_id, LessonProgress.status == "completed")
    )
    completed_lessons = len(completed_result.all())

    courses_result = await db.execute(select(Course).order_by(Course.order_index))
    courses = courses_result.scalars().all()

    course_progress = []
    for c in courses:
        lessons_result = await db.execute(select(Lesson.id).join(Module, Module.id == Lesson.module_id).where(Module.course_id == c.id))
        lesson_ids = [r[0] for r in lessons_result.all()]
        if not lesson_ids:
            course_progress.append({"course_id": c.id, "title": c.title, "progress_percent": 0.0})
            continue
        done_result = await db.execute(
            select(LessonProgress.id).where(
                LessonProgress.user_id == user_id, LessonProgress.lesson_id.in_(lesson_ids), LessonProgress.status == "completed"
            )
        )
        done = len(done_result.all())
        course_progress.append({"course_id": c.id, "title": c.title, "progress_percent": round(100 * done / len(lesson_ids), 1)})

    return {
        "curriculum_progress_percent": round(100 * completed_lessons / total_lessons, 1) if total_lessons else 0.0,
        "courses": course_progress,
    }
