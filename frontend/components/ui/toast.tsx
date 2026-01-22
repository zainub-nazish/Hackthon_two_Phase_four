"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import type { Toast as ToastType } from "@/types";

interface ToastProps extends ToastType {
  onDismiss: (id: string) => void;
}

const icons = {
  success: (
    <svg
      className="h-5 w-5 text-success"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M5 13l4 4L19 7"
      />
    </svg>
  ),
  error: (
    <svg
      className="h-5 w-5 text-danger"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M6 18L18 6M6 6l12 12"
      />
    </svg>
  ),
  info: (
    <svg
      className="h-5 w-5 text-primary"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
  ),
  warning: (
    <svg
      className="h-5 w-5 text-secondary"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
      />
    </svg>
  ),
};

const backgrounds = {
  success: "bg-success/20 border-success/30",
  error: "bg-danger/20 border-danger/30",
  info: "bg-primary/20 border-primary/30",
  warning: "bg-secondary/20 border-secondary/30",
};

function Toast({ id, type, message, onDismiss }: ToastProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-lg border p-4 shadow-md animate-slide-in",
        backgrounds[type]
      )}
      role="alert"
      aria-live="polite"
    >
      {icons[type]}
      <p className="flex-1 text-sm font-medium text-light">{message}</p>
      <button
        type="button"
        onClick={() => onDismiss(id)}
        className="rounded-md p-1 hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-primary"
        aria-label="Dismiss"
      >
        <svg
          className="h-4 w-4 text-muted hover:text-light"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>
  );
}

interface ToastContainerProps {
  toasts: ToastType[];
  onDismiss: (id: string) => void;
}

function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  if (toasts.length === 0) return null;

  return (
    <div
      className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full"
      aria-label="Notifications"
    >
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

export { Toast, ToastContainer };
