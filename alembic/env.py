from __future__ import annotations

import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Обеспечиваем импорт приложения
sys.path.insert(0, os.getcwd())
from app.core.config import settings  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.models import log as _log  # noqa: F401,E402  # ensure models are imported
from app.models import automation_run as _automation_run  # noqa: F401,E402

config = context.config

if config.config_file_name and os.path.exists(config.config_file_name):
    try:
        fileConfig(config.config_file_name)  # может отсутствовать секция форматтеров — игнорируем
    except Exception:
        pass

# URL БД из настроек
config.set_main_option("sqlalchemy.url", settings.database_url_async)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    async def _run() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

    try:
        asyncio.run(_run())
    finally:
        try:
            connectable.sync_engine.dispose()
        except Exception:
            pass


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
