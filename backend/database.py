"""Database connection and session management for async PostgreSQL."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel

from backend.config import settings


def _get_engine():
    """Create async database engine with connection pooling."""
    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured. "
            "Set it in environment variables or .env file."
        )

    # SQLite (used for testing) doesn't support pool_size/max_overflow
    is_sqlite = settings.database_url.startswith("sqlite")

    engine_args = {
        "echo": settings.debug,
    }

    if not is_sqlite:
        # PostgreSQL connection pooling options
        engine_args.update({
            "pool_pre_ping": True,
            "pool_size": 5,
            "max_overflow": 10,
        })

    return create_async_engine(settings.database_url, **engine_args)


# Lazy engine creation - only create when database_url is available
_engine = None


def get_engine():
    """Get or create the async database engine."""
    global _engine
    if _engine is None:
        _engine = _get_engine()
    return _engine


def get_async_session_maker():
    """Get async session factory."""
    return sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Yields an async session and ensures proper cleanup.
    Handles connection errors with appropriate error responses.
    """
    async_session = get_async_session_maker()
    async with async_session() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise RuntimeError(f"Database error: {str(e)}") from e


async def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in SQLModel metadata.
    Should be called during application startup.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.

    Should be called during application shutdown.
    """
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
