"""Run a lesson's open-ended practice code in the sandbox.

Unlike module-assessment coding questions, a practice exercise has no fixed function
signature or expected value to grade against - it's a "does this run" scratchpad, so
this just executes the student's script and returns what it printed. Nothing is scored,
persisted, or fed into progression/gating; the module-accessibility check below only
guards against running code for content the student hasn't unlocked yet (same rule as
viewing/completing the lesson).
"""
from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services import curriculum_service, progression_service
from app.services.code_execution import CodeExecutionUnavailable, CodeRunner

TIME_LIMIT_SECONDS = 5.0
MEMORY_LIMIT_MB = 128


async def run_practice_code(db: AsyncSession, user: User, lesson_id: UUID, code: str, runner: CodeRunner) -> dict:
    lesson = await curriculum_service.get_lesson_detail(db, lesson_id, user)
    await progression_service.assert_module_accessible(db, user, lesson["module_id"])

    if not code.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Write some code before running it.")

    try:
        result = await runner.run_script(language="python", code=code, time_limit=TIME_LIMIT_SECONDS, memory_mb=MEMORY_LIMIT_MB)
    except CodeExecutionUnavailable as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    return {
        "status": result.get("status", "error"),
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "error": result.get("error"),
        "duration_ms": result.get("duration_ms", 0),
    }
