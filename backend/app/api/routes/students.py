from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.content import Bookmark, Certificate
from app.models.curriculum import Lesson, Module
from app.models.user import User
from app.schemas.learning import OnboardingRequest
from app.services import dashboard_service, onboarding_service

router = APIRouter(prefix="/students/me", tags=["students"])


@router.post("/onboarding")
async def onboarding(payload: OnboardingRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    profile = await onboarding_service.complete_onboarding(db, user.id, payload)
    return {"ok": True, "onboarding_completed": profile.onboarding_completed}


@router.get("/profile")
async def get_profile(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    profile = await onboarding_service.get_profile(db, user.id)
    if profile is None:
        return {"onboarding_completed": False, "diagnostic_completed": False}

    # Fetch certificates for this user
    certs_result = await db.execute(
        select(Certificate).where(Certificate.user_id == user.id).order_by(Certificate.issued_at.desc())
    )
    certs = certs_result.scalars().all()
    certificates = [
        {
            "id": str(c.id),
            "certificate_number": c.certificate_number,
            "course_id": str(c.course_id),
            "issued_at": c.issued_at.isoformat() if c.issued_at else None,
        }
        for c in certs
    ]

    return {
        "onboarding_completed": profile.onboarding_completed,
        "diagnostic_completed": profile.diagnostic_completed,
        "career_goal": profile.career_goal,
        "target_role": profile.target_role,
        "preferred_pace": profile.preferred_pace,
        "available_hours_per_week": profile.available_hours_per_week,
        "current_streak_days": profile.current_streak_days,
        "longest_streak_days": profile.longest_streak_days,
        "streak_days": profile.current_streak_days,  # alias for frontend compatibility
        "bio": profile.bio,
        "certificates": certificates,
    }


@router.get("/activity")
async def recent_activity(limit: int = 8, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await dashboard_service.get_recent_activity(db, user.id, min(max(limit, 1), 30))


@router.get("/bookmarks")
async def list_bookmarks(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Return all lessons the student has bookmarked, newest first."""
    result = await db.execute(
        select(Bookmark, Lesson, Module.course_id)
        .join(Lesson, Lesson.id == Bookmark.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .where(Bookmark.user_id == user.id)
        .order_by(Bookmark.created_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": str(bm.id),
            "lesson_id": str(lesson.id),
            "lesson_title": lesson.title,
            "lesson_type": lesson.lesson_type,
            "course_id": str(course_id),
            "created_at": bm.created_at.isoformat() if bm.created_at else None,
        }
        for bm, lesson, course_id in rows
    ]


@router.get("/certificates")
async def list_certificates(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Return all certificates issued to the student."""
    from app.models.curriculum import Course
    result = await db.execute(
        select(Certificate, Course)
        .join(Course, Course.id == Certificate.course_id)
        .where(Certificate.user_id == user.id)
        .order_by(Certificate.issued_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": str(cert.id),
            "certificate_number": cert.certificate_number,
            "course_id": str(cert.course_id),
            "course_title": course.title,
            "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
        }
        for cert, course in rows
    ]
