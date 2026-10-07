from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import AIInteraction
from app.models.activity import Conversation, Message
from app.models.curriculum import Course, Lesson, Module
from app.services import skill_service

from ai_engine.agents.tutor import TutorAgent
from ai_engine.rag.retriever import retrieve_relevant_chunks

_tutor_agent = TutorAgent()


async def _build_lesson_context(db: AsyncSession, lesson_id: UUID | None) -> dict:
    if lesson_id is None:
        return {"course_title": None, "module_title": None, "lesson_title": None}
    result = await db.execute(
        select(Lesson, Module, Course)
        .join(Module, Module.id == Lesson.module_id)
        .join(Course, Course.id == Module.course_id)
        .where(Lesson.id == lesson_id)
    )
    row = result.first()
    if row is None:
        return {"course_title": None, "module_title": None, "lesson_title": None}
    lesson, module, course = row
    return {"course_title": course.title, "module_title": module.title, "lesson_title": lesson.title}


async def _student_level(db: AsyncSession, user_id: UUID) -> str:
    skills = await skill_service.get_student_skill_profile(db, user_id)
    attempted = [s for s in skills if s["attempts"] > 0]
    if not attempted:
        return "beginner"
    avg = sum(s["mastery"] for s in attempted) / len(attempted)
    if avg >= 0.9:
        return "expert"
    if avg >= 0.7:
        return "advanced"
    if avg >= 0.4:
        return "intermediate"
    return "beginner"


async def chat(db: AsyncSession, user_id: UUID, message: str, conversation_id: UUID | None, lesson_id: UUID | None) -> dict:
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .options(selectinload(Conversation.messages))
        )
        conversation = result.scalar_one_or_none()
        if conversation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        history = [{"role": m.role, "content": m.content} for m in conversation.messages]
    else:
        conversation = Conversation(user_id=user_id, agent_type="tutor", lesson_id=lesson_id, title=message[:80])
        db.add(conversation)
        await db.flush()
        history = []

    db.add(Message(conversation_id=conversation.id, role="user", content=message))
    await db.flush()

    chunks = await retrieve_relevant_chunks(db, query=message, lesson_id=str(lesson_id) if lesson_id else None, k=5)
    context = await _build_lesson_context(db, lesson_id)
    context["student_level"] = await _student_level(db, user_id)

    result = _tutor_agent.respond(question=message, context=context, history=history, retrieved_chunks=chunks)

    assistant_message = Message(
        conversation_id=conversation.id, role="assistant", content=result["reply"], citations=result["citations"]
    )
    db.add(assistant_message)
    db.add(AIInteraction(
        user_id=user_id, agent_type="tutor", input_summary=message[:200], output_summary=result["reply"][:200]
    ))
    await db.commit()

    return {"conversation_id": conversation.id, "reply": result["reply"], "citations": result["citations"]}


async def get_conversation(db: AsyncSession, user_id: UUID, conversation_id: UUID) -> Conversation:
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation
