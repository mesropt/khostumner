"""Tests for DISC-05 (OG endpoint).

RED state — og router not yet wired in 03-01.
"""

import pytest


@pytest.mark.asyncio
async def test_og_promise_not_found(client):
    response = await client.get("/api/og/promises/nonexistent-slug")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_og_promise_returns_html(client):
    # Fetch list first to get a real slug; skip if no items
    list_response = await client.get("/api/promises")
    if list_response.status_code != 200:
        pytest.skip("Promises endpoint not available — router not yet wired")
    items = list_response.json().get("items", [])
    if not items:
        pytest.skip("No promises in database — seed data required")
    slug = items[0]["slug"]
    response = await client.get(f"/api/og/promises/{slug}")
    assert response.status_code == 200
    assert "og:title" in response.text
    assert "og:description" in response.text
