from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import ActivityLog
from app.models.assessment import Assessment, AssessmentAttempt
from app.models.curriculum import Course, Lesson, Module
from app.models.enrollment import Enrollment, LessonProgress
from app.models.project import Project, ProjectSubmission
from app.models.user import StudentProfile, User
from app.services import planner_service, progress_service, progression_service, skill_service


async def get_dashboard(db: AsyncSession, user: User) -> dict:
    profile_result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()

    progress = await progress_service.get_student_progress(db, user.id)
    all_skills = await skill_service.get_all_skills_with_defaults(db, user.id)
    overall_mastery = round(sum(s["mastery"] for s in all_skills) / len(all_skills) * 100, 1) if all_skills else 0.0
    weak_skills = sorted([s for s in all_skills if s["attempts"] > 0], key=lambda s: s["mastery"])[:5]

    # current course = most recently active enrollment
    enrollment_result = await db.execute(
        select(Enrollment, Course).join(Course, Course.id == Enrollment.course_id)
        .where(Enrollment.user_id == user.id, Enrollment.is_active.is_(True))
        .order_by(Enrollment.updated_at.desc())
    )
    enrollment_row = enrollment_result.first()
    current_course = None
    continue_lesson = None
    pending_module_assessment = None
    if enrollment_row:
        enrollment, course = enrollment_row
        current_course = {"id": str(course.id), "title": course.title, "slug": course.slug, "progress_percent": enrollment.progress_percent}

        lessons_result = await db.execute(
            select(Lesson).join(Module, Module.id == Lesson.module_id).where(Module.course_id == course.id).order_by(Module.order_index, Lesson.order_index)
        )
        lessons = lessons_result.scalars().all()
        completed_result = await db.execute(
            select(LessonProgress.lesson_id).where(LessonProgress.user_id == user.id, LessonProgress.status == "completed")
        )
        completed_ids = {row[0] for row in completed_result.all()}
        # Never point the student at a module they cannot open yet.
        states = await progression_service.get_course_states(db, user, course.id)
        locked_ids = {st["module_id"] for st in states if st["locked"]}
        next_lesson = next((l for l in lessons if l.id not in completed_ids and l.module_id not in locked_ids), None)
        pending = next((st for st in states if st["assessment"] and st["assessment"]["status"] in ("available", "in_progress")), None)
        if pending:
            required = next((lv for lv in pending["assessment"]["levels"] if lv["required"]), pending["assessment"]["levels"][0])
            pending_module_assessment = {
                "assessment_id": str(required["assessment_id"]), "module_id": str(pending["module_id"]),
                "module_title": pending["title"], "level": required["level"], "status": pending["assessment"]["status"],
            }
        if next_lesson:
            continue_lesson = {"id": str(next_lesson.id), "title": next_lesson.title, "course_title": course.title}

    recent_attempt_result = await db.execute(
        select(AssessmentAttempt, Assessment).join(Assessment, Assessment.id == AssessmentAttempt.assessment_id)
        .where(AssessmentAttempt.user_id == user.id, AssessmentAttempt.status == "graded")
        .order_by(AssessmentAttempt.submitted_at.desc())
    )
    recent_row = recent_attempt_result.first()
    recent_assessment = None
    if recent_row:
        attempt, assessment = recent_row
        recent_assessment = {
            "attempt_id": str(attempt.id), "assessment_id": str(assessment.id), "title": assessment.title,
            "assessment_type": assessment.assessment_type,
            "score_percent": round((attempt.score or 0) * 100, 1),
            "passed": (attempt.score or 0) >= assessment.passing_score,
            "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
        }

    upcoming_assessment = await _next_assessment(db, user.id, profile, current_course)

    submissions_result = await db.execute(
        select(ProjectSubmission, Project).join(Project, Project.id == ProjectSubmission.project_id)
        .where(ProjectSubmission.user_id == user.id)
    )
    active_projects = [
        {"id": str(p.id), "title": p.title, "status": sub.status, "score": sub.score}
        for sub, p in submissions_result.all()
    ]

    recommendations = await planner_service.list_recommendations(db, user.id)

    return {
        "full_name": user.full_name,
        "curriculum_progress_percent": progress["curriculum_progress_percent"],
        "overall_skill_mastery_percent": overall_mastery,
        "current_course": current_course,
        "continue_lesson": continue_lesson,
        "pending_module_assessment": pending_module_assessment,
        "skills": all_skills,
        "weak_skills": weak_skills,
        "recent_assessment": recent_assessment,
        "upcoming_assessment": upcoming_assessment,
        "active_projects": active_projects,
        "learning_streak_days": profile.current_streak_days if profile else 0,
        "recommendations": recommendations,
    }


async def _next_assessment(db: AsyncSession, user_id: UUID, profile: StudentProfile | None, current_course: dict | None) -> dict | None:
    """The diagnostic if not yet taken, otherwise the current course's exam if not yet passed."""
    graded = await db.execute(
        select(AssessmentAttempt.assessment_id, AssessmentAttempt.score)
        .where(AssessmentAttempt.user_id == user_id, AssessmentAttempt.status == "graded")
    )
    best: dict[UUID, float] = {}
    for assessment_id, score in graded.all():
        best[assessment_id] = max(best.get(assessment_id, 0.0), score or 0.0)

    if profile is None or not profile.diagnostic_completed:
        diagnostic = (await db.execute(select(Assessment).where(Assessment.assessment_type == "diagnostic"))).scalars().first()
        if diagnostic:
            return {"assessment_id": str(diagnostic.id), "title": diagnostic.title, "assessment_type": "diagnostic"}

    if current_course:
        exam = (await db.execute(
            select(Assessment).where(Assessment.course_id == UUID(current_course["id"]), Assessment.assessment_type == "course_exam")
        )).scalars().first()
        if exam and best.get(exam.id, -1.0) < exam.passing_score:
            return {"assessment_id": str(exam.id), "title": exam.title, "assessment_type": "course_exam"}
    return None


async def get_recent_activity(db: AsyncSession, user_id: UUID, limit: int = 8) -> list[dict]:
    result = await db.execute(
        select(ActivityLog).where(ActivityLog.user_id == user_id).order_by(ActivityLog.created_at.desc()).limit(limit)
    )
    return [
        {
            "id": str(row.id), "action": row.action, "entity_type": row.entity_type,
            "entity_id": str(row.entity_id) if row.entity_id else None,
            "title": (row.metadata_json or {}).get("title"),
            "score_percent": (row.metadata_json or {}).get("score_percent"),
            "created_at": row.created_at.isoformat(),
        }
        for row in result.scalars().all()
    ]
