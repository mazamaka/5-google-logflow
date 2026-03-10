from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency for database session."""
    async for s in get_session():
        yield s
