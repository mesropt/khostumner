import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import get_db
from app.main import app


@pytest.fixture
async def client():
    """Create a test client with a fresh database engine for each test.

    Each test gets its own async engine + session factory to avoid connection
    contamination between tests (asyncpg per-connection state isolation).
    """
    test_engine = create_async_engine(settings.DATABASE_URL, echo=False)
    test_session_factory = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False,
    )

    async def override_get_db():
        async with test_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac
    finally:
        app.dependency_overrides.pop(get_db, None)
        await test_engine.dispose()