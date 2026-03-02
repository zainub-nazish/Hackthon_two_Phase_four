// ============================================================
// Task ID  : T044
// Title    : Frontend — WebSocket real-time task sync hook
// Spec Ref : speckit.plan → Section 6.2: Frontend → Backend Pattern
// Plan Ref : speckit.plan → Section 1.2: WebSocket Service
// ============================================================
"use client";

/**
 * useTaskSync — connects to the WebSocket Service and triggers a task list
 * refresh whenever a task.created / task.updated / task.deleted /
 * task.completed frame arrives.
 *
 * Usage:
 *   const { isConnected } = useTaskSync({ onUpdate: refreshTasks });
 *
 * The hook reconnects automatically on close (exponential back-off).
 * No external library required — uses the browser's native WebSocket API.
 */

import { useEffect, useRef, useState, useCallback } from "react";

const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8004";

const RECONNECT_DELAY_MS = 2_000;
const MAX_RECONNECT_DELAY_MS = 30_000;

export interface TaskSyncFrame {
  event: string;
  payload: Record<string, unknown>;
}

interface UseTaskSyncOptions {
  /** Called whenever any task sync event arrives. Typically refreshes the task list. */
  onUpdate?: (frame: TaskSyncFrame) => void;
  /** Disable the hook (e.g. when user is not logged in). Default: true */
  enabled?: boolean;
}

interface UseTaskSyncReturn {
  isConnected: boolean;
}

export function useTaskSync({
  onUpdate,
  enabled = true,
}: UseTaskSyncOptions = {}): UseTaskSyncReturn {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectDelayRef = useRef(RECONNECT_DELAY_MS);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const unmountedRef = useRef(false);

  const onUpdateRef = useRef(onUpdate);
  onUpdateRef.current = onUpdate;

  const connect = useCallback(() => {
    if (unmountedRef.current || !enabled) return;

    const url = `${WS_BASE_URL}/ws/tasks`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      if (unmountedRef.current) return;
      setIsConnected(true);
      reconnectDelayRef.current = RECONNECT_DELAY_MS; // reset back-off
    };

    ws.onmessage = (event) => {
      if (unmountedRef.current) return;
      try {
        const frame: TaskSyncFrame = JSON.parse(event.data as string);
        onUpdateRef.current?.(frame);
      } catch {
        // Malformed frame — ignore
      }
    };

    ws.onerror = () => {
      // onerror is always followed by onclose; handle reconnect there
    };

    ws.onclose = () => {
      if (unmountedRef.current) return;
      setIsConnected(false);
      wsRef.current = null;

      // Exponential back-off reconnect
      const delay = reconnectDelayRef.current;
      reconnectDelayRef.current = Math.min(
        delay * 2,
        MAX_RECONNECT_DELAY_MS
      );
      reconnectTimerRef.current = setTimeout(connect, delay);
    };
  }, [enabled]);

  useEffect(() => {
    unmountedRef.current = false;
    if (enabled) {
      connect();
    }

    return () => {
      unmountedRef.current = true;
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [enabled, connect]);

  return { isConnected };
}
