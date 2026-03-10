from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.logging_config import logger

engine = create_async_engine(settings.database_url_async, pool_pre_ping=True, future=True)
logger.info("[db] engine created host={} db={}", settings.postgres_host_effective, settings.postgres_db)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield an async database session, closing it on exit."""
    async with AsyncSessionLocal() as session:
        yield session
