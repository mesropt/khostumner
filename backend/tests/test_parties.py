"""Wave 0 test stubs for POLS-03.

These tests fail until plan 02-03 creates the parties router.
RED state is expected — these stubs define the contract.
"""

import pytest


@pytest.mark.asyncio
async def test_list_parties(client):
    response = await client.get("/api/parties")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_party(client):
    response = await client.get("/api/parties/nonexistent-slug")
    assert response.status_code == 404
