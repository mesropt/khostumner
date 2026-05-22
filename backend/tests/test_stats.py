"""Tests for DISC-01 (stats endpoint).

RED state — stats router not yet wired in 03-01.
"""

import pytest


@pytest.mark.asyncio
async def test_get_stats(client):
    response = await client.get("/api/stats")
    assert response.status_code == 200
    body = response.json()
    assert "total" in body
    assert "by_status" in body
    for key in ("kept", "broken", "in_progress", "stalled", "not_rated"):
        assert key in body["by_status"]
