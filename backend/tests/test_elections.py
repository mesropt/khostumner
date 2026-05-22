"""Tests for ELEC-01 (elections list) and ELEC-02 (election detail + promises).

GREEN state — elections router is implemented in plan 02-04.
"""

import pytest


@pytest.mark.asyncio
async def test_list_elections(client):
    response = await client.get("/api/elections")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "per_page" in body
    assert "pages" in body
    # If there are any items they must have promise_count
    for item in body["items"]:
        assert "promise_count" in item


@pytest.mark.asyncio
async def test_get_election_not_found(client):
    response = await client.get("/api/elections/nonexistent-slug")
    assert response.status_code == 404
    assert response.json()["detail"] == "Election not found"


@pytest.mark.asyncio
async def test_election_promises_not_found(client):
    response = await client.get("/api/elections/nonexistent-slug/promises")
    assert response.status_code == 404
    assert response.json()["detail"] == "Election not found"
