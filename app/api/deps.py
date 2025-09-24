from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session


# Алиас для зависимостей FastAPI
async def get_db_session() -> AsyncSession:
    async for s in get_session():
        yield s
