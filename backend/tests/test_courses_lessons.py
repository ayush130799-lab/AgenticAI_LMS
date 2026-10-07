async def test_list_and_get_course(client, seeded_course):
    resp = await client.get("/api/courses")
    assert resp.status_code == 200
    slugs = [c["slug"] for c in resp.json()]
    assert any("test-course" in s for s in slugs)

    resp = await client.get(f"/api/courses/{seeded_course['course_id']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Test Course"
    assert len(body["modules"]) == 1
    assert len(body["modules"][0]["lessons"]) == 1


async def test_lesson_detail_and_complete(client, seeded_course, auth_headers):
    lesson_id = seeded_course["lesson_id"]
    resp = await client.get(f"/api/lessons/{lesson_id}")
    assert resp.status_code == 200
    assert resp.json()["progress_status"] is None  # no auth on this call

    resp = await client.get(f"/api/lessons/{lesson_id}", headers=auth_headers)
    assert resp.json()["progress_status"] == "not_started"

    resp = await client.post(f"/api/lessons/{lesson_id}/complete", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["progress_status"] == "completed"

    resp = await client.get(f"/api/lessons/{lesson_id}", headers=auth_headers)
    assert resp.json()["progress_status"] == "completed"


async def test_progress_reflects_completion(client, seeded_course, auth_headers):
    await client.post(f"/api/lessons/{seeded_course['lesson_id']}/complete", headers=auth_headers)
    resp = await client.get("/api/students/me/progress", headers=auth_headers)
    assert resp.status_code == 200
    course_row = next(c for c in resp.json()["courses"] if c["course_id"] == str(seeded_course["course_id"]))
    assert course_row["progress_percent"] == 100.0


async def test_bookmark_and_notes(client, seeded_course, auth_headers):
    lesson_id = seeded_course["lesson_id"]
    resp = await client.post(f"/api/lessons/{lesson_id}/bookmark", headers=auth_headers)
    assert resp.json()["bookmarked"] is True
    resp = await client.post(f"/api/lessons/{lesson_id}/bookmark", headers=auth_headers)
    assert resp.json()["bookmarked"] is False

    resp = await client.post(f"/api/lessons/{lesson_id}/notes", json={"content": "remember this"}, headers=auth_headers)
    assert resp.status_code == 200
    resp = await client.get(f"/api/lessons/{lesson_id}/notes", headers=auth_headers)
    assert len(resp.json()) == 1
