# ============================================================
# Task ID  : T019
# Title    : Dapr Pub/Sub event publisher
# Spec Ref : speckit.plan → Section 3: Event-Driven Backbone
# Plan Ref : speckit.plan → Section 3.3: Publishing Pattern (Dapr Pub/Sub ONLY)
# ============================================================
"""
Async event publisher — always uses Dapr sidecar HTTP API.

All Kafka communication goes through Dapr Pub/Sub:
  POST http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}

Constitution C-01: NO direct kafka-python / aiokafka usage.
"""
from __future__ import annotations

import os

import httpx
import structlog

log = structlog.get_logger()

DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub-kafka")

_DAPR_PUBLISH_URL = (
    f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}"
)


async def publish_event(topic: str, event: dict) -> None:
    """
    Publish an event dict to the given Kafka topic via Dapr Pub/Sub.

    Fire-and-forget with structured logging on error.
    Failures are logged but do NOT raise — API responses must not be blocked
    by a Dapr sidecar unavailability.
    """
    url = f"{_DAPR_PUBLISH_URL}/{topic}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json=event)
            resp.raise_for_status()
        log.info(
            "event_published",
            topic=topic,
            event_type=event.get("event_type"),
            event_id=event.get("event_id"),
        )
    except httpx.HTTPStatusError as exc:
        log.error(
            "event_publish_http_error",
            topic=topic,
            event_type=event.get("event_type"),
            status_code=exc.response.status_code,
            detail=exc.response.text[:200],
        )
    except httpx.RequestError as exc:
        log.error(
            "event_publish_connection_error",
            topic=topic,
            event_type=event.get("event_type"),
            error=str(exc),
        )
