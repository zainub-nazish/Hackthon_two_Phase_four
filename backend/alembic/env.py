# ============================================================
# Task ID  : T007
# Title    : Alembic migration environment
# Spec Ref : speckit.plan → Section 7A: Prerequisites
# Plan Ref : speckit.plan → Section 5.1: State Store Config
# ============================================================
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# Import all models so Alembic can detect them
from backend.models.database import Task, Conversation, Message  # noqa: F401

# Alembic Config object — provides access to alembic.ini values
config = context.config

# Override sqlalchemy.url with DATABASE_URL env var (never hardcode)
db_url = os.environ.get("DATABASE_URL", "")
# Alembic needs synchronous URL for migrations — convert asyncpg → psycopg2
sync_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://") \
                 .replace("sqlite+aiosqlite://", "sqlite:///")
config.set_main_option("sqlalchemy.url", sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no DB connection needed)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (with live DB connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
