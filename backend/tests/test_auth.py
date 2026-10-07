import uuid


async def test_register_and_login(client):
    email = f"auth-{uuid.uuid4().hex[:8]}@example.com"
    resp = await client.post("/api/auth/register", json={"email": email, "password": "StrongPass123!", "full_name": "Jane Doe"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

    resp = await client.post("/api/auth/login", json={"email": email, "password": "StrongPass123!"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == email
    assert resp.json()["role"] == "student"


async def test_login_wrong_password(client):
    email = f"auth-{uuid.uuid4().hex[:8]}@example.com"
    await client.post("/api/auth/register", json={"email": email, "password": "StrongPass123!", "full_name": "Jane Doe"})
    resp = await client.post("/api/auth/login", json={"email": email, "password": "WrongPassword"})
    assert resp.status_code == 401


async def test_duplicate_registration_rejected(client):
    email = f"auth-{uuid.uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": "StrongPass123!", "full_name": "Jane Doe"}
    resp = await client.post("/api/auth/register", json=payload)
    assert resp.status_code == 200
    resp = await client.post("/api/auth/register", json=payload)
    assert resp.status_code == 409


async def test_protected_route_requires_token(client):
    resp = await client.get("/api/dashboard")
    assert resp.status_code == 401


async def test_refresh_token_issues_working_access_token(client):
    email = f"auth-{uuid.uuid4().hex[:8]}@example.com"
    tokens = (await client.post("/api/auth/register", json={"email": email, "password": "StrongPass123!", "full_name": "Jane Doe"})).json()

    resp = await client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {resp.json()['access_token']}"})
    assert resp.status_code == 200 and resp.json()["email"] == email


async def test_access_token_cannot_be_used_as_refresh_token(client):
    tokens = (await client.post("/api/auth/register", json={
        "email": f"auth-{uuid.uuid4().hex[:8]}@example.com", "password": "StrongPass123!", "full_name": "Jane Doe",
    })).json()
    resp = await client.post("/api/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert resp.status_code == 401


async def test_expired_access_token_reports_session_expired(client):
    from datetime import datetime, timedelta, timezone

    from jose import jwt

    from app.core.config import get_settings

    settings = get_settings()
    expired = jwt.encode(
        {"sub": str(uuid.uuid4()), "role": "student", "type": "access", "exp": datetime.now(timezone.utc) - timedelta(minutes=5)},
        settings.jwt_secret, algorithm=settings.jwt_algorithm,
    )
    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Session expired"
