# ============================================================
# Task ID  : T005 / T041 / T042
# Title    : WebSocket Service — real-time task broadcast
# Spec Ref : speckit.plan → Section 1.2: WebSocket Service
# Plan Ref : speckit.plan → Section 6.2: Frontend → Backend Pattern
# ============================================================
import structlog
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from handlers.task_sync import handle_task_sync, manager

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()

app = FastAPI(
    title="WebSocket Service",
    description="Subscribes to task-updates and broadcasts to all connected WebSocket clients",
    version="5.0.0",
)


@app.get("/health")
async def health():
    """Liveness + readiness probe endpoint."""
    return {"status": "ok", "service": "websocket-service", "connections": manager.count()}


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """Programmatic Dapr subscription for task-updates topic."""
    return [
        {
            "pubsubname": "pubsub-kafka",
            "topic": "task-updates",
            "route": "/task-updates-handler",
        }
    ]


@app.post("/task-updates-handler")
async def task_updates_handler(request: Request):
    """
    Dapr CloudEvent handler for task-updates topic.
    Broadcasts TaskSyncUpdate payload to all connected WebSocket clients.
    """
    try:
        body = await request.json()
        event = body.get("data", body)
        await handle_task_sync(event)
        return JSONResponse(status_code=200, content={"status": "SUCCESS"})
    except Exception as exc:
        log.error("task_updates_handler_error", error=str(exc))
        return JSONResponse(status_code=200, content={"status": "ERROR", "detail": str(exc)})


@app.websocket("/ws/tasks")
async def websocket_endpoint(websocket: WebSocket, user_id: str = "anonymous"):
    """
    WebSocket endpoint — clients connect here to receive real-time task updates.
    Query param: ?user_id=<uuid>
    """
    await manager.connect(websocket, user_id)
    log.info("websocket_connected", user_id=user_id)
    try:
        while True:
            # Keep connection alive; server pushes — client only pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        log.info("websocket_disconnected", user_id=user_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=False)
