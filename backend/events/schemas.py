# ============================================================
# Task ID  : T010
# Title    : Shared Kafka event schemas (Phase V)
# Spec Ref : speckit.plan → Section 3.3: Event Schema References
# Plan Ref : speckit.plan → Section 3: Event-Driven Backbone
# ============================================================
"""
All Kafka event schemas used by Chat API (producer) and consumer services.
Every event carries: event_id, event_type, schema_version, timestamp, task_id, user_id.
Schema version: 1.0.0 — BACKWARD compatible.
Idempotency key: event_id (UUID v4, producer-generated, never reused).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional
from uuid import UUID, uuid4


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_uuid() -> str:
    return str(uuid4())


# ---------------------------------------------------------------------------
# topic: task-events
# ---------------------------------------------------------------------------

@dataclass
class TaskCreated:
    task_id: str
    user_id: str
    title: str
    event_id: str = field(default_factory=_new_uuid)
    event_type: str = "TaskCreated"
    schema_version: str = "1.0.0"
    timestamp: str = field(default_factory=_now_iso)
    due_date: Optional[str] = None
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)
    recurrence: Optional[Dict] = None

    def dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class TaskUpdated:
    task_id: str
    user_id: str
    changed_fields: List[str]
    event_id: str = field(default_factory=_new_uuid)
    event_type: str = "TaskUpdated"
    schema_version: str = "1.0.0"
    timestamp: str = field(default_factory=_now_iso)
    previous_values: Optional[Dict] = None
    new_values: Optional[Dict] = None

    def dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class TaskDeleted:
    task_id: str
    user_id: str
    event_id: str = field(default_factory=_new_uuid)
    event_type: str = "TaskDeleted"
    schema_version: str = "1.0.0"
    timestamp: str = field(default_factory=_now_iso)
    deleted_at: str = field(default_factory=_now_iso)
    reason: Optional[str] = None

    def dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class TaskCompleted:
    task_id: str
    user_id: str
    completed_at: str
    event_id: str = field(default_factory=_new_uuid)
    event_type: str = "TaskCompleted"
    schema_version: str = "1.0.0"
    timestamp: str = field(default_factory=_now_iso)
    recurrence: Optional[Dict] = None

    def dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


# ---------------------------------------------------------------------------
# topic: reminders
# ---------------------------------------------------------------------------

@dataclass
class ReminderScheduled:
    task_id: str
    user_id: str
    remind_at: str
    title: str
    event_id: str = field(default_factory=_new_uuid)
    event_type: str = "ReminderScheduled"
    schema_version: str = "1.0.0"
    timestamp: str = field(default_factory=_now_iso)
    message: Optional[str] = None
    job_id: Optional[str] = None

    def dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class ReminderFired:
    task_id: str
    user_id: str
    fired_at: str
    event_id: str = field(default_factory=_new_uuid)
    event_type: str = "ReminderFired"
    schema_version: str = "1.0.0"
    timestamp: str = field(default_factory=_now_iso)
    delivery_status: Literal["delivered", "failed", "pending"] = "pending"
    job_id: Optional[str] = None

    def dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


# ---------------------------------------------------------------------------
# topic: task-updates
# ---------------------------------------------------------------------------

@dataclass
class TaskSyncUpdate:
    task_id: str
    user_id: str
    operation: Literal["created", "updated", "deleted", "completed"]
    event_id: str = field(default_factory=_new_uuid)
    event_type: str = "TaskSyncUpdate"
    schema_version: str = "1.0.0"
    timestamp: str = field(default_factory=_now_iso)
    payload: Optional[Dict] = None
    broadcast_to: Literal["all", "user", "room"] = "all"

    def dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}
