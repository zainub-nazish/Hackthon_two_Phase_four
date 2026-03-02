# ============================================================
# Task ID  : T003 / T034
# Title    : Notification Service — Dapr reminders subscriber
# Spec Ref : speckit.plan → Section 1.2: Notification Service
# Plan Ref : speckit.plan → Section 4.2: Reminder Scheduling Flow
# ============================================================
import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from handlers.reminder_fired import handle_reminder_fired

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()

app = FastAPI(
    title="Notification Service",
    description="Subscribes to reminders topic and delivers exact-time task reminders",
    version="5.0.0",
)


@app.get("/health")
async def health():
    """Liveness + readiness probe endpoint."""
    return {"status": "ok", "service": "notification-service"}


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """Programmatic Dapr subscription for reminders topic."""
    return [
        {
            "pubsubname": "pubsub-kafka",
            "topic": "reminders",
            "route": "/reminders-handler",
        }
    ]


@app.post("/reminders-handler")
async def reminders_handler(request: Request):
    """
    Dapr CloudEvent handler for reminders topic.
    Handles ReminderFired events and delivers notification to user.
    """
    try:
        body = await request.json()
        event = body.get("data", body)
        event_type = event.get("event_type", "")

        if event_type == "ReminderFired":
            await handle_reminder_fired(event)
        else:
            log.debug("skipping_event", event_type=event_type)

        return JSONResponse(status_code=200, content={"status": "SUCCESS"})

    except Exception as exc:
        log.error("reminders_handler_error", error=str(exc))
        return JSONResponse(status_code=200, content={"status": "ERROR", "detail": str(exc)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False)
