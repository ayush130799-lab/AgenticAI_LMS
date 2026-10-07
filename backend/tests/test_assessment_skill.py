async def test_start_and_submit_assessment_updates_skill(client, seeded_assessment, seeded_course, auth_headers):
    resp = await client.post("/api/assessments/start", json={"assessment_id": str(seeded_assessment["assessment_id"])}, headers=auth_headers)
    assert resp.status_code == 200
    attempt_id = resp.json()["attempt_id"]
    q1, q2 = seeded_assessment["question_ids"]

    resp = await client.post("/api/assessments/submit", json={
        "attempt_id": attempt_id,
        "answers": {str(q1): {"choice": "b"}, str(q2): {"choice": "a"}},
    }, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["score"] == 100.0
    assert body["passed"] is True

    resp = await client.get("/api/students/me/skills", headers=auth_headers)
    assert resp.status_code == 200
    skills = {s["skill_slug"]: s for s in resp.json()}
    test_skill = next(v for k, v in skills.items() if k.startswith("test-skill"))
    assert test_skill["attempts"] == 1
    assert test_skill["mastery"] > 0.0  # a correct assessment attempt should move mastery up from zero


async def test_partial_score_produces_weak_concepts(client, seeded_assessment, auth_headers):
    resp = await client.post("/api/assessments/start", json={"assessment_id": str(seeded_assessment["assessment_id"])}, headers=auth_headers)
    attempt_id = resp.json()["attempt_id"]
    q1, q2 = seeded_assessment["question_ids"]

    resp = await client.post("/api/assessments/submit", json={
        "attempt_id": attempt_id,
        "answers": {str(q1): {"choice": "a"}, str(q2): {"choice": "b"}},  # both wrong
    }, headers=auth_headers)
    body = resp.json()
    assert body["score"] == 0.0
    assert body["passed"] is False
    assert len(body["weak_concepts"]) >= 1


async def test_cannot_resubmit_graded_attempt(client, seeded_assessment, auth_headers):
    resp = await client.post("/api/assessments/start", json={"assessment_id": str(seeded_assessment["assessment_id"])}, headers=auth_headers)
    attempt_id = resp.json()["attempt_id"]
    q1, q2 = seeded_assessment["question_ids"]
    payload = {"attempt_id": attempt_id, "answers": {str(q1): {"choice": "b"}, str(q2): {"choice": "a"}}}

    await client.post("/api/assessments/submit", json=payload, headers=auth_headers)
    resp = await client.post("/api/assessments/submit", json=payload, headers=auth_headers)
    assert resp.status_code == 400


async def test_ui_shaped_answers_are_graded_correctly(client, seeded_assessment, auth_headers):
    """The web UI submits {selected: ...}; it must grade the same as {choice: ...}."""
    resp = await client.post("/api/assessments/start", json={"assessment_id": str(seeded_assessment["assessment_id"])}, headers=auth_headers)
    attempt_id = resp.json()["attempt_id"]
    q1, q2 = seeded_assessment["question_ids"]

    resp = await client.post("/api/assessments/submit", json={
        "attempt_id": attempt_id,
        "answers": {str(q1): {"selected": "b"}, str(q2): {"selected": "a"}},
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["score"] == 100.0


async def test_submitting_an_assessment_refreshes_recommendations(client, seeded_assessment, auth_headers):
    """New mastery evidence must update the AI recommendations without a manual regenerate."""
    resp = await client.get("/api/recommendations", headers=auth_headers)
    assert resp.json() == []

    resp = await client.post("/api/assessments/start", json={"assessment_id": str(seeded_assessment["assessment_id"])}, headers=auth_headers)
    attempt_id = resp.json()["attempt_id"]
    q1, q2 = seeded_assessment["question_ids"]
    await client.post("/api/assessments/submit", json={
        "attempt_id": attempt_id, "answers": {str(q1): {"selected": "a"}, str(q2): {"selected": "b"}},
    }, headers=auth_headers)

    resp = await client.get("/api/recommendations", headers=auth_headers)
    assert len(resp.json()) >= 1
