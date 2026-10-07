"""Code execution provider abstraction.

The backend NEVER runs student code in its own process. It talks to a `CodeRunner`;
the production implementation calls the isolated `code_runner` service (separate
container: no network, read-only filesystem, resource limits). If no runner is
configured the provider raises `CodeExecutionUnavailable` and the caller fails the
submission safely (HTTP 503, attempt stays open) rather than running anything locally.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache

import httpx

from app.core.config import get_settings


class CodeExecutionUnavailable(RuntimeError):
    """The sandbox is not configured or could not be reached."""


class CodeRunner(ABC):
    @abstractmethod
    async def run(
        self, *, language: str, code: str, function_name: str, tests: list[dict], time_limit: float, memory_mb: int
    ) -> list[dict]:
        """Run `code` against `tests` ({id, args, expected, visible}); one result dict per test, same order."""

    @abstractmethod
    async def run_script(self, *, language: str, code: str, time_limit: float, memory_mb: int) -> dict:
        """Run `code` as a plain script (no function call, nothing to grade) and return its stdout/stderr.

        For open-ended practice exercises: {status: ok|error|timeout, stdout, stderr, error, duration_ms}.
        """


class UnavailableCodeRunner(CodeRunner):
    async def run(self, **_: object) -> list[dict]:
        raise CodeExecutionUnavailable("Code execution is not configured on this server.")

    async def run_script(self, **_: object) -> dict:
        raise CodeExecutionUnavailable("Code execution is not configured on this server.")


class RemoteCodeRunner(CodeRunner):
    def __init__(self, url: str, token: str) -> None:
        self._url = url.rstrip("/")
        self._token = token

    async def run(
        self, *, language: str, code: str, function_name: str, tests: list[dict], time_limit: float, memory_mb: int
    ) -> list[dict]:
        payload = {
            "language": language, "code": code, "function_name": function_name, "tests": tests,
            "time_limit_seconds": time_limit, "memory_limit_mb": memory_mb,
        }
        # Every test may take the full limit (plus process start-up), so budget for all of them.
        timeout = httpx.Timeout(len(tests) * (time_limit + 1.5) + 10.0, connect=5.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(f"{self._url}/run", json=payload, headers={"X-Runner-Token": self._token})
        except httpx.HTTPError as exc:
            raise CodeExecutionUnavailable("The code execution service could not be reached.") from exc
        if response.status_code != 200:
            raise CodeExecutionUnavailable(f"The code execution service returned HTTP {response.status_code}.")
        results = response.json().get("results")
        if not isinstance(results, list) or len(results) != len(tests):
            raise CodeExecutionUnavailable("The code execution service returned an unexpected response.")
        return results

    async def run_script(self, *, language: str, code: str, time_limit: float, memory_mb: int) -> dict:
        payload = {"language": language, "code": code, "time_limit_seconds": time_limit, "memory_limit_mb": memory_mb}
        timeout = httpx.Timeout(time_limit + 10.0, connect=5.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(f"{self._url}/run-script", json=payload, headers={"X-Runner-Token": self._token})
        except httpx.HTTPError as exc:
            raise CodeExecutionUnavailable("The code execution service could not be reached.") from exc
        if response.status_code != 200:
            raise CodeExecutionUnavailable(f"The code execution service returned HTTP {response.status_code}.")
        result = response.json()
        if not isinstance(result, dict) or "status" not in result:
            raise CodeExecutionUnavailable("The code execution service returned an unexpected response.")
        return result


@lru_cache
def _default_runner() -> CodeRunner:
    settings = get_settings()
    if settings.code_runner_url and settings.code_runner_token:
        return RemoteCodeRunner(settings.code_runner_url, settings.code_runner_token)
    return UnavailableCodeRunner()


def get_code_runner() -> CodeRunner:
    """FastAPI dependency (overridable in tests)."""
    return _default_runner()
