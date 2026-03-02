# ============================================================
# Task ID  : T033
# Title    : Notification Service — ReminderFired handler
# Spec Ref : speckit.plan → Section 4.2: Reminder Scheduling Flow
# Plan Ref : speckit.plan → Section 1.2: Notification Service
# ============================================================
"""
Handle ReminderFired events from reminders topic.
Delivers reminder notification to user (console log for hackathon; extensible).
"""
from __future__ import annotations

from typing import Dict

import structlog

log = structlog.get_logger()

_processed_events: set[str] = set()


async def handle_reminder_fired(event: Dict) -> None:
    """
    Deliver a reminder notification.

    Phase V (hackathon): logs structured message. Future: email/push via SendGrid/FCM.
    """
    event_id = event.get("event_id", "")
    task_id = event.get("task_id", "")
    user_id = event.get("user_id", "")
    fired_at = event.get("fired_at", "")
    job_id = event.get("job_id", "")

    # Idempotency guard
    if event_id in _processed_events:
        log.info("duplicate_reminder_skipped", event_id=event_id, task_id=task_id)
        return

    _processed_events.add(event_id)

    # Deliver notification — console log for hackathon
    log.info(
        "reminder_delivered",
        service="notification-service",
        task_id=task_id,
        user_id=user_id,
        fired_at=fired_at,
        job_id=job_id,
        channel="console",  # future: email | push | slack
    )
