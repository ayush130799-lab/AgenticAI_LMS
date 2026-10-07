import logging

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from app.models.audit import AdminAuditLog

logger = logging.getLogger("agentic_ai_lms.audit")


async def record_admin_action(db: AsyncSession, admin_id: UUID, admin_email: str, request: Request, status_code: int) -> None:
    """Persist one audit row for a state-changing admin request. Never raises: auditing must not break the request.

    Takes the admin's id/email as plain values: rollback() expires ORM instances, and touching an expired
    `User` from async code raises MissingGreenlet.
    """
    try:
        if status_code >= 400:
            await db.rollback()  # the request's own transaction may be dirty or aborted
        # /api/admin/<entity>[/<id>[/<action>]]
        parts = [p for p in request.url.path.split("/") if p]
        tail = parts[2:] if len(parts) > 2 and parts[1] == "admin" else parts
        entity = tail[0] if tail else "unknown"
        entity_id = tail[1] if len(tail) > 1 else None
        db.add(
            AdminAuditLog(
                user_id=admin_id,
                actor_email=admin_email,
                method=request.method,
                path=request.url.path[:500],
                entity=entity[:50],
                entity_id=entity_id[:64] if entity_id else None,
                status_code=status_code,
                client_ip=request.client.host if request.client else None,
            )
        )
        await db.commit()
        logger.info("admin_audit user=%s %s %s -> %s", admin_email, request.method, request.url.path, status_code)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to record admin audit entry for %s %s", request.method, request.url.path)
        await db.rollback()
