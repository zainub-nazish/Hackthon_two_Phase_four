# Data Model: Backend API & Data Layer

**Feature**: 002-backend-api-data-layer
**Date**: 2026-01-12

## Overview

This document defines the database models for persistent task storage using SQLModel ORM with Neon Serverless PostgreSQL.

---

## Core Entities

### 1. Task

The primary entity representing a user's todo item.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Primary key, auto-generated |
| owner_id | string | Yes | User ID from JWT `sub` claim |
| title | string(255) | Yes | Task title, 1-255 characters |
| description | string(2000) | No | Optional task details |
| completed | boolean | Yes | Completion status, default false |
| created_at | datetime(tz) | Yes | Creation timestamp (UTC) |
| updated_at | datetime(tz) | Yes | Last modification timestamp (UTC) |

**Relationships**:
- Task belongs to a User (via owner_id)
- No foreign key constraint - user identity from JWT is authoritative

**Indexes**:
- Primary key on `id`
- Index on `owner_id` for user queries
- Composite index on `(owner_id, completed)` for filtered queries

---

## SQLModel Definition

```python
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    """Database model for task storage."""

    __tablename__ = "tasks"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique task identifier"
    )
    owner_id: str = Field(
        index=True,
        nullable=False,
        description="User ID from JWT sub claim"
    )
    title: str = Field(
        max_length=255,
        nullable=False,
        description="Task title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional task description"
    )
    completed: bool = Field(
        default=False,
        nullable=False,
        description="Task completion status"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Last update timestamp"
    )
```

---

## Pydantic Schemas (API Layer)

These schemas handle request/response validation, separate from the database model.

### TaskCreate (Request)

```python
class TaskCreate(SQLModel):
    """Request body for creating a task."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
```

### TaskUpdate (Request)

```python
class TaskUpdate(SQLModel):
    """Request body for updating a task (partial update)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: Optional[bool] = None
```

### TaskResponse (Response)

```python
class TaskResponse(SQLModel):
    """Response body for a task."""
    id: UUID
    owner_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

### TaskListResponse (Response)

```python
class TaskListResponse(SQLModel):
    """Response body for listing tasks."""
    items: list[TaskResponse]
    total: int
    limit: Optional[int]
    offset: Optional[int]
```

---

## Database Operations

### Create Task

```python
async def create_task(
    session: AsyncSession,
    owner_id: str,
    task_data: TaskCreate
) -> Task:
    task = Task(
        owner_id=owner_id,
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

### Get User Tasks

```python
async def get_user_tasks(
    session: AsyncSession,
    owner_id: str,
    completed: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
) -> tuple[list[Task], int]:
    # Base query filtered by owner
    query = select(Task).where(Task.owner_id == owner_id)

    # Optional completion filter
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Count total before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar_one()

    # Apply pagination
    query = query.offset(offset).limit(limit).order_by(Task.created_at.desc())
    result = await session.execute(query)

    return result.scalars().all(), total
```

### Get Single Task

```python
async def get_task(
    session: AsyncSession,
    owner_id: str,
    task_id: UUID
) -> Optional[Task]:
    query = select(Task).where(
        Task.id == task_id,
        Task.owner_id == owner_id  # ALWAYS filter by owner
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()
```

### Update Task

```python
async def update_task(
    session: AsyncSession,
    task: Task,
    task_data: TaskUpdate
) -> Task:
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    task.updated_at = datetime.now(timezone.utc)

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

### Delete Task

```python
async def delete_task(
    session: AsyncSession,
    task: Task
) -> None:
    await session.delete(task)
    await session.commit()
```

---

## State Transitions

### Task Completion States

```
┌─────────────────┐
│   Incomplete    │
│ (completed=false)│
└────────┬────────┘
         │
         │ Mark complete (PATCH completed=true)
         ▼
┌─────────────────┐
│    Completed    │
│ (completed=true) │
└────────┬────────┘
         │
         │ Mark incomplete (PATCH completed=false)
         ▼
┌─────────────────┐
│   Incomplete    │
└─────────────────┘
```

---

## Validation Rules

### Title Validation

| Rule | Constraint | Error |
|------|------------|-------|
| Required | Cannot be null/empty | 422 Validation Error |
| Min Length | >= 1 character | 422 Validation Error |
| Max Length | <= 255 characters | 422 Validation Error |

### Description Validation

| Rule | Constraint | Error |
|------|------------|-------|
| Optional | Can be null | N/A |
| Max Length | <= 2000 characters | 422 Validation Error |

### Ownership Validation

| Rule | Constraint | Error |
|------|------------|-------|
| Path Match | JWT.sub == path.user_id | 404 Not Found |
| Resource Owner | Task.owner_id == JWT.sub | 404 Not Found |

---

## Database Schema (SQL)

```sql
-- Generated by SQLModel, but shown for reference
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id VARCHAR NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_tasks_owner_id ON tasks(owner_id);
CREATE INDEX idx_tasks_owner_completed ON tasks(owner_id, completed);
CREATE INDEX idx_tasks_owner_created ON tasks(owner_id, created_at DESC);
```

---

## Security Considerations

1. **Owner Filtering**: Every database query MUST include `owner_id` filter
2. **No Direct ID Access**: Never query by `task_id` alone without `owner_id`
3. **UUID IDs**: Non-sequential IDs prevent enumeration attacks
4. **Input Validation**: SQLModel/Pydantic validates all inputs before DB operations
5. **SQL Injection**: ORM parameterization prevents injection attacks
