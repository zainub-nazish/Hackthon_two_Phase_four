"use client";

import { useState, useCallback } from "react";
import type { Toast } from "@/types";

const DEFAULT_DURATION = 5000;

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback(
    (toast: Omit<Toast, "id">) => {
      const id = crypto.randomUUID();
      const duration = toast.duration ?? DEFAULT_DURATION;

      setToasts((prev) => [...prev, { ...toast, id }]);

      // Auto-dismiss after duration
      if (duration > 0) {
        setTimeout(() => {
          setToasts((prev) => prev.filter((t) => t.id !== id));
        }, duration);
      }

      return id;
    },
    []
  );

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const success = useCallback(
    (message: string, duration?: number) => {
      return addToast({ type: "success", message, duration });
    },
    [addToast]
  );

  const error = useCallback(
    (message: string, duration?: number) => {
      return addToast({ type: "error", message, duration });
    },
    [addToast]
  );

  const info = useCallback(
    (message: string, duration?: number) => {
      return addToast({ type: "info", message, duration });
    },
    [addToast]
  );

  const warning = useCallback(
    (message: string, duration?: number) => {
      return addToast({ type: "warning", message, duration });
    },
    [addToast]
  );

  return {
    toasts,
    addToast,
    dismissToast,
    success,
    error,
    info,
    warning,
  };
}
