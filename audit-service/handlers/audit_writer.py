# ============================================================
# Task ID  : T037
# Title    : Audit Service — audit log writer
# Spec Ref : speckit.plan → Section 3.4: Idempotency enforcement
# Plan Ref : speckit.plan → Section 1.2: Audit Service
# ============================================================
"""
Write every consumed Kafka event to the audit_log table.
Deduplication via event_id unique constraint in PostgreSQL.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

import structlog

log = structlog.get_logger()

# In-memory audit log for hackathon (no DB dependency at startup)
# In production: replace with PostgreSQL via SQLModel + Alembic migration 002
_audit_log: List[Dict] = []
_processed_events: set[str] = set()


async def write_audit_entry(event: Dict, topic: str) -> None:
    """
    Write an audit entry for any consumed event.

    Idempotent: duplicate event_id is silently skipped.
    """
    event_id = event.get("event_id", str(uuid4()))
    event_type = event.get("event_type", "Unknown")

    if event_id in _processed_events:
        log.info("duplicate_audit_skipped", event_id=event_id, event_type=event_type)
        return

    _processed_events.add(event_id)

    entry = {
        "id": str(uuid4()),
        "event_id": event_id,
        "event_type": event_type,
        "topic": topic,
        "payload": event,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _audit_log.append(entry)

    log.info(
        "audit_entry_written",
        event_id=event_id,
        event_type=event_type,
        topic=topic,
        total_entries=len(_audit_log),
    )


async def list_audit_entries(
    limit: int = 50,
    offset: int = 0,
    topic: Optional[str] = None,
) -> List[Dict]:
    """Return paginated audit entries, optionally filtered by topic."""
    filtered = [e for e in _audit_log if topic is None or e["topic"] == topic]
    return list(reversed(filtered))[offset : offset + limit]
