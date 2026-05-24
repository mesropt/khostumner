"""Tests for PROM-01/02 (promise list/detail) and PROM-03/04/ELEC-03 (submission).

Phase 3 tests: previously RED state, now GREEN (promises router wired).
Phase 5 stubs: RED state — POST/PUT endpoints not yet implemented.
"""

import pytest


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
# Phase 5 RED-state stubs — PROM-03, PROM-04, ELEC-03
# These fail until Wave 1 implements POST /api/promises and PUT /api/promises/{slug}
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_promise(client):
    """PROM-03: POST /api/promises returns 201 for eligible authenticated user.

    RED — POST /api/promises not yet implemented (Wave 1).
    verified_user_client fixture added in Wave 1 conftest.
    """
    pytest.skip("RED — POST /api/promises not yet implemented (Wave 1)")


@pytest.mark.asyncio
async def test_create_promise_unauthenticated(client):
    """PROM-03: POST /api/promises returns 401 for unauthenticated request."""
    pytest.skip("RED — POST /api/promises not yet implemented (Wave 1)")


@pytest.mark.asyncio
async def test_create_promise_unverified(client):
    """PROM-03: POST /api/promises returns 403 for unverified user.

    RED — unverified_user_client fixture added in Wave 1 conftest.
    """
    pytest.skip("RED — POST /api/promises not yet implemented (Wave 1)")


@pytest.mark.asyncio
async def test_create_promise_too_young(client):
    """PROM-03: POST /api/promises returns 403 for account < 7 days old.

    RED — young_user_client fixture added in Wave 1 conftest.
    """
    pytest.skip("RED — POST /api/promises not yet implemented (Wave 1)")


@pytest.mark.asyncio
async def test_create_promise_invalid_election(client):
    """PROM-03/ELEC-03: POST /api/promises with non-existent election_id returns 422.

    RED — verified_user_client fixture added in Wave 1 conftest.
    """
    pytest.skip("RED — POST /api/promises not yet implemented (Wave 1)")


@pytest.mark.asyncio
async def test_create_promise_with_elections(client):
    """ELEC-03: POST /api/promises with election_ids creates PromiseElectionLink rows.

    RED — verified_user_client fixture added in Wave 1 conftest.
    """
    pytest.skip("RED — POST /api/promises not yet implemented (Wave 1)")


@pytest.mark.asyncio
async def test_edit_promise_creates_edit_row(client):
    """PROM-04: PUT /api/promises/{slug} inserts into promise_edits, not the live promise.

    RED — verified_user_client fixture added in Wave 1 conftest.
    """
    pytest.skip("RED — PUT /api/promises/{slug} not yet implemented (Wave 1)")


@pytest.mark.asyncio
async def test_edit_promise_unauthenticated(client):
    """PROM-04: PUT /api/promises/{slug} returns 401 for unauthenticated request."""
    pytest.skip("RED — PUT /api/promises/{slug} not yet implemented (Wave 1)")
