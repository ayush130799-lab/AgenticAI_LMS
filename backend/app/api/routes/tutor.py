from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.activity import Conversation
from app.models.user import User
from app.schemas.project import TutorChatRequest, TutorChatResponse
from app.services import tutor_service

router = APIRouter(prefix="/tutor", tags=["tutor"])


@router.post("/chat", response_model=TutorChatResponse)
async def chat(payload: TutorChatRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await tutor_service.chat(db, user.id, payload.message, payload.conversation_id, payload.lesson_id)


@router.get("/conversations")
async def list_conversations(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Return a summary list of past tutor conversations for the sidebar."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id, Conversation.agent_type == "tutor")
        .order_by(Conversation.updated_at.desc())
    )
    convs = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "title": c.title or "Untitled conversation",
            "lesson_id": str(c.lesson_id) if c.lesson_id else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }
        for c in convs
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    conversation = await tutor_service.get_conversation(db, user.id, conversation_id)
    return {
        "id": conversation.id,
        "messages": [
            {"role": m.role, "content": m.content, "citations": m.citations, "created_at": m.created_at}
            for m in conversation.messages
        ],
    }
