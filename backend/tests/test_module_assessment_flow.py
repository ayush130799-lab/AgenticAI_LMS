"""API tests for module assessments and progression gating (spec tests 1, 2, 13-23 plus security checks)."""
import uuid

import pytest
import pytest_asyncio

from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.curriculum import Course, Lesson, Module
from app.services import module_assessment_service
from app.services.code_execution import UnavailableCodeRunner, get_code_runner
from module_assessment_helpers import FakeCodeRunner, answers_for, seed_assessment, unique


@pytest.fixture(autouse=True)
def fake_runner():
    app.dependency_overrides[get_code_runner] = lambda: FakeCodeRunner()
    yield
    app.dependency_overrides.pop(get_code_runner, None)


def _lesson(module_id, n):
    return Lesson(
        module_id=module_id, slug=unique(f"l{n}"), title=f"Lesson {n}", description="d", lesson_type="reading", order_index=n,
        estimated_minutes=5, learning_objectives=[], content_markdown="body", examples=[], practice_exercises=[], resources=[],
    )


@pytest_asyncio.fixture
async def gated_course():
    """Course: M1 (2 lessons, published beginner assessment) -> M2 (1 lesson, no assessment) -> M3 (1 lesson)."""
    data = seed_assessment("beginner")
    async with AsyncSessionLocal() as db:
        course = Course(slug=unique("gated"), title="Gated", description="d", level="beginner", order_index=99, estimated_hours=1)
        db.add(course)
        await db.flush()
        mods = []
        for i, title in enumerate(["Module One", "Module Two", "Module Three"], 1):
            m = Module(course_id=course.id, slug=unique(f"m{i}"), title=title, description="d", order_index=i)
            db.add(m)
            await db.flush()
            mods.append(m)
        lessons = {0: [_lesson(mods[0].id, 1), _lesson(mods[0].id, 2)], 1: [_lesson(mods[1].id, 1)], 2: [_lesson(mods[2].id, 1)]}
        for group in lessons.values():
            db.add_all(group)
        await db.flush()
        assessment = await module_assessment_service.upsert_module_assessment(db, data, module_id=mods[0].id, publish=True)
        await db.commit()
        return {
            "data": data, "course_id": course.id, "assessment_id": str(assessment.id),
            "modules": [str(m.id) for m in mods], "lessons": {k: [str(item.id) for item in v] for k, v in lessons.items()},
        }


async def complete(client, headers, lesson_ids):
    for lid in lesson_ids:
        r = await client.post(f"/api/lessons/{lid}/complete", headers=headers)
        assert r.status_code == 200, r.text


async def start(client, headers, assessment_id):
    r = await client.post(f"/api/module-assessments/{assessment_id}/attempts", headers=headers)
    assert r.status_code == 200, r.text
    return r.json()


async def submit(client, headers, attempt_id, answers, **extra):
    return await client.post(f"/api/module-assessments/attempts/{attempt_id}/submit", json={"answers": answers, **extra}, headers=headers)


async def progress(client, headers, module_id):
    return (await client.get(f"/api/modules/{module_id}/progress", headers=headers)).json()


# ---- Tests 1 & 2: availability -------------------------------------------------------------------
async def test_assessment_locked_until_all_lessons_completed(client, auth_headers, gated_course):
    state = await progress(client, auth_headers, gated_course["modules"][0])
    assert state["assessment"]["status"] == "locked"
    assert state["assessment"]["unavailable_reason"] == "Complete all lessons in this module to unlock the assessment."

    await complete(client, auth_headers, gated_course["lessons"][0][:1])
    assert (await progress(client, auth_headers, gated_course["modules"][0]))["assessment"]["status"] == "locked"

    # direct URL access cannot bypass the lock
    view = await client.get(f"/api/module-assessments/{gated_course['assessment_id']}", headers=auth_headers)
    begin = await client.post(f"/api/module-assessments/{gated_course['assessment_id']}/attempts", headers=auth_headers)
    for r in (view, begin):
        assert r.status_code == 403 and "Complete all lessons" in r.json()["detail"]


async def test_assessment_available_after_all_lessons(client, auth_headers, gated_course):
    await complete(client, auth_headers, gated_course["lessons"][0])
    state = await progress(client, auth_headers, gated_course["modules"][0])
    assert state["all_lessons_completed"] and state["assessment"]["status"] == "available"
    assert state["status"] == "in_progress"  # lessons done, assessment pending: NOT completed


async def test_final_lesson_does_not_unlock_the_next_module(client, auth_headers, gated_course):
    await complete(client, auth_headers, gated_course["lessons"][0])
    assert (await progress(client, auth_headers, gated_course["modules"][1]))["locked"] is True


# ---- Module locking / unlocking (tests 15, 16, 19) ---------------------------------------------
async def test_locked_module_lessons_are_denied_server_side(client, auth_headers, gated_course):
    locked_lesson = gated_course["lessons"][1][0]
    assert (await client.get(f"/api/lessons/{locked_lesson}", headers=auth_headers)).status_code == 403
    assert (await client.get(f"/api/lessons/{locked_lesson}")).status_code == 403  # anonymous too
    r = await client.post(f"/api/lessons/{locked_lesson}/complete", headers=auth_headers)  # "fake completion"
    assert r.status_code == 403 and "Pass the assessment" in r.json()["detail"]
    assert (await client.get(f"/api/modules/{gated_course['modules'][2]}/access", headers=auth_headers)).json()["accessible"] is False


async def test_client_cannot_fake_module_completion_or_score(client, auth_headers, gated_course):
    await complete(client, auth_headers, gated_course["lessons"][0])
    attempt = await start(client, auth_headers, gated_course["assessment_id"])
    view = attempt["assessment"]["questions"]
    all_wrong = answers_for(gated_course["data"], view, wrong=set(range(7)))
    r = await submit(client, auth_headers, attempt["attempt"]["id"], all_wrong,
                     score=100, percentage=100, passed=True, is_correct=True, module_completed=True)
    assert r.status_code == 200
    result = r.json()
    assert result["result"]["passed"] is False and result["result"]["percentage"] < 50  # recalculated on the server
    assert (await progress(client, auth_headers, gated_course["modules"][0]))["status"] != "completed"
    assert (await progress(client, auth_headers, gated_course["modules"][1]))["locked"] is True


async def test_pass_completes_module_and_unlocks_next(client, auth_headers, gated_course):
    await complete(client, auth_headers, gated_course["lessons"][0])
    attempt = await start(client, auth_headers, gated_course["assessment_id"])
    answers = answers_for(gated_course["data"], attempt["assessment"]["questions"], wrong={3})  # 1 quiz wrong => 6/7
    r = await submit(client, auth_headers, attempt["attempt"]["id"], answers)
    body = r.json()
    assert body["result"]["passed"] and body["result"]["percentage"] == 85.7
    assert (body["result"]["mcq"], body["result"]["quiz"], body["result"]["coding"]) == (
        {"correct": 3, "total": 3}, {"correct": 1, "total": 2}, {"correct": 2, "total": 2})
    assert body["next_module"]["module_id"] == gated_course["modules"][1]

    assert (await progress(client, auth_headers, gated_course["modules"][0]))["status"] == "completed"
    assert (await progress(client, auth_headers, gated_course["modules"][1]))["locked"] is False
    assert (await client.get(f"/api/lessons/{gated_course['lessons'][1][0]}", headers=auth_headers)).status_code == 200
    course = (await client.get(f"/api/courses/{gated_course['course_id']}", headers=auth_headers)).json()
    assert course["modules"][0]["status"] == "completed" and course["modules_completed"] == 1


async def test_progress_made_before_gating_is_grandfathered(client, auth_headers, gated_course):
    """A student who already completed a lesson in a now-gated-behind module keeps access to that module."""
    from sqlalchemy import select

    from app.models.enrollment import LessonProgress
    from app.models.user import User

    me = (await client.get("/api/auth/me", headers=auth_headers)).json()
    legacy_lesson = gated_course["lessons"][1][0]  # module 2: locked for a fresh student
    assert (await client.get(f"/api/lessons/{legacy_lesson}", headers=auth_headers)).status_code == 403
    async with AsyncSessionLocal() as db:  # simulate progress recorded before the gate existed
        db.add(LessonProgress(user_id=uuid.UUID(me["id"]), lesson_id=uuid.UUID(legacy_lesson), status="completed"))
        await db.commit()
    assert (await client.get(f"/api/lessons/{legacy_lesson}", headers=auth_headers)).status_code == 200
    assert (await progress(client, auth_headers, gated_course["modules"][1]))["locked"] is False
    # ...but modules the student has NOT started remain gated
    assert (await progress(client, auth_headers, gated_course["modules"][2]))["locked"] is True


# ---- Tests 13, 14: fail -> retry -> pass; attempts stored separately ---------------------------
async def test_fail_then_retry_then_pass_stores_every_attempt(client, auth_headers, gated_course):
    await complete(client, auth_headers, gated_course["lessons"][0])
    data, aid = gated_course["data"], gated_course["assessment_id"]

    first = await start(client, auth_headers, aid)
    r1 = (await submit(client, auth_headers, first["attempt"]["id"], answers_for(data, first["assessment"]["questions"], wrong={0, 1, 2, 3}))).json()
    assert r1["result"]["passed"] is False and r1["attempt"]["attempt_number"] == 1
    assert (await progress(client, auth_headers, gated_course["modules"][0]))["assessment"]["status"] == "available"  # retry allowed

    second = await start(client, auth_headers, aid)
    assert second["attempt"]["attempt_number"] == 2 and second["attempt"]["id"] != first["attempt"]["id"]
    r2 = (await submit(client, auth_headers, second["attempt"]["id"], answers_for(data, second["assessment"]["questions"], wrong={0, 1, 2, 3, 4}))).json()
    assert r2["result"]["passed"] is False

    third = await start(client, auth_headers, aid)
    r3 = (await submit(client, auth_headers, third["attempt"]["id"], answers_for(data, third["assessment"]["questions"]))).json()
    assert r3["result"]["passed"] and r3["result"]["percentage"] == 100.0

    history = (await client.get(f"/api/module-assessments/{aid}/attempts", headers=auth_headers)).json()
    assert [(a["attempt_number"], a["passed"]) for a in history] == [(1, False), (2, False), (3, True)]
    assert (await progress(client, auth_headers, gated_course["modules"][0]))["status"] == "completed"
    assert (await client.post(f"/api/module-assessments/{aid}/attempts", headers=auth_headers)).status_code == 409  # already passed


async def test_failed_result_hides_the_answer_key_but_a_pass_reveals_it(client, auth_headers, gated_course):
    await complete(client, auth_headers, gated_course["lessons"][0])
    data, aid = gated_course["data"], gated_course["assessment_id"]
    a = await start(client, auth_headers, aid)
    failed = (await submit(client, auth_headers, a["attempt"]["id"], answers_for(data, a["assessment"]["questions"], wrong={0, 1, 2, 3, 4}))).json()
    assert all(q["explanation"] is None and q["correct_answer"] is None for q in failed["questions"])
    b = await start(client, auth_headers, aid)
    passed = (await submit(client, auth_headers, b["attempt"]["id"], answers_for(data, b["assessment"]["questions"]))).json()
    assert all(q["explanation"] for q in passed["questions"])


# ---- Secrets, authorization, validation -----------------------------------------------------------
async def test_answer_key_never_appears_before_submission(client, auth_headers, gated_course):
    await complete(client, auth_headers, gated_course["lessons"][0])
    attempt = await start(client, auth_headers, gated_course["assessment_id"])
    text = str(attempt)
    assert "correct_answer" not in text and "explanation" not in text and "solution" not in text

    views = [q for q in attempt["assessment"]["questions"] if q["coding"]]
    keys = [q for q in gated_course["data"]["questions"] if q["type"] == "coding"]
    for view, key in zip(views, keys):
        tests = key["coding_config"]["test_cases"]
        shown = view["coding"]["sample_tests"]
        assert shown == [{"args": t["args"], "expected": t["expected"]} for t in tests if t["visible"]]  # visible only
        assert view["coding"]["hidden_test_count"] == sum(1 for t in tests if not t["visible"]) >= 1


async def test_other_users_attempt_is_forbidden(client, auth_headers, gated_course):
    await complete(client, auth_headers, gated_course["lessons"][0])
    attempt = await start(client, auth_headers, gated_course["assessment_id"])
    aid = attempt["attempt"]["id"]
    other = (await client.post("/api/auth/register", json={"email": f"o-{uuid.uuid4().hex[:8]}@example.com", "password": "StrongPass123!", "full_name": "Other"})).json()
    other_headers = {"Authorization": f"Bearer {other['access_token']}"}
    assert (await client.get(f"/api/module-assessments/attempts/{aid}", headers=other_headers)).status_code == 403
    assert (await submit(client, other_headers, aid, {})).status_code == 403
    assert (await client.put(f"/api/module-assessments/attempts/{aid}/answers", json={"answers": {}}, headers=other_headers)).status_code == 403


async def test_unauthenticated_access_is_rejected(client, gated_course):
    assert (await client.get(f"/api/module-assessments/{gated_course['assessment_id']}")).status_code == 401
    assert (await client.get(f"/api/modules/{gated_course['modules'][0]}/progress")).status_code == 401


async def test_invalid_quiz_answer_is_a_validation_error_and_attempt_stays_open(client, auth_headers, gated_course):
    await complete(client, auth_headers, gated_course["lessons"][0])
    attempt = await start(client, auth_headers, gated_course["assessment_id"])
    quiz_id = str([q for q in attempt["assessment"]["questions"] if q["type"] == "quiz"][0]["id"])
    for bad in ({"choices": "abc"}, {"choice": 5}, {"choices": ["zzz"]}, {"text": ["x"]}):
        r = await submit(client, auth_headers, attempt["attempt"]["id"], {quiz_id: bad})
        assert r.status_code == 422, bad
    assert (await submit(client, auth_headers, attempt["attempt"]["id"], {"not-a-question": {"choice": "a"}})).status_code == 422
    state = (await client.get(f"/api/module-assessments/attempts/{attempt['attempt']['id']}", headers=auth_headers)).json()
    assert state["attempt"]["status"] == "in_progress"


async def test_attempt_cannot_be_submitted_twice(client, auth_headers, gated_course):
    await complete(client, auth_headers, gated_course["lessons"][0])
    attempt = await start(client, auth_headers, gated_course["assessment_id"])
    assert (await submit(client, auth_headers, attempt["attempt"]["id"], {})).status_code == 200
    assert (await submit(client, auth_headers, attempt["attempt"]["id"], {})).status_code == 409


# ---- Test 23: refresh consistency ----------------------------------------------------------------
async def test_refresh_resumes_the_same_attempt_with_saved_answers(client, auth_headers, gated_course):
    await complete(client, auth_headers, gated_course["lessons"][0])
    first = await start(client, auth_headers, gated_course["assessment_id"])
    qid = str(first["assessment"]["questions"][0]["id"])
    saved = await client.put(f"/api/module-assessments/attempts/{first['attempt']['id']}/answers", json={"answers": {qid: {"choice": "a"}}}, headers=auth_headers)
    assert saved.status_code == 200
    again = await start(client, auth_headers, gated_course["assessment_id"])  # "refresh"
    assert again["attempt"]["id"] == first["attempt"]["id"] and again["saved_answers"] == {qid: {"choice": "a"}}
    bogus = await client.put(f"/api/module-assessments/attempts/{first['attempt']['id']}/answers", json={"answers": {"bogus": {}}}, headers=auth_headers)
    assert bogus.status_code == 422


# ---- Test 22 (backend side): sandbox unavailable fails safely ------------------------------------
async def test_submission_fails_safely_when_code_execution_is_unavailable(client, auth_headers, gated_course):
    app.dependency_overrides[get_code_runner] = lambda: UnavailableCodeRunner()
    await complete(client, auth_headers, gated_course["lessons"][0])
    attempt = await start(client, auth_headers, gated_course["assessment_id"])
    answers = answers_for(gated_course["data"], attempt["assessment"]["questions"])
    r = await submit(client, auth_headers, attempt["attempt"]["id"], answers)
    assert r.status_code == 503 and "try again" in r.json()["detail"].lower()
    state = (await client.get(f"/api/module-assessments/attempts/{attempt['attempt']['id']}", headers=auth_headers)).json()
    assert state["attempt"]["status"] == "in_progress"  # nothing was graded or consumed


async def test_run_button_only_runs_visible_tests(client, auth_headers, gated_course):
    await complete(client, auth_headers, gated_course["lessons"][0])
    attempt = await start(client, auth_headers, gated_course["assessment_id"])
    coding_q = [q for q in attempt["assessment"]["questions"] if q["coding"]][0]
    idx = [q["type"] for q in gated_course["data"]["questions"]].index("coding")
    code = gated_course["data"]["questions"][idx]["coding_config"]["solution"]
    r = await client.post(f"/api/module-assessments/attempts/{attempt['attempt']['id']}/questions/{coding_q['id']}/run", json={"code": code}, headers=auth_headers)
    assert r.status_code == 200 and r.json()["total_count"] == len(coding_q["coding"]["sample_tests"])
    assert all(x["visible"] for x in r.json()["results"])


# ---- Backward compatibility (test 17) & the old assessment flow --------------------------------
async def test_modules_without_assessments_behave_exactly_as_before(client, auth_headers, seeded_course):
    state = await progress(client, auth_headers, str(seeded_course["module_id"]))
    assert state["has_assessment"] is False and state["assessment"] is None and state["locked"] is False
    lesson = str(seeded_course["lesson_id"])
    assert (await client.get(f"/api/lessons/{lesson}", headers=auth_headers)).status_code == 200
    assert (await client.post(f"/api/lessons/{lesson}/complete", headers=auth_headers)).status_code == 200
    detail = (await client.get(f"/api/courses/{seeded_course['course_id']}", headers=auth_headers)).json()
    assert detail["modules"][0]["status"] == "completed" and detail["modules"][0]["assessment_status"] is None
    assert (await client.get(f"/api/modules/{seeded_course['module_id']}/assessments", headers=auth_headers)).json() == []
    missing = await client.get(f"/api/module-assessments/{seeded_course['module_id']}", headers=auth_headers)
    assert missing.status_code == 404


async def test_old_assessment_flow_cannot_reach_module_assessments(client, auth_headers, gated_course):
    listed = (await client.get("/api/assessments", headers=auth_headers)).json()
    assert gated_course["assessment_id"] not in [a["id"] for a in listed]
    r = await client.post("/api/assessments/start", json={"assessment_id": gated_course["assessment_id"]}, headers=auth_headers)
    assert r.status_code == 404


async def test_dashboard_and_planner_never_point_at_locked_modules(client, auth_headers, gated_course):
    await complete(client, auth_headers, gated_course["lessons"][0])
    dash = (await client.get("/api/dashboard", headers=auth_headers)).json()
    hidden = set(gated_course["lessons"][1] + gated_course["lessons"][2])
    assert dash["continue_lesson"] is None or dash["continue_lesson"]["id"] not in hidden
    assert dash["pending_module_assessment"]["assessment_id"] == gated_course["assessment_id"]
    plan = (await client.post("/api/learning-path/generate", headers=auth_headers)).json()
    assert not {s["target_id"] for s in plan["recommended_path"]} & hidden


# ---- Admin: publishing requires a valid structure ------------------------------------------------
async def test_admin_cannot_publish_or_save_an_invalid_structure(client, admin_headers, gated_course):
    bad = seed_assessment("intermediate")
    bad["questions"].pop()
    body = {**{k: bad[k] for k in ("level", "title", "description", "questions")}, "module_id": gated_course["modules"][1]}
    r = await client.post("/api/admin/module-assessments", json=body, headers=admin_headers)
    assert r.status_code == 422 and any("exactly 7 questions" in e for e in r.json()["detail"]["errors"])


async def test_admin_publish_flow_and_edit_guard(client, admin_headers, auth_headers, gated_course):
    good = seed_assessment("intermediate")
    body = {**{k: good[k] for k in ("level", "title", "description", "questions")}, "module_id": gated_course["modules"][1], "publish": False}
    created = (await client.post("/api/admin/module-assessments", json=body, headers=admin_headers)).json()
    aid = created["id"]
    assert created["is_published"] is False
    assert (await client.get(f"/api/admin/module-assessments/{aid}/validate", headers=admin_headers)).json() == {"valid": True, "errors": []}
    assert (await client.post(f"/api/admin/module-assessments/{aid}/publish", headers=admin_headers)).status_code == 200
    # a published module assessment cannot be edited/deleted through the generic editor
    assert (await client.delete(f"/api/admin/assessments/{aid}", headers=admin_headers)).status_code == 409
    # non-admins cannot unpublish
    assert (await client.post(f"/api/admin/module-assessments/{aid}/unpublish", headers=auth_headers)).status_code == 403
