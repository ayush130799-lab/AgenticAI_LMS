from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import get_settings

settings = get_settings()

# default_limits only take effect because main.py installs SlowAPIMiddleware.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
    enabled=settings.rate_limit_enabled,
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """429 in the API's standard {"detail": ...} shape (slowapi's default body is {"error": ...})."""
    retry_after = 60
    try:
        retry_after = int(exc.limit.limit.get_expiry())
    except Exception:  # noqa: BLE001 - header is best-effort
        pass
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please wait a moment and try again."},
        headers={"Retry-After": str(retry_after)},
    )
