"""API tests for the lesson practice code runner (open-ended, ungraded execution)."""
import uuid

import pytest
import pytest_asyncio

from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.curriculum import Course, Lesson, Module
from app.services import module_assessment_service
from app.services.code_execution import UnavailableCodeRunner, get_code_runner
from module_assessment_helpers import FakeCodeRunner, seed_assessment, unique


@pytest.fixture(autouse=True)
def fake_runner():
    app.dependency_overrides[get_code_runner] = lambda: FakeCodeRunner()
    yield
    app.dependency_overrides.pop(get_code_runner, None)


async def test_run_practice_code_returns_stdout(client, seeded_course, auth_headers):
    resp = await client.post(
        f"/api/lessons/{seeded_course['lesson_id']}/practice/run",
        json={"code": "print('hello from practice')"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "ok"
    assert "hello from practice" in body["stdout"]
    assert body["error"] is None


async def test_run_practice_code_reports_errors_without_failing_the_request(client, seeded_course, auth_headers):
    resp = await client.post(
        f"/api/lessons/{seeded_course['lesson_id']}/practice/run",
        json={"code": "raise ValueError('oops')"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "error"
    assert "oops" in body["error"]


async def test_run_practice_code_rejects_empty_code(client, seeded_course, auth_headers):
    resp = await client.post(
        f"/api/lessons/{seeded_course['lesson_id']}/practice/run", json={"code": "   "}, headers=auth_headers,
    )
    assert resp.status_code == 422


async def test_run_practice_code_requires_auth(client, seeded_course):
    resp = await client.post(f"/api/lessons/{seeded_course['lesson_id']}/practice/run", json={"code": "print(1)"})
    assert resp.status_code == 401


async def test_run_practice_code_404s_for_unknown_lesson(client, auth_headers):
    resp = await client.post(f"/api/lessons/{uuid.uuid4()}/practice/run", json={"code": "print(1)"}, headers=auth_headers)
    assert resp.status_code == 404


async def test_run_practice_code_503s_when_the_sandbox_is_unavailable(client, seeded_course, auth_headers):
    app.dependency_overrides[get_code_runner] = lambda: UnavailableCodeRunner()
    resp = await client.post(
        f"/api/lessons/{seeded_course['lesson_id']}/practice/run", json={"code": "print(1)"}, headers=auth_headers,
    )
    assert resp.status_code == 503


@pytest_asyncio.fixture
async def locked_module_lesson():
    """A second module behind an unpassed gate, with its own (not-yet-completed) lesson."""
    data = seed_assessment("beginner")
    async with AsyncSessionLocal() as db:
        course = Course(slug=unique("gated-practice"), title="Gated", description="d", level="beginner", order_index=99, estimated_hours=1)
        db.add(course)
        await db.flush()
        m1 = Module(course_id=course.id, slug=unique("m1"), title="Module One", description="d", order_index=1)
        m2 = Module(course_id=course.id, slug=unique("m2"), title="Module Two", description="d", order_index=2)
        db.add_all([m1, m2])
        await db.flush()
        l1 = Lesson(
            module_id=m1.id, slug=unique("l1"), title="L1", description="d", lesson_type="reading", order_index=1,
            estimated_minutes=5, learning_objectives=[], content_markdown="body", examples=[], practice_exercises=[], resources=[],
        )
        l2 = Lesson(
            module_id=m2.id, slug=unique("l2"), title="L2", description="d", lesson_type="coding", order_index=1,
            estimated_minutes=5, learning_objectives=[], content_markdown="body", examples=[], practice_exercises=[], resources=[],
        )
        db.add_all([l1, l2])
        await db.flush()
        await module_assessment_service.upsert_module_assessment(db, data, module_id=m1.id, publish=True)
        await db.commit()
        return {"locked_lesson_id": str(l2.id)}


async def test_run_practice_code_403s_for_a_locked_module(client, locked_module_lesson, auth_headers):
    resp = await client.post(
        f"/api/lessons/{locked_module_lesson['locked_lesson_id']}/practice/run",
        json={"code": "print(1)"}, headers=auth_headers,
    )
    assert resp.status_code == 403
