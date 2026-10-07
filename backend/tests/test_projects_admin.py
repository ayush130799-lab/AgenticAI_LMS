async def test_non_admin_cannot_access_admin_routes(client, auth_headers):
    resp = await client.post("/api/admin/courses", json={
        "slug": "hacked-course", "title": "x", "description": "x",
    }, headers=auth_headers)
    assert resp.status_code == 403


async def test_admin_can_create_course_and_skill(client, admin_headers):
    resp = await client.post("/api/admin/skills", json={
        "slug": "admin-test-skill", "name": "Admin Test Skill", "category": "foundations",
    }, headers=admin_headers)
    assert resp.status_code == 200

    resp = await client.post("/api/admin/courses", json={
        "slug": "admin-test-course", "title": "Admin Test Course", "description": "desc",
    }, headers=admin_headers)
    assert resp.status_code == 200
    assert "id" in resp.json()


async def test_unauthenticated_cannot_reach_admin(client):
    resp = await client.get("/api/admin/users")
    assert resp.status_code == 401


async def test_project_submission_gets_ai_feedback(client, admin_headers, auth_headers):
    resp = await client.post("/api/admin/skills", json={
        "slug": "proj-test-skill", "name": "Project Test Skill", "category": "agents",
    }, headers=admin_headers)
    assert resp.status_code == 200

    resp = await client.post("/api/admin/projects", json={
        "slug": "test-project", "title": "Test Project", "overview": "Build a thing",
        "objective": "Demonstrate the skill", "requirements": ["Requirement A", "Requirement B"],
        "evaluation_criteria": [{"criterion": "Requirement A present", "weight": 0.5}, {"criterion": "Requirement B present", "weight": 0.5}],
        "skill_slugs": ["proj-test-skill"],
    }, headers=admin_headers)
    assert resp.status_code == 200
    project_id = resp.json()["id"]

    resp = await client.get("/api/projects", headers=auth_headers)
    assert any(p["id"] == project_id for p in resp.json())

    resp = await client.post(f"/api/projects/{project_id}/submit", json={
        "repo_url": "https://github.com/example/test-project",
        "submission_notes": "Implemented Requirement A and Requirement B with a small FastAPI service.",
    }, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "evaluated"
    assert body["score"] is not None
    assert "feedback" in body["ai_feedback"]
