# ============================================================
# Task ID  : T022 (Dapr job handler added)
# Title    : FastAPI application entry point — Phase V
# Spec Ref : speckit.plan → Section 4.2: Dapr Jobs callback
# Plan Ref : speckit.plan → Section 4: Scheduling & Reminder/Recurring Logic
# ============================================================
"""FastAPI application entry point — Phase V with Dapr job handler."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings

# Validate configuration on startup
settings.validate_secret()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Startup: Initialize database tables (if DATABASE_URL is configured).
    Shutdown: Close database connections.
    """
    # Startup
    if settings.database_url:
        from backend.database import init_db, close_db
        # Import models to register them with SQLModel metadata
        from backend.models import database as _  # noqa: F401
        await init_db()

    yield

    # Shutdown
    if settings.database_url:
        from backend.database import close_db
        await close_db()


# Create FastAPI application
app = FastAPI(
    title="Todo Application API",
    description="JWT-authenticated Todo API with user isolation",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint for health checks."""
    return {"status": "ok", "message": "Todo API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and register routers after app is created
from backend.routes import auth, tasks, chat

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(tasks.internal_router)
app.include_router(chat.router)


# =============================================================================
# T022: Dapr Jobs API callback handler
# Dapr calls POST /job/{job_name} when a scheduled job fires.
# job_name convention: reminder-{task_id}
# =============================================================================


@app.post("/job/{job_name}", tags=["Dapr"])
async def dapr_job_handler(job_name: str, request: Request) -> JSONResponse:
    """
    Receives Dapr Jobs API callbacks when a scheduled job fires.

    Convention: job_name = reminder-{task_id}
    Action: publish ReminderFired event to `reminders` Kafka topic via Dapr Pub/Sub.
    """
    import structlog

    log = structlog.get_logger()

    try:
        body = await request.json()
    except Exception:
        body = {}

    log.info("dapr_job_fired", job_name=job_name, data=body)

    # Extract task metadata embedded when job was created
    data = body.get("data", body)
    task_id = data.get("task_id", job_name.replace("reminder-", "", 1))
    user_id = data.get("user_id", "")
    title = data.get("title", "")

    from datetime import datetime, timezone
    from backend.events.schemas import ReminderFired
    from backend.events.publisher import publish_event

    fired_event = ReminderFired(
        task_id=task_id,
        user_id=user_id,
        fired_at=datetime.now(timezone.utc).isoformat(),
        job_id=job_name,
        delivery_status="delivered",
    )
    await publish_event("reminders", fired_event.dict())

    return JSONResponse(status_code=200, content={"status": "SUCCESS"})


