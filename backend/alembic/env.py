"""Alembic async migration environment."""
import asyncio
from logging.config import fileConfig

from alembic import context

# Reuse the app's own engine/URL/SSL resolution instead of duplicating it via
# alembic.ini's static sqlalchemy.url — that file has no way to see the real
# DATABASE_URL env var, so migrations were silently trying to connect to the
# local placeholder instead of production.
from app.core.database import Base, get_engine
from app.core.config import settings
from app.models.models import *  # noqa: ensure all models are loaded

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = get_engine()
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
