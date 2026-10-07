from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.curriculum import CourseDetailOut, CourseSummaryOut, ModuleDetailOut
from app.services import curriculum_service

router = APIRouter(tags=["courses"])


@router.get("/courses", response_model=list[CourseSummaryOut])
async def list_courses(db: AsyncSession = Depends(get_db), user: User | None = Depends(get_optional_user)):
    return await curriculum_service.list_courses(db, user)


@router.get("/courses/{course_id}", response_model=CourseDetailOut)
async def get_course(course_id: UUID, db: AsyncSession = Depends(get_db), user: User | None = Depends(get_optional_user)):
    return await curriculum_service.get_course_detail(db, course_id, user)


@router.get("/courses/{course_id}/modules", response_model=list[ModuleDetailOut])
async def get_course_modules(course_id: UUID, db: AsyncSession = Depends(get_db), user: User | None = Depends(get_optional_user)):
    detail = await curriculum_service.get_course_detail(db, course_id, user)
    return detail["modules"]
