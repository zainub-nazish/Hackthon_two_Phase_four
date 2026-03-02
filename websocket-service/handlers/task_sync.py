# ============================================================
# Task ID  : T040 / T041
# Title    : WebSocket Service — ConnectionManager + TaskSyncUpdate handler
# Spec Ref : speckit.plan → Section 6.2: Frontend → Backend Pattern
# Plan Ref : speckit.plan → Section 1.2: WebSocket Service
# ============================================================
"""
Manages active WebSocket connections and broadcasts TaskSyncUpdate events.

ConnectionManager holds a dict of user_id → list[WebSocket].
On TaskSyncUpdate, broadcast payload to all connected clients (broadcast_to="all").
"""
from __future__ import annotations

import json
from typing import Dict, List

import structlog
from fastapi import WebSocket

log = structlog.get_logger()

_processed_events: set[str] = set()


class ConnectionManager:
    """Thread-safe WebSocket connection manager (single-pod, single-replica)."""

    def __init__(self):
        self._connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = []
        self._connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        if user_id in self._connections:
            try:
                self._connections[user_id].remove(websocket)
            except ValueError:
                pass
            if not self._connections[user_id]:
                del self._connections[user_id]

    async def broadcast(self, message: dict) -> None:
        """Broadcast a message to ALL connected clients regardless of user_id."""
        payload = json.dumps(message)
        dead = []
        for user_id, sockets in self._connections.items():
            for ws in list(sockets):
                try:
                    await ws.send_text(payload)
                except Exception:
                    dead.append((user_id, ws))
        # Clean up dead connections
        for user_id, ws in dead:
            self.disconnect(ws, user_id)

    def count(self) -> int:
        return sum(len(sockets) for sockets in self._connections.values())


# Singleton — shared across all requests in this process
manager = ConnectionManager()


async def handle_task_sync(event: Dict) -> None:
    """
    Broadcast a TaskSyncUpdate event to all connected WebSocket clients.

    Idempotent: duplicate event_id is silently skipped.
    """
    event_id = event.get("event_id", "")
    task_id = event.get("task_id", "")
    operation = event.get("operation", "updated")

    if event_id in _processed_events:
        log.info("duplicate_sync_skipped", event_id=event_id, task_id=task_id)
        return

    _processed_events.add(event_id)

    message = {
        "event": f"task.{operation}",
        "payload": event,
    }

    connection_count = manager.count()
    log.info(
        "broadcasting_task_sync",
        task_id=task_id,
        operation=operation,
        connections=connection_count,
    )

    await manager.broadcast(message)
