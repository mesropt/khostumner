"""Wave 0 test stubs for POLS-01, POLS-02.

These tests fail until plan 02-02 creates the politicians router.
RED state is expected — these stubs define the contract.
"""

import pytest


@pytest.mark.asyncio
async def test_list_politicians(client):
    response = await client.get("/api/politicians")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "per_page" in body
    assert "pages" in body


@pytest.mark.asyncio
async def test_filter_by_party(client):
    response = await client.get(
        "/api/politicians?party=00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_filter_by_level(client):
    response = await client.get("/api/politicians?level=national")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_politician_by_slug(client):
    response = await client.get("/api/politicians/does-not-exist-yet")
    assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_politician_not_found(client):
    response = await client.get("/api/politicians/zzz-nonexistent")
    assert response.status_code == 404
