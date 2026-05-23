"""
RED test stubs for AUTH-01 through AUTH-05.

All tests are marked xfail(strict=False) — they are expected to fail until
Phase 4 auth implementation (plans 04-02 and 04-03) is complete.

Requirements coverage:
  AUTH-01 — Registration (test_register_success, test_register_duplicate_email)
  AUTH-02 — Email verification (test_request_verify, test_verify_email)
  AUTH-03 — Password reset (test_forgot_password, test_reset_password)
  AUTH-04 — OAuth login (test_oauth_google_authorize)
  AUTH-05 — Persistent JWT session (test_me_authenticated, test_me_unauthenticated)
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# AUTH-01: Registration
# ---------------------------------------------------------------------------


@pytest.mark.xfail(reason="auth not implemented yet", strict=False)
async def test_register_success(client: AsyncClient):
    """POST /api/auth/register with valid email+password+display_name returns 201."""
    raise NotImplementedError("implement in 04-02/04-03")


@pytest.mark.xfail(reason="auth not implemented yet", strict=False)
async def test_register_duplicate_email(client: AsyncClient):
    """POST /api/auth/register with a duplicate email returns 400."""
    raise NotImplementedError("implement in 04-02/04-03")


# ---------------------------------------------------------------------------
# AUTH-02: Email verification
# ---------------------------------------------------------------------------


@pytest.mark.xfail(reason="auth not implemented yet", strict=False)
async def test_request_verify(client: AsyncClient):
    """POST /api/auth/request-verify-token returns 202 (mock SMTP)."""
    raise NotImplementedError("implement in 04-02/04-03")


@pytest.mark.xfail(reason="auth not implemented yet", strict=False)
async def test_verify_email(client: AsyncClient):
    """POST /api/auth/verify with valid token sets is_verified=True (returns 200)."""
    raise NotImplementedError("implement in 04-02/04-03")


# ---------------------------------------------------------------------------
# AUTH-03: Password reset
# ---------------------------------------------------------------------------


@pytest.mark.xfail(reason="auth not implemented yet", strict=False)
async def test_forgot_password(client: AsyncClient):
    """POST /api/auth/forgot-password returns 202 (mock SMTP)."""
    raise NotImplementedError("implement in 04-02/04-03")


@pytest.mark.xfail(reason="auth not implemented yet", strict=False)
async def test_reset_password(client: AsyncClient):
    """POST /api/auth/reset-password with valid token returns 200."""
    raise NotImplementedError("implement in 04-02/04-03")


# ---------------------------------------------------------------------------
# AUTH-04: OAuth login
# ---------------------------------------------------------------------------


@pytest.mark.xfail(reason="auth not implemented yet", strict=False)
async def test_oauth_google_authorize(client: AsyncClient):
    """GET /api/auth/google/authorize returns redirect (302 or 307)."""
    raise NotImplementedError("implement in 04-02/04-03")


# ---------------------------------------------------------------------------
# AUTH-05: Persistent JWT session
# ---------------------------------------------------------------------------


@pytest.mark.xfail(reason="auth not implemented yet", strict=False)
async def test_me_authenticated(client: AsyncClient):
    """GET /api/users/me with valid access cookie returns 200 with user object."""
    raise NotImplementedError("implement in 04-02/04-03")


@pytest.mark.xfail(reason="auth not implemented yet", strict=False)
async def test_me_unauthenticated(client: AsyncClient):
    """GET /api/users/me without cookie returns 401."""
    raise NotImplementedError("implement in 04-02/04-03")
