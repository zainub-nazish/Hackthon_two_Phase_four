"""Task management routes with user isolation and database persistence."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.auth.dependencies import verify_user_owns_resource
from backend.config import settings
from backend.models.schemas import (
    CurrentUser,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)

router = APIRouter(
    prefix="/api/v1/users/{user_id}/tasks",
    tags=["Tasks"],
)


# =============================================================================
# Database Session Dependency
# =============================================================================


async def get_db_session():
    """Get database session - uses DB if configured, otherwise raises error."""
    if not settings.database_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    from backend.database import get_session
    async for session in get_session():
        yield session


# =============================================================================
# Task Endpoints
# =============================================================================


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    user_id: str = Path(..., description="User ID"),
    current_user: CurrentUser = Depends(verify_user_owns_resource),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    session: AsyncSession = Depends(get_db_session),
) -> TaskListResponse:
    """
    List all tasks for the authenticated user.

    Only returns tasks owned by the authenticated user.
    Cross-user access is blocked with 404 response.
    """
    from backend.models.database import Task

    # Build query with owner filter (ALWAYS required for security)
    query = select(Task).where(Task.owner_id == user_id)

    # Filter by completion status if specified
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await session.execute(count_query)
    total = count_result.scalar_one()

    # Apply pagination and ordering
    query = query.order_by(Task.created_at.desc()).offset(offset).limit(limit)
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

    The task owner_id is automatically set to the authenticated user.
    """
    from backend.models.database import Task

    task = Task(
        owner_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed,
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str = Path(..., description="User ID"),
    task_id: UUID = Path(..., description="Task ID"),
    current_user: CurrentUser = Depends(verify_user_owns_resource),
    session: AsyncSession = Depends(get_db_session),
) -> TaskResponse:
    """
    Get a specific task by ID.

    Returns 404 if task doesn't exist or user doesn't own it.
    """
    from backend.models.database import Task

    # Query with owner filter (ALWAYS required for security)
    query = select(Task).where(Task.id == task_id, Task.owner_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )

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
    Update a task.

    Only updates provided fields (partial update).
    Returns 404 if task doesn't exist or user doesn't own it.
    """
    from backend.models.database import Task

    # Query with owner filter (ALWAYS required for security)
    query = select(Task).where(Task.id == task_id, Task.owner_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str = Path(..., description="User ID"),
    task_id: UUID = Path(..., description="Task ID"),
    current_user: CurrentUser = Depends(verify_user_owns_resource),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Delete a task.

    Returns 404 if task doesn't exist or user doesn't own it.
    """
    from backend.models.database import Task

    # Query with owner filter (ALWAYS required for security)
    query = select(Task).where(Task.id == task_id, Task.owner_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )

    await session.delete(task)
    await session.commit()
