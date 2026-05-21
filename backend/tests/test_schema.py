import pytest
from sqlalchemy import text

from app.database import AsyncSessionLocal

EXPECTED_TABLES = {
    "users",
    "parties",
    "politicians",
    "politician_party_memberships",
    "elections",
    "promises",
    "promise_election_links",
    "evidence",
    "votes",
    "vote_history",
    "stats_cache",
    "app_settings",
}


@pytest.mark.asyncio
async def test_tables_exist():
    """
    Verify all 12 schema tables exist in the public schema.
    Requires: alembic upgrade head run against the target DATABASE_URL before executing.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
        )
        actual_tables = {row[0] for row in result.fetchall()}

    missing = EXPECTED_TABLES - actual_tables
    assert not missing, f"Missing tables in database: {missing}"
