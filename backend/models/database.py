# ============================================================
# Task ID  : T011
# Title    : Extend Task model with Phase V fields
# Spec Ref : speckit.tasks → T011 (Task model extension)
# Plan Ref : speckit.plan → Section 2.4: Database & External Services
# ============================================================
"""SQLModel database models for persistent task storage and chat."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON
from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    """
    Database model for task storage — Phase V extended.
    New fields: due_date, priority, tags, recurrence, completed_at.
    Added via Alembic migration 001_add_phase_v_task_fields.
    """

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
        max_length=200,
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
    # Phase V fields — added via Alembic migration 001
    due_date: Optional[datetime] = Field(
        default=None,
        description="When this task is due (ISO 8601 UTC)"
    )
    priority: str = Field(
        default="medium",
        max_length=10,
        description="Task priority: low | medium | high"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        sa_type=JSON,
        description="Arbitrary string labels"
    )
    recurrence: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_type=JSON,
        description="Recurrence config: {interval: daily|weekly|monthly|custom, every: int}"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when /complete was called"
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


# =============================================================================
# Chat Models (007-chat-api)
# =============================================================================


class Conversation(SQLModel, table=True):
    """Database model for chat conversations."""

    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier"
    )
    owner_id: str = Field(
        index=True,
        nullable=False,
        description="User ID from JWT sub claim"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Conversation creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last activity timestamp"
    )


class Message(SQLModel, table=True):
    """Database model for chat messages within a conversation."""

    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier"
    )
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        nullable=False,
        description="Parent conversation ID"
    )
    role: str = Field(
        max_length=20,
        nullable=False,
        description="Sender role: 'user' or 'assistant'"
    )
    content: str = Field(
        nullable=False,
        description="Message text content"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Message timestamp"
    )


class ToolCall(SQLModel, table=True):
    """Database model for AI agent tool invocations."""

    __tablename__ = "tool_calls"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique tool call identifier"
    )
    message_id: UUID = Field(
        foreign_key="messages.id",
        index=True,
        nullable=False,
        description="Parent assistant message ID"
    )
    tool_name: str = Field(
        max_length=100,
        nullable=False,
        description="Name of the invoked tool"
    )
    parameters: str = Field(
        nullable=False,
        description="JSON-encoded input parameters"
    )
    result: str = Field(
        nullable=False,
        description="JSON-encoded output result"
    )
    status: str = Field(
        max_length=20,
        nullable=False,
        description="Execution status: 'success' or 'error'"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Execution timestamp"
    )
