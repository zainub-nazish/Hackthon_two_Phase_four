# ============================================================
# Task ID  : T002 / T031
# Title    : Recurring Task Service — Dapr subscriber
# Spec Ref : speckit.plan → Section 4.3: Recurring Task Spawn Flow
# Plan Ref : speckit.plan → Section 1.2: Recurring Task Service
# ============================================================
import logging

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from handlers.task_completed import handle_task_completed

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()

app = FastAPI(
    title="Recurring Task Service",
    description="Subscribes to task-events and auto-creates next task occurrence on completion",
    version="5.0.0",
)


@app.get("/health")
async def health():
    """Liveness + readiness probe endpoint."""
    return {"status": "ok", "service": "recurring-service"}


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """Declarative Dapr subscription registration (fallback to programmatic)."""
    return [
        {
            "pubsubname": "pubsub-kafka",
            "topic": "task-events",
            "route": "/task-events-handler",
        }
    ]


@app.post("/task-events-handler")
async def task_events_handler(request: Request):
    """
    Dapr CloudEvent handler for task-events topic.
    Only acts on TaskCompleted events that carry a recurrence field.
    """
    try:
        body = await request.json()
        # Dapr wraps payload in CloudEvent envelope: body["data"] is the actual event
        event = body.get("data", body)
        event_type = event.get("event_type", "")

        if event_type == "TaskCompleted":
            await handle_task_completed(event)
        else:
            log.debug("skipping_non_recurring_event", event_type=event_type)

        return JSONResponse(status_code=200, content={"status": "SUCCESS"})

    except Exception as exc:
        log.error("task_events_handler_error", error=str(exc))
        # Return 200 to prevent Dapr from redelivering — log and continue
        return JSONResponse(status_code=200, content={"status": "ERROR", "detail": str(exc)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
