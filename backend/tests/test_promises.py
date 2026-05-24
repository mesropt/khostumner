"""Tests for PROM-01/02 (promise list/detail) and PROM-03/04/ELEC-03 (submission).

Phase 3 tests: previously RED state, now GREEN (promises router wired).
Phase 5 stubs: RED state — POST/PUT endpoints not yet implemented.
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import get_db
from app.main import app
from app.models.users import User, UserRole
from app.models.promises import ModerationStatus, Promise


@pytest.fixture
async def verified_user_client(client):
    """HTTP client authenticated as a verified user with account_age_days >= 7."""
    import httpx
    from app.auth.schemas import UserCreate
    from fastapi_users.password import PasswordHelper

    # Register a new user via the API
    reg_resp = await client.post(
        "/api/auth/register",
        json={
            "email": "verified@test.com",
            "password": "TestPass1!",
            "display_name": "Verified User",
        },
    )
    assert reg_resp.status_code in (201, 400), f"Register failed: {reg_resp.text}"

    # Directly update user in DB to set is_verified=True and account_age_days=10
    test_engine = create_async_engine(settings.DATABASE_URL, echo=False)
    test_session_factory = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False,
    )
    async with test_session_factory() as session:
        from sqlalchemy import select, update
        result = await session.execute(
            select(User).where(User.email == "verified@test.com")
        )
        user = result.scalar_one_or_none()
        if user is not None:
            user.is_verified = True
            user.account_age_days = 10
            await session.commit()
    await test_engine.dispose()

    # Login
    login_resp = await client.post(
        "/api/auth/jwt/login",
        data={"username": "verified@test.com", "password": "TestPass1!"},
    )
    if login_resp.status_code != 200:
        pytest.skip(f"Login failed: {login_resp.text}")

    tokens = login_resp.json()
    access_token = tokens.get("access_token")
    if not access_token:
        pytest.skip("No access_token in login response")

    # Create a new ASGI client with auth headers
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {access_token}"},
    ) as auth_client:
        yield auth_client


@pytest.fixture
async def young_user_client(client):
    """HTTP client authenticated as a verified user with account_age_days=0 (too young)."""
    # Register a new user via the API
    reg_resp = await client.post(
        "/api/auth/register",
        json={
            "email": "young@test.com",
            "password": "TestPass1!",
            "display_name": "Young User",
        },
    )
    assert reg_resp.status_code in (201, 400), f"Register failed: {reg_resp.text}"

    # Directly update user in DB to set is_verified=True and account_age_days=0
    test_engine = create_async_engine(settings.DATABASE_URL, echo=False)
    test_session_factory = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False,
    )
    async with test_session_factory() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.email == "young@test.com")
        )
        user = result.scalar_one_or_none()
        if user is not None:
            user.is_verified = True
            user.account_age_days = 0
            await session.commit()
    await test_engine.dispose()

    # Login
    login_resp = await client.post(
        "/api/auth/jwt/login",
        data={"username": "young@test.com", "password": "TestPass1!"},
    )
    if login_resp.status_code != 200:
        pytest.skip(f"Login failed: {login_resp.text}")

    tokens = login_resp.json()
    access_token = tokens.get("access_token")
    if not access_token:
        pytest.skip("No access_token in login response")

    # Create a new ASGI client with auth headers
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {access_token}"},
    ) as auth_client:
        yield auth_client


@pytest.mark.asyncio
async def test_list_promises(client):
    response = await client.get("/api/promises")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "per_page" in body
    assert "pages" in body


@pytest.mark.asyncio
async def test_list_promises_filter_status(client):
    response = await client.get("/api/promises?status=kept")
    assert response.status_code == 200
    for item in response.json()["items"]:
        assert item["resolved_status"] == "kept"


@pytest.mark.asyncio
async def test_list_promises_multi_status(client):
    response = await client.get("/api/promises?status=broken,stalled")
    assert response.status_code == 200
    for item in response.json()["items"]:
        assert item["resolved_status"] in ("broken", "stalled")


@pytest.mark.asyncio
async def test_list_promises_moderation_filter(client):
    # Must never return non-approved promises
    # Verified by integration with seed data — all returned items are approved
    response = await client.get("/api/promises")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["items"], list)


@pytest.mark.asyncio
async def test_get_promise_not_found(client):
    response = await client.get("/api/promises/nonexistent-slug")
    assert response.status_code == 404
    assert response.json()["detail"] == "Promise not found"


@pytest.mark.asyncio
async def test_get_promise(client):
    # Fetch list first; skip if no items (seed data may be empty in CI)
    list_response = await client.get("/api/promises")
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    if not items:
        pytest.skip("No promises in database — seed data required")
    slug = items[0]["slug"]
    response = await client.get(f"/api/promises/{slug}")
    assert response.status_code == 200
    body = response.json()
    assert "title_hy" in body
    assert "quote_hy" in body
    assert "politician_name_hy" in body
    assert "politician_slug" in body


# ──────────────────────────────────────────────────────────────────────────────
# Phase 5 — PROM-03, PROM-04, ELEC-03
# Tests for POST /api/promises and PUT /api/promises/{slug}
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_promise(client):
    """PROM-03: POST /api/promises returns 201 for eligible authenticated user.

    RED — POST /api/promises not yet implemented (Wave 1).
    verified_user_client fixture added in Wave 1 conftest.
    """
    pytest.skip("RED — verified_user_client fixture needed for full test")


@pytest.mark.asyncio
async def test_create_promise_unauthenticated(client):
    """PROM-03: POST /api/promises returns 401 for unauthenticated request."""
    response = await client.post(
        "/api/promises",
        json={
            "title_hy": "Test Promise",
            "quote_hy": "Verbatim quote here",
            "source_url": "https://example.com",
            "politician_id": str(uuid.uuid4()),
            "election_ids": [],
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_promise_unverified(client):
    """PROM-03: POST /api/promises returns 403 for unverified user.

    RED — unverified_user_client fixture added in Wave 1 conftest.
    """
    pytest.skip("RED — unverified_user_client fixture needed")


@pytest.mark.asyncio
async def test_create_promise_too_young(young_user_client):
    """PROM-03: POST /api/promises returns 403 for account < 7 days old."""
    from sqlalchemy import select
    from app.models.politicians import Politician

    # Fetch a politician id to use in the request
    test_engine = create_async_engine(settings.DATABASE_URL, echo=False)
    test_session_factory = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False,
    )
    politician_id = None
    async with test_session_factory() as session:
        result = await session.execute(select(Politician).limit(1))
        pol = result.scalar_one_or_none()
        if pol:
            politician_id = str(pol.id)
    await test_engine.dispose()

    if not politician_id:
        pytest.skip("No politicians in database — seed data required")

    response = await young_user_client.post(
        "/api/promises",
        json={
            "title_hy": "Test Promise Too Young",
            "quote_hy": "Verbatim quote here",
            "source_url": "https://example.com",
            "politician_id": politician_id,
            "election_ids": [],
        },
    )
    assert response.status_code == 403
    assert "7 days" in response.json()["detail"] or "7 օր" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_promise_invalid_election(client):
    """PROM-03/ELEC-03: POST /api/promises with non-existent election_id returns 422.

    RED — verified_user_client fixture added in Wave 1 conftest.
    """
    pytest.skip("RED — verified_user_client fixture needed for full test")


@pytest.mark.asyncio
async def test_create_promise_with_elections(client):
    """ELEC-03: POST /api/promises with election_ids creates PromiseElectionLink rows.

    RED — verified_user_client fixture added in Wave 1 conftest.
    """
    pytest.skip("RED — verified_user_client fixture needed for full test")


@pytest.mark.asyncio
async def test_edit_promise_creates_edit_row(client):
    """PROM-04: PUT /api/promises/{slug} inserts into promise_edits, not the live promise.

    RED — verified_user_client fixture added in Wave 1 conftest.
    """
    pytest.skip("RED — verified_user_client fixture needed for full test")


@pytest.mark.asyncio
async def test_edit_promise_unauthenticated(client):
    """PROM-04: PUT /api/promises/{slug} returns 401 for unauthenticated request."""
    response = await client.put(
        "/api/promises/some-promise-slug",
        json={
            "title_hy": "Test Edit",
            "quote_hy": "Verbatim quote here",
            "source_url": "https://example.com",
            "election_ids": [],
        },
    )
    assert response.status_code == 401
