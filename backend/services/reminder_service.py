# ============================================================
# Task ID  : T021
# Title    : Dapr Jobs API — reminder scheduling & cancellation
# Spec Ref : speckit.plan → Section 4: Scheduling & Reminder/Recurring Logic
# Plan Ref : speckit.plan → Section 4.2: Flow for scheduling a reminder
# ============================================================
"""
Schedule and cancel exact-time reminder jobs via Dapr Jobs API.

Constitution C-02: Use Dapr Jobs API (NOT cron bindings, NOT polling).
Job naming convention: reminder-{task_id}
Job callback endpoint: POST /job/reminder/{task_id}
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

import httpx
import structlog

log = structlog.get_logger()

DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
_DAPR_JOBS_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/jobs"


def _job_id(task_id: str) -> str:
    return f"reminder-{task_id}"


async def schedule_reminder(
    task_id: str,
    due_date: datetime,
    user_id: str,
    title: str,
) -> None:
    """
    Create a Dapr Job that fires at due_date (exact-time, no polling).

    Dapr will call POST /job/reminder-{task_id} on this app when the job fires.
    Constitution C-02: exact-time execution via Dapr Jobs API.
    """
    job_id = _job_id(task_id)
    # Dapr Jobs API expects dueTime in RFC3339 / ISO 8601 format
    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)
    due_time_iso = due_date.isoformat()

    payload = {
        "dueTime": due_time_iso,
        "data": {
            "task_id": task_id,
            "user_id": user_id,
            "title": title,
        },
    }

    url = f"{_DAPR_JOBS_URL}/{job_id}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.put(url, json=payload)
            resp.raise_for_status()
        log.info(
            "reminder_scheduled",
            job_id=job_id,
            task_id=task_id,
            due_time=due_time_iso,
        )
    except httpx.HTTPStatusError as exc:
        log.error(
            "reminder_schedule_http_error",
            job_id=job_id,
            status_code=exc.response.status_code,
            detail=exc.response.text[:200],
        )
    except httpx.RequestError as exc:
        log.error(
            "reminder_schedule_connection_error",
            job_id=job_id,
            error=str(exc),
        )


async def cancel_reminder(task_id: str) -> None:
    """
    Delete a Dapr Job by job_id (idempotent — 404 is silently ignored).
    """
    job_id = _job_id(task_id)
    url = f"{_DAPR_JOBS_URL}/{job_id}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.delete(url)
            if resp.status_code not in (200, 204, 404):
                resp.raise_for_status()
        log.info("reminder_cancelled", job_id=job_id, task_id=task_id)
    except httpx.RequestError as exc:
        log.error(
            "reminder_cancel_connection_error",
            job_id=job_id,
            error=str(exc),
        )
