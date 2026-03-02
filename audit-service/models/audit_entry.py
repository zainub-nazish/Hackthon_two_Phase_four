# ============================================================
# Task ID  : T036
# Title    : Audit Service — AuditEntry SQLModel
# Spec Ref : speckit.plan → Section 1.2: Audit Service
# Plan Ref : speckit.plan → Section 5.1: State & Secrets (audit_log table)
# ============================================================
"""
SQLModel ORM for audit_log table.

In hackathon mode: handlers use in-memory list (audit_writer.py).
In production: replace _audit_log list with async DB writes using this model.
Migration for schema: backend/alembic/versions/002_add_audit_and_dedup_tables.py
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlmodel import Field, JSON, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuditEntry(SQLModel, table=True):
    """
    Immutable audit log row — one row per consumed Kafka event.

    Constitution constraint: event_id has a UNIQUE constraint to enforce
    exactly-once write semantics at the DB level.
    """

    __tablename__ = "audit_log"  # matches migration 002

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Audit entry UUID",
    )
    event_id: str = Field(
        index=True,
        description="Producer-assigned UUID — UNIQUE constraint prevents duplicate writes",
    )
    event_type: str = Field(description="Event class name (e.g. TaskCreated)")
    topic: str = Field(description="Kafka topic name")
    payload: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_type=JSON,
        description="Full event payload as JSON",
    )
    created_at: datetime = Field(
        default_factory=_utcnow,
        description="UTC timestamp when the audit entry was written",
    )
