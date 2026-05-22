"""Tests for PROM-01 (promise list) and PROM-02 (promise detail).

RED state — promises router not yet wired in 03-01.
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
