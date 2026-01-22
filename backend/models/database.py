"""SQLModel database models for persistent task storage."""

from datetime import datetime
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
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp"
    )
