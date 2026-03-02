# ============================================================
# Task ID  : T029 / T030
# Title    : Recurring Task Service — TaskCompleted handler
# Spec Ref : speckit.plan → Section 4.3: Recurring Task Spawn Flow
# Plan Ref : speckit.plan → Section 1.2: Recurring Task Service
# ============================================================
"""
Handle TaskCompleted events from task-events topic.

Flow:
1. Check event_id against dedup store (in-memory for now; PostgreSQL in production)
2. If recurrence is set, calculate next_due date
3. Call Chat API via Dapr Service Invocation to create next task occurrence
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import httpx
import structlog

log = structlog.get_logger()

# In-memory dedup set — stateless pod restart resets it, which is acceptable
# (at-most-once processing per pod lifetime; Kafka offset reset handles at-least-once)
_processed_events: set[str] = set()

DAPR_HTTP_PORT = os.environ.get("DAPR_HTTP_PORT", "3500")
BACKEND_APP_ID = "todo-backend"


async def handle_task_completed(event: Dict) -> None:
    """
    Process a TaskCompleted event.

    Skips if: not a recurring task, or event already processed (idempotency).
    Creates next occurrence via Dapr Service Invocation on Chat API.
    """
    event_id = event.get("event_id", "")
    task_id = event.get("task_id", "")
    user_id = event.get("user_id", "")
    recurrence = event.get("recurrence")

    # Idempotency guard
    if event_id in _processed_events:
        log.info("duplicate_event_skipped", event_id=event_id, task_id=task_id)
        return

    _processed_events.add(event_id)

    if not recurrence:
        log.debug("no_recurrence_skipping", task_id=task_id)
        return

    completed_at_str = event.get("completed_at", datetime.now(timezone.utc).isoformat())
    try:
        completed_at = datetime.fromisoformat(completed_at_str.replace("Z", "+00:00"))
    except ValueError:
        completed_at = datetime.now(timezone.utc)

    next_due = _calculate_next_due(completed_at, recurrence)

    log.info(
        "spawning_next_occurrence",
        task_id=task_id,
        user_id=user_id,
        next_due=next_due.isoformat(),
        interval=recurrence.get("interval"),
    )

    payload = {
        "title": event.get("title", "Recurring Task"),
        "description": event.get("description"),
        "completed": False,
        "due_date": next_due.isoformat(),
        "priority": event.get("priority", "medium"),
        "tags": event.get("tags", []),
        "recurrence": recurrence,
    }

    url = (
        f"http://localhost:{DAPR_HTTP_PORT}/v1.0/invoke"
        f"/{BACKEND_APP_ID}/method/internal/tasks?user_id={user_id}"
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        log.info("next_occurrence_created", task_id=task_id, status=resp.status_code)


def _calculate_next_due(completed_at: datetime, recurrence: Dict) -> datetime:
    """Calculate the next due date from a completed task's recurrence config."""
    interval = recurrence.get("interval", "daily")
    every = int(recurrence.get("every", 1))

    if interval == "daily":
        return completed_at + timedelta(days=every)
    elif interval == "weekly":
        return completed_at + timedelta(weeks=every)
    elif interval == "monthly":
        from dateutil.relativedelta import relativedelta
        return completed_at + relativedelta(months=every)
    elif interval == "custom":
        return completed_at + timedelta(days=every)
    else:
        return completed_at + timedelta(days=1)
