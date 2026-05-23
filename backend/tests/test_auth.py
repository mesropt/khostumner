"""
Integration tests for AUTH-01 through AUTH-05.

Requirements coverage:
  AUTH-01 — Registration (test_register_success, test_register_duplicate_email)
  AUTH-02 — Email verification (test_request_verify, test_verify_email)
  AUTH-03 — Password reset (test_forgot_password, test_reset_password)
  AUTH-04 — OAuth login (test_oauth_google_authorize)
  AUTH-05 — Persistent JWT session (test_me_authenticated, test_me_unauthenticated)

Notes:
  - CSRF is seeded via GET /health in the client fixture; tests use csrf_headers()
    to include the x-csrftoken header required by starlette-csrf on POST requests.
  - Email-sending hooks are mocked via monkeypatch to avoid SMTP dependency.
  - test_oauth_google_authorize is skipped when GOOGLE_CLIENT_ID is not configured.
  - test_verify_email and test_reset_password capture tokens via monkeypatched
    UserManager hooks.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.auth import users as auth_users_module
from app.config import settings
from app.main import app


@pytest.fixture
async def client():
    """ASGI test client with CSRF cookie pre-seeded.

    starlette-csrf sets csrftoken cookie on GET requests and validates the
    matching x-csrftoken header on POST requests. The GET /health call seeds
    the cookie; tests must pass the cookie value as x-csrftoken header.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        # Seed the CSRF cookie via a safe GET request
        await ac.get("/health")
        # Store token value for convenience
        ac._test_csrf_token = ac.cookies.get("csrftoken", "")  # type: ignore[attr-defined]
        yield ac


def csrf_headers(client: AsyncClient) -> dict:
    """Return x-csrftoken header dict for POST/PUT/DELETE requests."""
    token = getattr(client, "_test_csrf_token", "")
    return {"x-csrftoken": token}


# ---------------------------------------------------------------------------
# AUTH-01: Registration
# ---------------------------------------------------------------------------


async def test_register_success(client: AsyncClient):
    """POST /api/auth/register with valid email+password+display_name returns 201."""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "TestPass123!",
            "display_name": "Test User",
        },
        headers=csrf_headers(client),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "newuser@example.com"
    assert "id" in body


async def test_register_duplicate_email(client: AsyncClient):
    """POST /api/auth/register with a duplicate email returns 400."""
    payload = {
        "email": "duplicate@example.com",
        "password": "TestPass123!",
        "display_name": "First User",
    }
    # First registration — should succeed
    first = await client.post(
        "/api/auth/register",
        json=payload,
        headers=csrf_headers(client),
    )
    assert first.status_code == 201

    # Second registration with same email — should fail with 400
    second = await client.post(
        "/api/auth/register",
        json=payload,
        headers=csrf_headers(client),
    )
    assert second.status_code == 400


# ---------------------------------------------------------------------------
# AUTH-02: Email verification
# ---------------------------------------------------------------------------


async def test_request_verify(client: AsyncClient, monkeypatch):
    """POST /api/auth/request-verify-token returns 202 (mock SMTP)."""
    # Mock email sending to avoid SMTP dependency
    async def mock_send_verification(self, user, token, request=None):
        pass

    monkeypatch.setattr(
        auth_users_module.UserManager,
        "on_after_request_verify",
        mock_send_verification,
    )

    # Register first
    await client.post(
        "/api/auth/register",
        json={
            "email": "verify_req@example.com",
            "password": "TestPass123!",
            "display_name": "Verify Test",
        },
        headers=csrf_headers(client),
    )

    response = await client.post(
        "/api/auth/request-verify-token",
        json={"email": "verify_req@example.com"},
        headers=csrf_headers(client),
    )
    assert response.status_code == 202


async def test_verify_email(client: AsyncClient, monkeypatch):
    """POST /api/auth/verify with valid token sets is_verified=True (returns 200)."""
    captured_token: list[str] = []

    async def mock_on_after_request_verify(self, user, token, request=None):
        captured_token.append(token)

    monkeypatch.setattr(
        auth_users_module.UserManager,
        "on_after_request_verify",
        mock_on_after_request_verify,
    )

    # Register
    await client.post(
        "/api/auth/register",
        json={
            "email": "verify_email@example.com",
            "password": "TestPass123!",
            "display_name": "Verify User",
        },
        headers=csrf_headers(client),
    )

    # Request verification token
    await client.post(
        "/api/auth/request-verify-token",
        json={"email": "verify_email@example.com"},
        headers=csrf_headers(client),
    )

    assert len(captured_token) == 1, "Expected exactly one verify token to be captured"
    token = captured_token[0]

    # Verify the email
    response = await client.post(
        "/api/auth/verify",
        json={"token": token},
        headers=csrf_headers(client),
    )
    assert response.status_code == 200
    assert response.json()["is_verified"] is True


# ---------------------------------------------------------------------------
# AUTH-03: Password reset
# ---------------------------------------------------------------------------


async def test_forgot_password(client: AsyncClient, monkeypatch):
    """POST /api/auth/forgot-password returns 202 (mock SMTP)."""
    async def mock_send_reset(self, user, token, request=None):
        pass

    monkeypatch.setattr(
        auth_users_module.UserManager,
        "on_after_forgot_password",
        mock_send_reset,
    )

    # Register a user first
    await client.post(
        "/api/auth/register",
        json={
            "email": "forgot@example.com",
            "password": "TestPass123!",
            "display_name": "Forgot User",
        },
        headers=csrf_headers(client),
    )

    response = await client.post(
        "/api/auth/forgot-password",
        json={"email": "forgot@example.com"},
        headers=csrf_headers(client),
    )
    assert response.status_code == 202


async def test_reset_password(client: AsyncClient, monkeypatch):
    """POST /api/auth/reset-password with valid token returns 200."""
    captured_token: list[str] = []

    async def mock_on_after_forgot_password(self, user, token, request=None):
        captured_token.append(token)

    monkeypatch.setattr(
        auth_users_module.UserManager,
        "on_after_forgot_password",
        mock_on_after_forgot_password,
    )

    # Register
    await client.post(
        "/api/auth/register",
        json={
            "email": "reset@example.com",
            "password": "OldPass123!",
            "display_name": "Reset User",
        },
        headers=csrf_headers(client),
    )

    # Request password reset
    await client.post(
        "/api/auth/forgot-password",
        json={"email": "reset@example.com"},
        headers=csrf_headers(client),
    )

    assert len(captured_token) == 1, "Expected exactly one reset token to be captured"
    token = captured_token[0]

    # Reset the password
    response = await client.post(
        "/api/auth/reset-password",
        json={"token": token, "password": "NewPass123!"},
        headers=csrf_headers(client),
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# AUTH-04: OAuth login
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not settings.GOOGLE_CLIENT_ID,
    reason="No Google OAuth credentials configured",
)
async def test_oauth_google_authorize(client: AsyncClient):
    """GET /api/auth/google/authorize returns redirect (302 or 307)."""
    response = await client.get(
        "/api/auth/google/authorize", follow_redirects=False
    )
    assert response.status_code in (302, 303, 307)
    assert "accounts.google.com" in response.headers.get("location", "")


# ---------------------------------------------------------------------------
# AUTH-05: Persistent JWT session
# ---------------------------------------------------------------------------


async def test_me_authenticated(client: AsyncClient):
    """GET /api/users/me with valid access cookie returns 200 with user object."""
    # Register
    await client.post(
        "/api/auth/register",
        json={
            "email": "me_auth@example.com",
            "password": "TestPass123!",
            "display_name": "Me User",
        },
        headers=csrf_headers(client),
    )

    # Login to get access cookie — FastAPI-Users uses OAuth2PasswordRequestForm
    login_res = await client.post(
        "/api/auth/login",
        content="username=me_auth%40example.com&password=TestPass123%21",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            **csrf_headers(client),
        },
    )
    assert login_res.status_code == 200

    # The httpx client stores cookies from login response automatically
    me_response = await client.get("/api/users/me")
    assert me_response.status_code == 200
    assert "email" in me_response.json()


async def test_me_unauthenticated(client: AsyncClient):
    """GET /api/users/me without cookie returns 401."""
    # Use a fresh client with no auth cookies
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as fresh_client:
        response = await fresh_client.get("/api/users/me")
        assert response.status_code == 401
