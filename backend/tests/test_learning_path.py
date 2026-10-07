async def test_generate_learning_path(client, seeded_course, auth_headers):
    resp = await client.post("/api/learning-path/generate", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["summary"]
    assert isinstance(body["recommended_path"], list)
    assert len(body["recommended_path"]) >= 1


async def test_get_learning_path_creates_one_if_missing(client, seeded_course, auth_headers):
    resp = await client.get("/api/learning-path", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["summary"]


async def test_recommendations_populated_after_plan_generation(client, seeded_course, auth_headers):
    await client.post("/api/learning-path/generate", headers=auth_headers)
    resp = await client.get("/api/recommendations", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_dashboard_reflects_real_state(client, seeded_course, auth_headers):
    await client.post(f"/api/lessons/{seeded_course['lesson_id']}/complete", headers=auth_headers)
    resp = await client.get("/api/dashboard", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["curriculum_progress_percent"] > 0
    assert body["continue_lesson"] is None or isinstance(body["continue_lesson"], dict)


async def test_plan_steps_reference_real_skills(client, seeded_course, auth_headers):
    """The planner must receive real skill slugs, so no step may point at a null skill."""
    resp = await client.post("/api/learning-path/generate", headers=auth_headers)
    assert resp.status_code == 200
    for step in resp.json()["recommended_path"]:
        assert all(isinstance(slug, str) and slug for slug in step["skill_focus"])


def test_stored_plan_with_null_skill_entries_still_serializes():
    """Plans stored by an earlier planner bug contain null skill_focus entries; reading them must not 500."""
    from app.schemas.learning import LearningPlanStepOut

    step = LearningPlanStepOut(step_type="lesson", target_id=None, title="t", reason="r", skill_focus=[None, "python"])
    assert step.skill_focus == ["python"]
