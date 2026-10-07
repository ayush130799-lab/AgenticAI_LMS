"""
Test fixtures. Requires a real Postgres+pgvector instance (the same one
docker-compose provisions) — SQLite can't represent this schema (UUID,
JSONB, ARRAY, pgvector columns are all Postgres-specific).

Point TEST_DATABASE_URL at a throwaway database before running pytest, e.g.:

    docker compose up -d postgres
    createdb -h localhost -U lms_user agentic_ai_lms_test
    TEST_DATABASE_URL=postgresql+psycopg://lms_user:lms_password@localhost:5432/agentic_ai_lms_test pytest
"""
import asyncio
import os
import sys
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

if sys.platform == "win32":  # psycopg async needs the selector loop
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg://lms_user:lms_password@localhost:5432/agentic_ai_lms_test"),
)
# The suite fires far more than 120 requests/minute from one "IP"; rate-limit tests switch the limiter on themselves.
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
# The fixtures below DROP and recreate every table. Inside the docker-compose backend container DATABASE_URL already
# points at the development database, and setdefault() above does not override it - so refuse to continue unless the
# target is clearly a throwaway database.
if not TEST_DATABASE_URL.split("?")[0].rsplit("/", 1)[-1].endswith("_test"):
    raise RuntimeError(
        "Refusing to run the test suite: DATABASE_URL must point at a database whose name ends in '_test' "
        f"(got {TEST_DATABASE_URL.rsplit('/', 1)[-1]!r}). The tests drop and recreate every table."
    )

from app.db import session as db_session_module  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _setup_database():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    test_session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    db_session_module.engine = engine
    db_session_module.AsyncSessionLocal = test_session_factory

    yield

    await engine.dispose()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def student_token(client):
    email = f"student-{uuid.uuid4().hex[:10]}@example.com"
    resp = await client.post("/api/auth/register", json={
        "email": email, "password": "StrongPass123!", "full_name": "Test Student",
    })
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(student_token):
    return {"Authorization": f"Bearer {student_token}"}


@pytest_asyncio.fixture
async def seeded_course():
    """Minimal real curriculum data (one skill/course/module/lesson) for
    tests that don't want to pay the cost of running the full content seed."""
    from app.db.session import AsyncSessionLocal
    from app.models.curriculum import Course, Lesson, LessonSkill, Module, Skill

    suffix = uuid.uuid4().hex[:8]
    async with AsyncSessionLocal() as db:
        skill = Skill(slug=f"test-skill-{suffix}", name="Test Skill", description="A skill for tests", category="foundations")
        db.add(skill)
        await db.flush()

        course = Course(
            slug=f"test-course-{suffix}", title="Test Course", description="A course for tests",
            learning_outcomes=["Outcome one"], order_index=1, estimated_hours=1, level="beginner",
        )
        db.add(course)
        await db.flush()

        module = Module(course_id=course.id, slug=f"test-module-{suffix}", title="Test Module", description="desc", order_index=1)
        db.add(module)
        await db.flush()

        lesson = Lesson(
            module_id=module.id, slug=f"test-lesson-{suffix}", title="Test Lesson", description="desc",
            lesson_type="reading", order_index=1, estimated_minutes=10, learning_objectives=["Learn X"],
            content_markdown="## Test content\nThis is a real test lesson body about Test Skill.",
            examples=[], practice_exercises=[], resources=[],
        )
        db.add(lesson)
        await db.flush()
        db.add(LessonSkill(lesson_id=lesson.id, skill_id=skill.id, weight=1.0))
        await db.commit()

        return {"skill_id": skill.id, "course_id": course.id, "module_id": module.id, "lesson_id": lesson.id}


@pytest_asyncio.fixture
async def seeded_assessment(seeded_course):
    from app.db.session import AsyncSessionLocal
    from app.models.assessment import Assessment, Question

    async with AsyncSessionLocal() as db:
        assessment = Assessment(
            title="Test Skill Check", assessment_type="skill_check", passing_score=0.5, time_limit_minutes=10,
        )
        db.add(assessment)
        await db.flush()

        q1 = Question(
            assessment_id=assessment.id, skill_id=seeded_course["skill_id"], question_type="mcq",
            prompt="2 + 2 = ?", options=[{"id": "a", "text": "3"}, {"id": "b", "text": "4"}],
            correct_answer={"choice": "b"}, explanation="Basic arithmetic.", points=1.0, order_index=0,
        )
        q2 = Question(
            assessment_id=assessment.id, skill_id=seeded_course["skill_id"], question_type="mcq",
            prompt="3 + 3 = ?", options=[{"id": "a", "text": "6"}, {"id": "b", "text": "5"}],
            correct_answer={"choice": "a"}, explanation="Basic arithmetic.", points=1.0, order_index=1,
        )
        db.add_all([q1, q2])
        await db.commit()
        return {"assessment_id": assessment.id, "question_ids": [q1.id, q2.id]}


@pytest_asyncio.fixture
async def seeded_rag_chunk(seeded_course):
    from app.db.session import AsyncSessionLocal
    from app.models.rag import DocumentChunk

    from ai_engine.rag.embedder import embed_text
    from ai_engine.rag.ingest import build_lesson_chunks

    lesson = {
        "id": str(seeded_course["lesson_id"]), "title": "Test Lesson",
        "content_markdown": "## Test content\nThis is a real test lesson body about Test Skill and how it works in practice.",
        "examples": [],
    }
    chunks = build_lesson_chunks(lesson)
    async with AsyncSessionLocal() as db:
        for chunk in chunks:
            db.add(DocumentChunk(
                lesson_id=seeded_course["lesson_id"], source_type="lesson",
                title=chunk.get("title", lesson["title"]), chunk_index=chunk["chunk_index"],
                content=chunk["content"], embedding=embed_text(chunk["content"]),
            ))
        await db.commit()
    return seeded_course


@pytest_asyncio.fixture
async def admin_headers(client):
    from app.core.security import hash_password
    from app.db.session import AsyncSessionLocal
    from app.models.user import User

    email = f"admin-{uuid.uuid4().hex[:8]}@example.com"
    async with AsyncSessionLocal() as db:
        db.add(User(email=email, hashed_password=hash_password("AdminPass123!"), full_name="Test Admin", role="admin"))
        await db.commit()

    resp = await client.post("/api/auth/login", json={"email": email, "password": "AdminPass123!"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
