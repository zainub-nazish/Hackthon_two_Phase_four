# Quickstart: Backend API & Data Layer

**Feature**: 002-backend-api-data-layer
**Estimated Setup Time**: 15 minutes

## Prerequisites

- Python 3.11+
- Neon PostgreSQL account (free tier works)
- Existing 001-jwt-auth setup complete
- `BETTER_AUTH_SECRET` configured in `.env`

## Step 1: Install Dependencies

```bash
cd backend
pip install sqlmodel asyncpg python-dotenv
```

Or add to `requirements.txt`:
```
sqlmodel>=0.0.16
asyncpg>=0.29.0
python-dotenv>=1.0.0
```

## Step 2: Configure Database Connection

1. Create a Neon database at https://neon.tech
2. Get the pooled connection string (with `-pooler` suffix)
3. Add to `backend/.env`:

```env
# Existing from 001-jwt-auth
BETTER_AUTH_SECRET=your-32-char-secret-here

# New for database
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx-pooler.region.neon.tech/dbname?sslmode=require
```

## Step 3: Create Database Module

Create `backend/database.py`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from backend.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session():
    """Dependency for database sessions."""
    async with async_session() as session:
        yield session


async def init_db():
    """Create database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

## Step 4: Create Task Model

Create `backend/models/database.py`:

```python
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    """Database model for tasks."""

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    owner_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
```

## Step 5: Update Config

Add to `backend/config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings ...

    database_url: str = Field(
        alias="DATABASE_URL",
        description="PostgreSQL connection string"
    )
```

## Step 6: Update Task Routes

Modify `backend/routes/tasks.py` to use database instead of in-memory storage:

```python
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_session
from backend.models.database import Task

@router.get("", response_model=TaskListResponse)
async def list_tasks(
    user_id: str = Path(...),
    current_user: CurrentUser = Depends(verify_user_owns_resource),
    completed: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    query = select(Task).where(Task.owner_id == user_id)
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Get total count
    from sqlalchemy import func
    count_result = await session.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar_one()

    # Get paginated results
    query = query.offset(offset).limit(limit)
    result = await session.execute(query)
    tasks = result.scalars().all()

    return TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
        limit=limit,
        offset=offset,
    )
```

## Step 7: Initialize Database on Startup

Update `backend/main.py`:

```python
from contextlib import asynccontextmanager
from backend.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    await init_db()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    # ... existing config ...
    lifespan=lifespan,
)
```

## Step 8: Run and Test

```bash
# Start server
uvicorn backend.main:app --reload

# Test health check
curl http://localhost:8000/health

# Test with auth token
TOKEN="your-jwt-token"
USER_ID="your-user-id"

# Create a task
curl -X POST "http://localhost:8000/api/v1/users/${USER_ID}/tasks" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Testing persistence"}'

# List tasks
curl "http://localhost:8000/api/v1/users/${USER_ID}/tasks" \
  -H "Authorization: Bearer ${TOKEN}"
```

## Step 9: Verify Persistence

1. Create a task via API
2. Stop the server (Ctrl+C)
3. Start the server again
4. Query for tasks - they should still exist

## Verification Checklist

- [ ] Database connection works (no errors on startup)
- [ ] Tasks persist after server restart
- [ ] CRUD operations work correctly
- [ ] Cross-user access returns 404
- [ ] Filtering by `completed` works
- [ ] Pagination works correctly

## Troubleshooting

### Connection Refused
- Check DATABASE_URL is correct
- Ensure using `-pooler` endpoint for Neon
- Verify SSL mode is `require`

### Authentication Errors
- Verify database credentials
- Check Neon dashboard for connection limits

### Import Errors
- Ensure `sqlmodel` and `asyncpg` are installed
- Check Python version is 3.11+

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement database migrations with Alembic
3. Add comprehensive test coverage
