# Research: Backend API & Data Layer

**Feature**: 002-backend-api-data-layer
**Date**: 2026-01-12
**Status**: Complete

## Executive Summary

This research consolidates findings on implementing persistent data storage with SQLModel ORM and Neon Serverless PostgreSQL, integrating with the existing FastAPI backend from 001-jwt-auth.

---

## Decision 1: ORM Choice - SQLModel

**Decision**: Use SQLModel for database modeling and queries

**Rationale**:
- Built by the same author as FastAPI (Sebastián Ramírez)
- Combines SQLAlchemy with Pydantic for seamless validation
- Single model definition serves as both database schema AND request/response schema
- Native async support with SQLAlchemy 2.0
- Type hints throughout, excellent IDE support
- Reduces boilerplate vs. separate SQLAlchemy + Pydantic models

**Alternatives Considered**:
| Option | Pros | Cons | When to Use |
|--------|------|------|-------------|
| SQLModel | FastAPI native, Pydantic integration, type-safe | Younger ecosystem | FastAPI projects (chosen) |
| SQLAlchemy + Pydantic | Mature, well-documented | More boilerplate, dual models | Complex enterprise apps |
| Raw SQL | Maximum control, performance | No type safety, SQL injection risk | Performance-critical queries |
| Prisma (Python) | Modern DX | Less mature Python support | TypeScript-first projects |

**Installation**: `pip install sqlmodel`

---

## Decision 2: Database Connection - Neon Serverless PostgreSQL

**Decision**: Use Neon with connection pooling via `asyncpg`

**Rationale**:
- Serverless PostgreSQL - scales to zero, pay-per-use
- Built-in connection pooling handles serverless cold starts
- PostgreSQL compatibility - standard SQL, ACID guarantees
- Branching support for development workflows
- Free tier sufficient for hackathon/MVP

**Connection Configuration**:
```python
# Use pooled connection string for serverless
DATABASE_URL = "postgresql+asyncpg://user:pass@ep-xxx.region.neon.tech/dbname?sslmode=require"
```

**Key Considerations**:
- Always use pooled connection endpoint (`-pooler` suffix)
- SSL required for Neon connections
- Connection timeout handling for cold starts
- Max connections limit awareness (free tier: 100)

---

## Decision 3: Database Schema Strategy

**Decision**: Use SQLModel's `create_all()` for initial schema, with Alembic for future migrations

**Rationale**:
- Simple initial setup - `SQLModel.metadata.create_all()` creates tables
- Alembic provides migration path when schema evolves
- Auto-generates migrations from model changes
- Rollback capability for production safety

**Schema Design**:
```sql
-- Tasks table (SQLModel will generate this)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id VARCHAR NOT NULL,  -- References user from JWT sub claim
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index for efficient user queries
CREATE INDEX idx_tasks_owner_id ON tasks(owner_id);
CREATE INDEX idx_tasks_owner_completed ON tasks(owner_id, completed);
```

**Note**: No foreign key to users table - user identity comes from JWT `sub` claim via auth layer.

---

## Decision 4: Async Database Operations

**Decision**: Use async SQLModel with `asyncpg` driver

**Rationale**:
- FastAPI is async-native - blocking DB calls waste resources
- `asyncpg` is the fastest PostgreSQL driver for Python
- SQLAlchemy 2.0 (underlying SQLModel) has full async support
- Connection pooling handled at driver level

**Implementation Pattern**:
```python
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with async_session() as session:
        yield session
```

---

## Decision 5: Endpoint Structure

**Decision**: Nested resource URLs under user context

**Rationale**:
- Maintains consistency with existing 001-jwt-auth endpoints
- URL structure: `/api/v1/users/{user_id}/tasks`
- Clear ownership semantics in URL
- IDOR prevention via path parameter validation

**Endpoint Design**:
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/users/{user_id}/tasks` | List user's tasks |
| POST | `/api/v1/users/{user_id}/tasks` | Create task |
| GET | `/api/v1/users/{user_id}/tasks/{task_id}` | Get single task |
| PATCH | `/api/v1/users/{user_id}/tasks/{task_id}` | Update task |
| DELETE | `/api/v1/users/{user_id}/tasks/{task_id}` | Delete task |

**Note**: Already implemented in 001-jwt-auth with in-memory storage. This feature replaces with persistent DB.

---

## Decision 6: Error Handling Strategy

**Decision**: Consistent error responses with appropriate HTTP status codes

**Error Taxonomy**:
| Scenario | Status | Response Body |
|----------|--------|---------------|
| Validation error | 422 | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| Not found / Unauthorized access | 404 | `{"detail": "Not found"}` |
| Authentication missing | 401 | `{"detail": "Not authenticated"}` |
| Database error | 503 | `{"detail": "Service temporarily unavailable"}` |
| Server error | 500 | `{"detail": "Internal server error"}` |

**IDOR Prevention**: Always return 404 (not 403) when user attempts to access another user's resource.

---

## Decision 7: Query Filtering Implementation

**Decision**: Always filter by owner_id at database query level

**Rationale**:
- Defense in depth - auth layer validates, DB layer enforces
- No risk of accidentally returning other users' data
- Index on owner_id ensures efficient queries

**Implementation Pattern**:
```python
# Every query MUST include owner_id filter
async def get_user_tasks(session: AsyncSession, owner_id: str) -> list[Task]:
    statement = select(Task).where(Task.owner_id == owner_id)
    result = await session.execute(statement)
    return result.scalars().all()
```

---

## Decision 8: Timestamp Management

**Decision**: Use SQLModel/SQLAlchemy defaults with timezone-aware timestamps

**Implementation**:
```python
from datetime import datetime, timezone
from sqlmodel import Field

class Task(SQLModel, table=True):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

**Update Pattern**: Explicitly set `updated_at` on every PATCH operation.

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| Web Framework | FastAPI | 0.109+ |
| ORM | SQLModel | 0.0.16+ |
| Database Driver | asyncpg | 0.29+ |
| Database | Neon PostgreSQL | Serverless |
| Migrations | Alembic | 1.13+ (future) |
| Testing | pytest + pytest-asyncio | Latest |
| Python | Python | 3.11+ |

---

## Integration with Existing Code

The 001-jwt-auth feature already implements:
- JWT authentication via `get_current_user` dependency
- User ownership verification via `verify_user_owns_resource`
- Task routes with in-memory storage (`backend/routes/tasks.py`)
- Pydantic models for Task (`backend/models/schemas.py`)

This feature will:
1. Add SQLModel database models (new file: `backend/models/database.py`)
2. Add database session dependency (new file: `backend/database.py`)
3. Replace in-memory storage in `backend/routes/tasks.py` with DB queries
4. Preserve existing route structure and auth dependencies

---

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| SQLModel vs SQLAlchemy | SQLModel (FastAPI-native) |
| Sync vs Async DB | Async with asyncpg |
| Schema migrations | create_all() initially, Alembic later |
| User table needed? | No - user_id from JWT is sufficient |
| Connection pooling | Neon built-in pooler |
| Soft delete? | No - hard delete per spec |

---

## References

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Neon PostgreSQL Docs](https://neon.tech/docs)
- [FastAPI + SQLModel Integration](https://sqlmodel.tiangolo.com/tutorial/fastapi/)
- [asyncpg Driver](https://magicstack.github.io/asyncpg/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
