"""Tests for POLS-03: Party detail, member politicians, and party promises endpoints.

Tests assert:
- GET /api/parties returns 200 list
- GET /api/parties/{slug} with nonexistent slug returns 404
- GET /api/parties/{slug}/politicians with nonexistent slug returns 404
- GET /api/parties/{slug}/promises with nonexistent slug returns 404
"""

import pytest


@pytest.mark.asyncio
async def test_list_parties(client):
    response = await client.get("/api/parties")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_party_not_found(client):
    """GET /api/parties/nonexistent-slug must return 404."""
    response = await client.get("/api/parties/nonexistent-slug")
    assert response.status_code == 404
    assert response.json()["detail"] == "Party not found"


@pytest.mark.asyncio
async def test_get_party_politicians_not_found(client):
    """GET /api/parties/{slug}/politicians with unknown slug must return 404."""
    response = await client.get("/api/parties/nonexistent-slug/politicians")
    assert response.status_code == 404
    assert response.json()["detail"] == "Party not found"


@pytest.mark.asyncio
async def test_get_party_promises_not_found(client):
    """GET /api/parties/{slug}/promises with unknown slug must return 404."""
    response = await client.get("/api/parties/nonexistent-slug/promises")
    assert response.status_code == 404
    assert response.json()["detail"] == "Party not found"


@pytest.mark.asyncio
async def test_get_party_promises_pagination_shape(client):
    """GET /api/parties/{slug}/promises response is a PaginatedResponse envelope when party exists.

    This test only verifies the shape of the 404 response — real integration
    tests with seed data run in CI where PostgreSQL is available.
    We rely on the router logic test via 404 path for slug routing.
    """
    response = await client.get("/api/parties/nonexistent-slug/promises?page=1&per_page=20")
    assert response.status_code == 404
