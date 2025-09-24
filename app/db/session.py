from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.logging_config import logger

# Async SQLAlchemy 2.0 engine & sessionmaker
engine = create_async_engine(settings.database_url_async, pool_pre_ping=True, future=True)
logger.info("[db] async engine created (host=%s db=%s)", settings.postgres_host_effective, settings.postgres_db)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_session() -> AsyncSession:
    logger.debug("[db] acquiring async session")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            logger.debug("[db] session closed")
