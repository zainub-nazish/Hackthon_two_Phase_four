# ============================================================
# Task ID  : T024
# Title    : Dapr State Store — conversation state management
# Spec Ref : speckit.plan → Section 5: State & Secrets Management
# Plan Ref : speckit.plan → Section 5.1: Dapr statestore configuration
# ============================================================
"""
Conversation state management via Dapr State Store (state-postgresql).

Key pattern: {user_id}||{session_id}
State TTL: not set here — managed by Dapr component cleanupInterval.
Constitution C-02: all state access via Dapr sidecar HTTP API.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import httpx
import structlog

log = structlog.get_logger()

DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
STATE_STORE_NAME = os.getenv("DAPR_STATE_STORE_NAME", "state-postgresql")
_DAPR_STATE_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{STATE_STORE_NAME}"


def _state_key(user_id: str, session_id: str) -> str:
    """State key pattern: user_id||session_id."""
    return f"{user_id}||{session_id}"


async def save_conversation_state(
    user_id: str,
    session_id: str,
    messages: List[Dict[str, Any]],
) -> None:
    """
    Persist conversation message history to Dapr state store.

    Uses upsert semantics — creates or replaces the state entry.
    """
    key = _state_key(user_id, session_id)
    state_body = [
        {
            "key": key,
            "value": {"user_id": user_id, "session_id": session_id, "messages": messages},
        }
    ]
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(_DAPR_STATE_URL, json=state_body)
            resp.raise_for_status()
        log.info(
            "conversation_state_saved",
            user_id=user_id,
            session_id=session_id,
            message_count=len(messages),
        )
    except httpx.HTTPStatusError as exc:
        log.error(
            "state_save_http_error",
            key=key,
            status_code=exc.response.status_code,
            detail=exc.response.text[:200],
        )
    except httpx.RequestError as exc:
        log.error("state_save_connection_error", key=key, error=str(exc))


async def get_conversation_state(
    user_id: str,
    session_id: str,
) -> Optional[List[Dict[str, Any]]]:
    """
    Retrieve conversation message history from Dapr state store.

    Returns None if no state found (404) or on error.
    """
    key = _state_key(user_id, session_id)
    url = f"{_DAPR_STATE_URL}/{key}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            if resp.status_code == 204 or not resp.content:
                return None
            resp.raise_for_status()
            data = resp.json()
            return data.get("messages", [])
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return None
        log.error(
            "state_get_http_error",
            key=key,
            status_code=exc.response.status_code,
        )
        return None
    except httpx.RequestError as exc:
        log.error("state_get_connection_error", key=key, error=str(exc))
        return None
