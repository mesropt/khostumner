"""Wave 0 test stubs for ELEC-01, ELEC-02.

These tests fail until plan 02-04 creates the elections router.
RED state is expected — these stubs define the contract.
"""

import pytest


@pytest.mark.asyncio
async def test_list_elections(client):
    response = await client.get("/api/elections")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body


@pytest.mark.asyncio
async def test_get_election(client):
    response = await client.get("/api/elections/nonexistent-slug")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_election_promises(client):
    response = await client.get("/api/elections/nonexistent-slug/promises")
    assert response.status_code == 404
