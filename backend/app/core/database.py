"""Database connection and session management."""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# Lazy engine creation — tests can override _engine before first use
_engine = None
_session_factory = None


def get_engine():
    global _engine
    if _engine is None:
        url = settings.DATABASE_URL
        if url.startswith("sqlite"):
            _engine = create_async_engine(
                url,
                echo=settings.DEBUG,
            )
        else:
            _engine = create_async_engine(
                url,
                echo=settings.DEBUG,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
    return _engine


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


def override_engine(engine):
    """Override engine for testing."""
    global _engine, _session_factory
    _engine = engine
    _session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


async def get_db() -> AsyncSession:  # type: ignore[misc]
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
