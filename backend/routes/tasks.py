# ============================================================
# Task ID  : T014 / T015 / T016 / T017 / T020 / T023
# Title    : Task routes — Phase V (search/filter/sort, /complete, /internal, events, reminders)
# Spec Ref : speckit.tasks → T014-T020 / T023
# Plan Ref : speckit.plan → Section 3: API Contracts / Section 6.2
# ============================================================
"""Task management routes — Phase V extended with search, filter, sort, complete."""

from datetime import datetime, timezone
from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy import func, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.auth.dependencies import verify_user_owns_resource
from backend.config import settings
from backend.events import publisher
from backend.events.schemas import (
    TaskCreated,
    TaskUpdated,
    TaskDeleted,
    TaskCompleted,
    TaskSyncUpdate,
)
from backend.models.schemas import (
    CurrentUser,
    TaskCompleteResponse,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)

router = APIRouter(
    prefix="/api/v1/users/{user_id}/tasks",
    tags=["Tasks"],
)

# Internal router — no auth prefix (protected by Dapr mTLS + NetworkPolicy)
internal_router = APIRouter(prefix="/internal", tags=["Internal"])


# =============================================================================
# Database Session Dependency
# =============================================================================


async def get_db_session():
    """Get database session — uses DB if configured, otherwise raises 503."""
    if not settings.database_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    from backend.database import get_session
    async for session in get_session():
        yield session


# =============================================================================
# Helpers
# =============================================================================


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _priority_sort_key(priority_col):
    """Map priority string to numeric sort weight via CASE expression."""
    from sqlalchemy import case
    return case(
        (priority_col == "high", 1),
        (priority_col == "medium", 2),
        (priority_col == "low", 3),
        else_=4,
    )


# =============================================================================
# Task Endpoints
# =============================================================================


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    user_id: str = Path(..., description="User ID"),
    current_user: CurrentUser = Depends(verify_user_owns_resource),
    # Existing filters
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    # Phase V filters
    search: Optional[str] = Query(None, description="Full-text search on title + description"),
    priority: Optional[str] = Query(None, description="Filter by priority: low|medium|high"),
    tag: Optional[str] = Query(None, description="Filter by tag (exact match in tags array)"),
    due_before: Optional[datetime] = Query(None, description="Filter tasks due before this datetime"),
    due_after: Optional[datetime] = Query(None, description="Filter tasks due after this datetime"),
    # Sort
    sort: Optional[Literal["due_date", "priority", "created_at"]] = Query(
        None, description="Sort field"
    ),
    sort_dir: Optional[Literal["asc", "desc"]] = Query("desc", description="Sort direction"),
    # Pagination
    limit: int = Query(50, ge=1, le=100, description="Maximum tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    session: AsyncSession = Depends(get_db_session),
) -> TaskListResponse:
    """
    List tasks for the authenticated user.

    Supports full-text search, filter by priority/tag/due_date range, and sort.
    All filters are AND-combined. Owner isolation is always enforced.
    """
    from backend.models.database import Task

    query = select(Task).where(Task.owner_id == user_id)

    # --- Filters ---
    if completed is not None:
        query = query.where(Task.completed == completed)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            Task.title.ilike(search_term) | Task.description.ilike(search_term)
        )

    if priority:
        if priority not in ("low", "medium", "high"):
            raise HTTPException(status_code=400, detail="priority must be low, medium, or high")
        query = query.where(Task.priority == priority)

    if tag:
        # JSON array containment — works on PostgreSQL; SQLite uses string LIKE fallback
        query = query.where(cast(Task.tags, String).contains(f'"{tag}"'))

    if due_before:
        query = query.where(Task.due_date <= due_before)

    if due_after:
        query = query.where(Task.due_date >= due_after)

    # --- Count (before pagination) ---
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await session.execute(count_query)
    total = count_result.scalar_one()

    # --- Sort ---
    if sort == "due_date":
        col = Task.due_date.asc() if sort_dir == "asc" else Task.due_date.desc()
    elif sort == "priority":
        col = _priority_sort_key(Task.priority).asc() if sort_dir == "asc" \
              else _priority_sort_key(Task.priority).desc()
    else:
        col = Task.created_at.asc() if sort_dir == "asc" else Task.created_at.desc()

    query = query.order_by(col).offset(offset).limit(limit)
    result = await session.execute(query)
    tasks = result.scalars().all()

    return TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Path(..., description="User ID"),
    current_user: CurrentUser = Depends(verify_user_owns_resource),
    session: AsyncSession = Depends(get_db_session),
) -> TaskResponse:
    """
    Create a new task for the authenticated user.

    Phase V: accepts due_date, priority, tags, recurrence.
    If due_date is set, a Dapr Job reminder is scheduled (via event_publisher).
    """
    from backend.models.database import Task

    recurrence_dict = task_data.recurrence.model_dump() if task_data.recurrence else None

    task = Task(
        owner_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed,
        due_date=task_data.due_date,
        priority=task_data.priority,
        tags=task_data.tags or [],
        recurrence=recurrence_dict,
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    task_resp = TaskResponse.model_validate(task)

    # T020: Publish task-events + task-updates after successful create
    created_event = TaskCreated(
        task_id=str(task.id),
        user_id=user_id,
        title=task.title,
        due_date=task.due_date.isoformat() if task.due_date else None,
        priority=task.priority,
        tags=task.tags or [],
        recurrence=task.recurrence,
    )
    sync_event = TaskSyncUpdate(
        task_id=str(task.id),
        user_id=user_id,
        operation="created",
        payload=created_event.dict(),
    )
    await publisher.publish_event("task-events", created_event.dict())
    await publisher.publish_event("task-updates", sync_event.dict())

    # T023: Schedule reminder if due_date set
    if task.due_date:
        from backend.services import reminder_service
        await reminder_service.schedule_reminder(
            task_id=str(task.id),
            due_date=task.due_date,
            user_id=user_id,
            title=task.title,
        )

    return task_resp


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str = Path(..., description="User ID"),
    task_id: UUID = Path(..., description="Task ID"),
    current_user: CurrentUser = Depends(verify_user_owns_resource),
    session: AsyncSession = Depends(get_db_session),
) -> TaskResponse:
    """Get a specific task by ID. Returns 404 if not found or not owned."""
    from backend.models.database import Task

    query = select(Task).where(Task.id == task_id, Task.owner_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_data: TaskUpdate,
    user_id: str = Path(..., description="User ID"),
    task_id: UUID = Path(..., description="Task ID"),
    current_user: CurrentUser = Depends(verify_user_owns_resource),
    session: AsyncSession = Depends(get_db_session),
) -> TaskResponse:
    """
    Partially update a task.

    Only updates provided fields. Phase V: supports due_date, priority, tags, recurrence.
    """
    from backend.models.database import Task

    query = select(Task).where(Task.id == task_id, Task.owner_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "recurrence" and value is not None:
            # Convert Pydantic model to dict for JSON storage
            value = value if isinstance(value, dict) else value.model_dump()
        setattr(task, key, value)

    task.updated_at = _utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    task_resp = TaskResponse.model_validate(task)

    # T020: Publish task-events + task-updates after successful update
    changed = list(update_data.keys())
    updated_event = TaskUpdated(
        task_id=str(task.id),
        user_id=user_id,
        changed_fields=changed,
        new_values={k: update_data[k] for k in changed},
    )
    sync_event = TaskSyncUpdate(
        task_id=str(task.id),
        user_id=user_id,
        operation="updated",
        payload=updated_event.dict(),
    )
    await publisher.publish_event("task-events", updated_event.dict())
    await publisher.publish_event("task-updates", sync_event.dict())

    # T023: Re-schedule reminder if due_date changed
    if "due_date" in update_data:
        from backend.services import reminder_service
        await reminder_service.cancel_reminder(str(task.id))
        if task.due_date:
            await reminder_service.schedule_reminder(
                task_id=str(task.id),
                due_date=task.due_date,
                user_id=user_id,
                title=task.title,
            )

    return task_resp


@router.post("/{task_id}/complete", response_model=TaskCompleteResponse)
async def complete_task(
    user_id: str = Path(..., description="User ID"),
    task_id: UUID = Path(..., description="Task ID"),
    current_user: CurrentUser = Depends(verify_user_owns_resource),
    session: AsyncSession = Depends(get_db_session),
) -> TaskCompleteResponse:
    """
    Mark a task as complete.

    Sets completed=True and completed_at=utcnow().
    If task has recurrence, the Recurring Task Service will spawn the next occurrence
    after receiving the TaskCompleted event via Dapr Pub/Sub.
    """
    from backend.models.database import Task

    query = select(Task).where(Task.id == task_id, Task.owner_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if task.completed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Task already completed")

    now = _utcnow()
    task.completed = True
    task.completed_at = now
    task.updated_at = now

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # T020: Publish TaskCompleted + task-updates after marking complete
    completed_event = TaskCompleted(
        task_id=str(task.id),
        user_id=user_id,
        completed_at=task.completed_at.isoformat(),
        recurrence=task.recurrence,
    )
    sync_event = TaskSyncUpdate(
        task_id=str(task.id),
        user_id=user_id,
        operation="completed",
        payload=completed_event.dict(),
    )
    await publisher.publish_event("task-events", completed_event.dict())
    await publisher.publish_event("task-updates", sync_event.dict())

    # T023: Cancel reminder on completion (no longer needed)
    from backend.services import reminder_service
    await reminder_service.cancel_reminder(str(task.id))

    return TaskCompleteResponse(
        id=task.id,
        completed=task.completed,
        completed_at=task.completed_at,
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str = Path(..., description="User ID"),
    task_id: UUID = Path(..., description="Task ID"),
    current_user: CurrentUser = Depends(verify_user_owns_resource),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete a task. Returns 404 if not found or not owned."""
    from backend.models.database import Task

    query = select(Task).where(Task.id == task_id, Task.owner_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    await session.delete(task)
    await session.commit()

    # T020: Publish TaskDeleted + task-updates after deletion
    deleted_event = TaskDeleted(task_id=str(task_id), user_id=user_id)
    sync_event = TaskSyncUpdate(
        task_id=str(task_id),
        user_id=user_id,
        operation="deleted",
        payload=deleted_event.dict(),
    )
    await publisher.publish_event("task-events", deleted_event.dict())
    await publisher.publish_event("task-updates", sync_event.dict())

    # T023: Cancel any pending reminder
    from backend.services import reminder_service
    await reminder_service.cancel_reminder(str(task_id))


# =============================================================================
# Internal Endpoint — Dapr Service Invocation only (T017)
# =============================================================================


@internal_router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_internal(
    task_data: TaskCreate,
    user_id: str = Query(..., description="User ID (from recurring-service via Dapr)"),
    session: AsyncSession = Depends(get_db_session),
) -> TaskResponse:
    """
    Internal endpoint for Dapr Service Invocation.

    Used exclusively by the Recurring Task Service to create the next task occurrence.
    NOT exposed externally — protected by Dapr mTLS + NetworkPolicy.
    No JWT auth check: caller is a trusted internal Dapr service.
    """
    from backend.models.database import Task

    recurrence_dict = task_data.recurrence.model_dump() if task_data.recurrence else None

    task = Task(
        owner_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False,
        due_date=task_data.due_date,
        priority=task_data.priority,
        tags=task_data.tags or [],
        recurrence=recurrence_dict,
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return TaskResponse.model_validate(task)
