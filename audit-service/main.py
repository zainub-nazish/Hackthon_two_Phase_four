# ============================================================
# Task ID  : T004 / T038
# Title    : Audit Service — immutable event log writer
# Spec Ref : speckit.plan → Section 1.2: Audit Service
# Plan Ref : speckit.plan → Section 3.2: Consumers per topic
# ============================================================
import structlog
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()

app = FastAPI(
    title="Audit Service",
    description="Subscribes to all topics and writes immutable append-only audit log",
    version="5.0.0",
)


@app.get("/health")
async def health():
    """Liveness + readiness probe endpoint."""
    return {"status": "ok", "service": "audit-service"}


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """Programmatic Dapr subscription for all 3 topics."""
    return [
        {"pubsubname": "pubsub-kafka", "topic": "task-events",  "route": "/task-events-handler"},
        {"pubsubname": "pubsub-kafka", "topic": "reminders",    "route": "/reminders-handler"},
        {"pubsubname": "pubsub-kafka", "topic": "task-updates",  "route": "/task-updates-handler"},
    ]


async def _handle_event(request: Request, topic: str):
    """Shared handler: dedup check + write AuditEntry."""
    try:
        from handlers.audit_writer import write_audit_entry
        body = await request.json()
        event = body.get("data", body)
        await write_audit_entry(event, topic)
        return JSONResponse(status_code=200, content={"status": "SUCCESS"})
    except Exception as exc:
        log.error("audit_handler_error", topic=topic, error=str(exc))
        return JSONResponse(status_code=200, content={"status": "ERROR", "detail": str(exc)})


@app.post("/task-events-handler")
async def task_events_handler(request: Request):
    return await _handle_event(request, "task-events")


@app.post("/reminders-handler")
async def reminders_handler(request: Request):
    return await _handle_event(request, "reminders")


@app.post("/task-updates-handler")
async def task_updates_handler(request: Request):
    return await _handle_event(request, "task-updates")


@app.get("/audit")
async def get_audit_log(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    topic: str = Query(None, description="Filter by topic"),
):
    """Return paginated audit log entries."""
    from handlers.audit_writer import list_audit_entries
    entries = await list_audit_entries(limit=limit, offset=offset, topic=topic)
    return {"entries": entries, "limit": limit, "offset": offset}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=False)
