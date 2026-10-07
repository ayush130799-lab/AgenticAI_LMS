"""Code-runner service: POST /run executes a student function against test cases in a sandbox.

Only reachable from the backend over an internal Docker network, authenticated with a shared token.
"""
from __future__ import annotations

import hmac
import os
import threading

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from sandbox import run_script, run_submission

TOKEN = os.environ.get("RUNNER_TOKEN", "")
MAX_CONCURRENT = int(os.environ.get("RUNNER_MAX_CONCURRENT", "4"))
_slots = threading.BoundedSemaphore(MAX_CONCURRENT)

app = FastAPI(title="AgenticAI code runner", docs_url=None, redoc_url=None, openapi_url=None)


class TestCase(BaseModel):
    id: str
    args: list = Field(max_length=16)
    expected: object = None
    visible: bool = False


class RunRequest(BaseModel):
    language: str = "python"
    code: str = Field(max_length=20_000)
    function_name: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$", max_length=64)
    tests: list[TestCase] = Field(min_length=1, max_length=20)
    time_limit_seconds: float = Field(default=2.0, gt=0, le=10)
    memory_limit_mb: int = Field(default=128, ge=32, le=512)


class RunScriptRequest(BaseModel):
    language: str = "python"
    code: str = Field(max_length=20_000)
    time_limit_seconds: float = Field(default=5.0, gt=0, le=10)
    memory_limit_mb: int = Field(default=128, ge=32, le=512)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/run")
def run(req: RunRequest, x_runner_token: str = Header(default="")) -> dict:
    if not TOKEN or not hmac.compare_digest(x_runner_token, TOKEN):
        raise HTTPException(status_code=401, detail="unauthorized")
    if req.language != "python":
        raise HTTPException(status_code=400, detail="unsupported language")
    if not _slots.acquire(timeout=15):
        raise HTTPException(status_code=503, detail="runner is busy")
    try:
        results = run_submission(
            req.code, req.function_name,
            [t.model_dump() for t in req.tests], req.time_limit_seconds, req.memory_limit_mb,
        )
    finally:
        _slots.release()
    return {"results": results}


@app.post("/run-script")
def run_script_endpoint(req: RunScriptRequest, x_runner_token: str = Header(default="")) -> dict:
    """Run open-ended code (no function/tests) and return its stdout/stderr - for practice exercises,
    which have no fixed answer to grade against."""
    if not TOKEN or not hmac.compare_digest(x_runner_token, TOKEN):
        raise HTTPException(status_code=401, detail="unauthorized")
    if req.language != "python":
        raise HTTPException(status_code=400, detail="unsupported language")
    if not _slots.acquire(timeout=15):
        raise HTTPException(status_code=503, detail="runner is busy")
    try:
        result = run_script(req.code, req.time_limit_seconds, req.memory_limit_mb)
    finally:
        _slots.release()
    return result
