from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import StudentProfile
from app.schemas.learning import OnboardingRequest


async def complete_onboarding(db: AsyncSession, user_id: UUID, payload: OnboardingRequest) -> StudentProfile:
    result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = StudentProfile(user_id=user_id)
        db.add(profile)

    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    profile.onboarding_completed = True

    await db.commit()
    await db.refresh(profile)
    return profile


async def get_profile(db: AsyncSession, user_id: UUID) -> StudentProfile | None:
    result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == user_id))
    return result.scalar_one_or_none()
