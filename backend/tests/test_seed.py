import os

import pytest
from sqlalchemy import func, select

from app.database import AsyncSessionLocal
from app.models.elections import Election
from app.models.politicians import Politician
from app.models.promises import Promise


@pytest.mark.skipif(
    os.getenv("ENVIRONMENT") == "ci_no_seed",
    reason="Seed test requires seeded DB",
)
async def test_seed_data_counts():
    """Verify that the seed loader inserts the expected number of rows."""
    async with AsyncSessionLocal() as session:
        pol_count = (
            await session.execute(select(func.count(Politician.id)))
        ).scalar()
        elec_count = (
            await session.execute(select(func.count(Election.id)))
        ).scalar()
        prom_count = (
            await session.execute(select(func.count(Promise.id)))
        ).scalar()

    assert pol_count >= 3, f"Expected >= 3 politicians, got {pol_count}"
    assert elec_count >= 2, f"Expected >= 2 elections, got {elec_count}"
    assert prom_count >= 5, f"Expected >= 5 promises, got {prom_count}"
