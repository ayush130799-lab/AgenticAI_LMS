from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.curriculum import (
    BookmarkOut,
    HighlightCreate,
    HighlightOut,
    LessonDetailOut,
    NoteCreate,
    NoteOut,
    PracticeRunOut,
    PracticeRunRequest,
)
from app.services import content_service, curriculum_service, practice_service, progress_service, progression_service
from app.services.code_execution import CodeRunner, get_code_runner

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/{lesson_id}", response_model=LessonDetailOut)
async def get_lesson(lesson_id: UUID, db: AsyncSession = Depends(get_db), user: User | None = Depends(get_optional_user)):
    lesson = await curriculum_service.get_lesson_detail(db, lesson_id, user)
    await progression_service.assert_module_accessible(db, user, lesson["module_id"])
    return lesson


@router.post("/{lesson_id}/complete", response_model=LessonDetailOut)
async def complete_lesson(lesson_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    lesson = await curriculum_service.get_lesson_detail(db, lesson_id, user)
    await progression_service.assert_module_accessible(db, user, lesson["module_id"])
    await progress_service.mark_lesson_complete(db, user.id, lesson_id)
    return await curriculum_service.get_lesson_detail(db, lesson_id, user)


@router.post("/{lesson_id}/practice/run", response_model=PracticeRunOut)
async def run_practice_code(
    lesson_id: UUID, payload: PracticeRunRequest, db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user), runner: CodeRunner = Depends(get_code_runner),
):
    return await practice_service.run_practice_code(db, user, lesson_id, payload.code, runner)


@router.get("/{lesson_id}/notes", response_model=list[NoteOut])
async def get_notes(lesson_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await content_service.list_notes(db, user.id, lesson_id)


@router.post("/{lesson_id}/notes", response_model=NoteOut)
async def create_note(lesson_id: UUID, payload: NoteCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await content_service.ensure_lesson_accessible(db, user, lesson_id)
    return await content_service.add_note(db, user.id, lesson_id, payload.content)


@router.post("/{lesson_id}/bookmark", response_model=BookmarkOut)
async def bookmark_lesson(lesson_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await content_service.ensure_lesson_accessible(db, user, lesson_id)
    return {"bookmarked": await content_service.toggle_bookmark(db, user.id, lesson_id)}


@router.post("/{lesson_id}/highlights", response_model=HighlightOut)
async def highlight_lesson(lesson_id: UUID, payload: HighlightCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await content_service.ensure_lesson_accessible(db, user, lesson_id)
    return await content_service.add_highlight(db, user.id, lesson_id, payload.text, payload.color)
