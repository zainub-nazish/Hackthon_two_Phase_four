# ============================================================
# Task ID  : T037
# Title    : Audit Service — task-updates handler
# Spec Ref : speckit.plan → Section 3.2: Consumers per topic
# Plan Ref : speckit.plan → Section 1.2: Audit Service
# ============================================================
"""Per-topic handler for task-updates topic — delegates to shared audit_writer."""
from typing import Dict

from handlers.audit_writer import write_audit_entry


async def handle_task_update_event(event: Dict) -> None:
    """Write any task-updates event to the audit log."""
    await write_audit_entry(event, "task-updates")
