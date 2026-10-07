"""Notes / highlights / bookmarks, optional-auth handling, rate limiting, and admin conflicts + audit trail."""
import asyncio
import uuid

import pytest
from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.session import AsyncSessionLocal
from app.models.audit import AdminAuditLog
from app.models.content import Bookmark
from test_practice_run import locked_module_lesson  # noqa: F401  (re-used fixture)


# ---------------------------------------------------------------- notes
async def test_note_roundtrip_returns_lesson_id_and_trims(client, seeded_course, auth_headers):
    lid = str(seeded_course["lesson_id"])
    resp = await client.post(f"/api/lessons/{lid}/notes", json={"content": "  remember this  "}, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["lesson_id"] == lid
    assert resp.json()["content"] == "remember this"

    listed = await client.get(f"/api/lessons/{lid}/notes", headers=auth_headers)
    assert listed.status_code == 200
    assert [(n["lesson_id"], n["content"]) for n in listed.json()] == [(lid, "remember this")]


@pytest.mark.parametrize("content", ["", "   ", 123, None, ["a"], "x" * 10_001])
async def test_note_rejects_invalid_content(client, seeded_course, auth_headers, content):
    resp = await client.post(f"/api/lessons/{seeded_course['lesson_id']}/notes", json={"content": content}, headers=auth_headers)
    assert resp.status_code == 422


async def test_note_requires_auth(client, seeded_course):
    resp = await client.post(f"/api/lessons/{seeded_course['lesson_id']}/notes", json={"content": "hi"})
    assert resp.status_code == 401


async def test_note_on_unknown_lesson_is_404_not_500(client, auth_headers):
    resp = await client.post(f"/api/lessons/{uuid.uuid4()}/notes", json={"content": "hi"}, headers=auth_headers)
    assert resp.status_code == 404


async def test_note_on_locked_module_lesson_is_403(client, locked_module_lesson, auth_headers):
    resp = await client.post(
        f"/api/lessons/{locked_module_lesson['locked_lesson_id']}/notes", json={"content": "sneaky"}, headers=auth_headers
    )
    assert resp.status_code == 403


# ----------------------------------------------------------- highlights
async def test_highlight_roundtrip_and_default_color(client, seeded_course, auth_headers):
    lid = str(seeded_course["lesson_id"])
    resp = await client.post(f"/api/lessons/{lid}/highlights", json={"text": "key idea"}, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["lesson_id"] == lid and body["color"] == "yellow" and body["created_at"]

    resp = await client.post(f"/api/lessons/{lid}/highlights", json={"text": "hex", "color": "#fde68a"}, headers=auth_headers)
    assert resp.status_code == 200 and resp.json()["color"] == "#fde68a"


@pytest.mark.parametrize(
    "payload",
    [{"text": ""}, {"text": "  "}, {"text": "x" * 2_001}, {"text": "ok", "color": "c" * 21}, {"text": "ok", "color": "bad color!"}, {"text": 5}],
)
async def test_highlight_rejects_invalid_payload(client, seeded_course, auth_headers, payload):
    resp = await client.post(f"/api/lessons/{seeded_course['lesson_id']}/highlights", json=payload, headers=auth_headers)
    assert resp.status_code == 422


async def test_highlight_unknown_lesson_404_and_locked_403(client, locked_module_lesson, auth_headers):
    resp = await client.post(f"/api/lessons/{uuid.uuid4()}/highlights", json={"text": "x"}, headers=auth_headers)
    assert resp.status_code == 404
    resp = await client.post(
        f"/api/lessons/{locked_module_lesson['locked_lesson_id']}/highlights", json={"text": "x"}, headers=auth_headers
    )
    assert resp.status_code == 403


# ------------------------------------------------------------ bookmarks
async def test_bookmark_toggles_and_validates_lesson(client, seeded_course, auth_headers):
    url = f"/api/lessons/{seeded_course['lesson_id']}/bookmark"
    assert (await client.post(url, headers=auth_headers)).json() == {"bookmarked": True}
    assert (await client.post(url, headers=auth_headers)).json() == {"bookmarked": False}

    resp = await client.post(f"/api/lessons/{uuid.uuid4()}/bookmark", headers=auth_headers)
    assert resp.status_code == 404


async def test_concurrent_bookmark_toggles_never_duplicate_or_500(client, seeded_course, auth_headers):
    lesson_id = seeded_course["lesson_id"]
    url = f"/api/lessons/{lesson_id}/bookmark"
    results = await asyncio.gather(*[client.post(url, headers=auth_headers) for _ in range(12)])
    assert [r.status_code for r in results] == [200] * 12

    async with AsyncSessionLocal() as db:
        rows = (await db.execute(select(func.count()).select_from(Bookmark).where(Bookmark.lesson_id == lesson_id))).scalar_one()
    assert rows <= 1

    # the endpoint must still work afterwards (previously duplicates made every later toggle a 500)
    assert (await client.post(url, headers=auth_headers)).status_code == 200


# --------------------------------------------------------- lesson payload
async def test_lesson_detail_includes_course_id(client, seeded_course, auth_headers):
    resp = await client.get(f"/api/lessons/{seeded_course['lesson_id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["course_id"] == str(seeded_course["course_id"])


# ---------------------------------------------------------- optional auth
async def test_bad_token_on_optional_auth_routes_is_401_so_the_client_can_refresh(client, seeded_course):
    bad = {"Authorization": "Bearer not-a-real-token"}
    for path in ("/api/courses", f"/api/courses/{seeded_course['course_id']}", f"/api/lessons/{seeded_course['lesson_id']}"):
        assert (await client.get(path, headers=bad)).status_code == 401, path


async def test_refresh_token_is_not_accepted_as_an_access_token(client):
    reg = await client.post("/api/auth/register", json={
        "email": f"wrongtype-{uuid.uuid4().hex[:8]}@example.com", "password": "StrongPass123!", "full_name": "T",
    })
    resp = await client.get("/api/courses", headers={"Authorization": f"Bearer {reg.json()['refresh_token']}"})
    assert resp.status_code == 401


async def test_public_routes_still_work_without_a_token(client, seeded_course):
    assert (await client.get("/api/courses")).status_code == 200
    assert (await client.get(f"/api/courses/{seeded_course['course_id']}")).status_code == 200


async def test_validation_errors_are_sanitised(client):
    resp = await client.post("/api/auth/register", json={"email": "not-an-email", "password": "short-pw", "full_name": "T"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["detail"] == "Invalid request data"
    assert all(set(e) == {"loc", "msg", "type"} for e in body["errors"])
    assert "short-pw" not in resp.text  # the submitted password must not be echoed back


# ---------------------------------------------------------- rate limiting
@pytest.fixture
def rate_limiting():
    limiter.reset()
    limiter.enabled = True
    yield
    limiter.enabled = False
    limiter.reset()


async def test_login_attempts_are_rate_limited(client, rate_limiting):
    allowed = int(get_settings().rate_limit_auth.split("/")[0])
    codes, last = [], None
    for _ in range(allowed + 2):
        last = await client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "wrong-password"})
        codes.append(last.status_code)
    assert codes[:allowed] == [401] * allowed
    assert codes[allowed:] == [429, 429]
    assert last.json() == {"detail": "Too many requests. Please wait a moment and try again."}
    assert int(last.headers["retry-after"]) > 0


async def test_general_api_has_a_default_limit_but_health_is_exempt(client, rate_limiting):
    for _ in range(130):
        assert (await client.get("/api/health")).status_code == 200
    codes = [(await client.get("/api/courses")).status_code for _ in range(125)]
    assert 429 in codes and codes[0] == 200


# ------------------------------------------------- admin conflicts + audit
async def _audit_rows(**filters):
    async with AsyncSessionLocal() as db:
        query = select(AdminAuditLog).order_by(AdminAuditLog.created_at)
        for column, value in filters.items():
            query = query.where(getattr(AdminAuditLog, column) == value)
        return (await db.execute(query)).scalars().all()


async def test_admin_delete_of_a_referenced_skill_is_409_not_500(client, admin_headers, seeded_course, seeded_assessment):
    resp = await client.delete(f"/api/admin/skills/{seeded_course['skill_id']}", headers=admin_headers)
    assert resp.status_code == 409, resp.text
    assert "cannot be deleted" in resp.json()["detail"]
    # the session was rolled back cleanly: the skill is still there and the API still works
    assert (await client.get("/api/skills", headers=admin_headers)).status_code == 200


async def test_admin_duplicate_slug_is_409(client, admin_headers):
    body = {"slug": f"dup-{uuid.uuid4().hex[:8]}", "title": "Dup", "description": "d"}
    assert (await client.post("/api/admin/courses", json=body, headers=admin_headers)).status_code == 200
    resp = await client.post("/api/admin/courses", json=body, headers=admin_headers)
    assert resp.status_code == 409
    assert "duplicate slug" in resp.json()["detail"]


async def test_admin_mutations_are_audited_and_reads_are_not(client, admin_headers):
    before = len(await _audit_rows(method="POST", path="/api/admin/courses"))
    slug = f"audit-{uuid.uuid4().hex[:8]}"
    created = await client.post("/api/admin/courses", json={"slug": slug, "title": "Audit", "description": "d"}, headers=admin_headers)
    assert created.status_code == 200
    course_id = created.json()["id"]

    rows = await _audit_rows(method="POST", path="/api/admin/courses")
    assert len(rows) == before + 1
    assert rows[-1].status_code == 200 and rows[-1].entity == "courses" and rows[-1].actor_email.startswith("admin-")

    assert (await client.delete(f"/api/admin/courses/{course_id}", headers=admin_headers)).status_code == 200
    deleted = (await _audit_rows(method="DELETE", entity_id=course_id))[-1]
    assert deleted.status_code == 200 and deleted.entity == "courses"

    # failed attempts are recorded with their outcome
    missing = str(uuid.uuid4())
    assert (await client.delete(f"/api/admin/courses/{missing}", headers=admin_headers)).status_code == 404
    assert (await _audit_rows(method="DELETE", entity_id=missing))[-1].status_code == 404

    reads_before = len(await _audit_rows(method="GET"))
    assert (await client.get("/api/admin/users", headers=admin_headers)).status_code == 200
    assert len(await _audit_rows(method="GET")) == reads_before == 0


async def test_non_admin_admin_attempt_is_403_and_not_recorded(client, auth_headers):
    before = len(await _audit_rows())
    assert (await client.post("/api/admin/courses", json={"slug": "x", "title": "x", "description": "x"}, headers=auth_headers)).status_code == 403
    assert len(await _audit_rows()) == before
