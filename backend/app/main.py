import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.config import get_settings
from app.core.rate_limit import limiter, rate_limit_exceeded_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agentic_ai_lms")

settings = get_settings()

app = FastAPI(title="Agentic AI LMS API", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Added BEFORE CORS so CORS ends up outermost: a 429 must still carry CORS headers, otherwise the browser
# reports it as a network error instead of showing the "too many requests" message.
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Only loc/msg/type: `ctx` can hold exception objects (not JSON-serialisable -> the handler itself would 500)
    # and `input` echoes back whatever the client sent, including rejected passwords.
    errors = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": "Invalid request data", "errors": errors})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    headers = {}
    # This handler runs outside CORSMiddleware; without the header the browser reports a 500 as a network/CORS failure.
    origin = request.headers.get("origin")
    if origin and origin in settings.cors_origin_list:
        headers = {"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Credentials": "true", "Vary": "Origin"}
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"}, headers=headers
    )


@app.get("/api/health")
@limiter.exempt
async def health():
    return {"status": "ok"}


app.include_router(api_router)
