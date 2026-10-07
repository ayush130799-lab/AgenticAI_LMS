from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Bookmark, Highlight, Note
from app.models.curriculum import Lesson
from app.models.user import User
from app.services import progression_service


async def ensure_lesson_accessible(db: AsyncSession, user: User, lesson_id: UUID) -> None:
    """404 if the lesson does not exist, 403 if its module is locked for this student (same rule as viewing it)."""
    module_id = (await db.execute(select(Lesson.module_id).where(Lesson.id == lesson_id))).scalar_one_or_none()
    if module_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    await progression_service.assert_module_accessible(db, user, module_id)


async def list_notes(db: AsyncSession, user_id: UUID, lesson_id: UUID) -> list[Note]:
    result = await db.execute(select(Note).where(Note.user_id == user_id, Note.lesson_id == lesson_id).order_by(Note.created_at))
    return result.scalars().all()


async def add_note(db: AsyncSession, user_id: UUID, lesson_id: UUID, content: str) -> Note:
    note = Note(user_id=user_id, lesson_id=lesson_id, content=content)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def toggle_bookmark(db: AsyncSession, user_id: UUID, lesson_id: UUID) -> bool:
    """Flip the bookmark and return the new state. Safe under concurrent requests.

    Removal is a single DELETE ... RETURNING (no read-then-write gap), and creation relies on the
    (user_id, lesson_id) unique constraint: if a concurrent request inserted first we lose the race,
    the row exists, and "bookmarked" is the truthful answer.
    """
    removed = await db.execute(
        delete(Bookmark).where(Bookmark.user_id == user_id, Bookmark.lesson_id == lesson_id).returning(Bookmark.id)
    )
    if removed.first() is not None:
        await db.commit()
        return False
    try:
        db.add(Bookmark(user_id=user_id, lesson_id=lesson_id))
        await db.commit()
    except IntegrityError:
        await db.rollback()
    return True


async def add_highlight(db: AsyncSession, user_id: UUID, lesson_id: UUID, text: str, color: str) -> Highlight:
    highlight = Highlight(user_id=user_id, lesson_id=lesson_id, text=text, color=color)
    db.add(highlight)
    await db.commit()
    await db.refresh(highlight)
    return highlight
