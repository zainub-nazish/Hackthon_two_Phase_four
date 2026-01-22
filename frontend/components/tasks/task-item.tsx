"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import type { Task } from "@/types";

interface TaskItemProps {
  task: Task;
  onToggle: (id: string) => Promise<void>;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
}

export function TaskItem({ task, onToggle, onEdit, onDelete }: TaskItemProps) {
  const [isToggling, setIsToggling] = useState(false);

  async function handleToggle() {
    setIsToggling(true);
    try {
      await onToggle(task.id);
    } finally {
      setIsToggling(false);
    }
  }

  return (
    <div
      className={cn(
        "group flex items-start gap-3 rounded-lg border border-white/10 bg-surface p-4 transition-all duration-150",
        "hover:bg-white/5",
        task.completed && "opacity-75"
      )}
    >
      {/* Checkbox - min 44px touch target for mobile */}
      <div className="flex-shrink-0 pt-0.5">
        <button
          type="button"
          onClick={handleToggle}
          disabled={isToggling}
          className={cn(
            "h-6 w-6 sm:h-5 sm:w-5 rounded border-2 flex items-center justify-center transition-colors duration-150",
            "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-dark",
            "touch-manipulation",
            task.completed
              ? "border-success bg-success"
              : "border-white/30 hover:border-primary",
            isToggling && "opacity-50"
          )}
          aria-label={task.completed ? "Mark as pending" : "Mark as completed"}
        >
          {task.completed && (
            <svg
              className="h-4 w-4 sm:h-3 sm:w-3 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={3}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M5 13l4 4L19 7"
              />
            </svg>
          )}
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <h3
            className={cn(
              "text-sm font-medium text-light transition-colors duration-150",
              task.completed && "text-muted line-through"
            )}
          >
            {task.title}
          </h3>
          {/* Status Badge */}
          <span
            className={cn(
              "px-2 py-0.5 rounded-full text-xs font-medium",
              task.completed
                ? "bg-success/20 text-success"
                : "bg-secondary/20 text-secondary"
            )}
          >
            {task.completed ? "Completed" : "Pending"}
          </span>
        </div>
        {task.description && (
          <p
            className={cn(
              "mt-1 text-sm text-muted line-clamp-2",
              task.completed && "text-muted/70"
            )}
          >
            {task.description}
          </p>
        )}
        <p className="mt-2 text-xs text-muted">
          {new Date(task.created_at).toLocaleDateString()}
        </p>
      </div>

      {/* Actions - visible on mobile, hover on desktop, min 44px touch targets */}
      <div className="flex-shrink-0 flex items-center gap-1 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onEdit(task)}
          className="h-10 w-10 sm:h-8 sm:w-8 p-0 touch-manipulation"
          aria-label="Edit task"
        >
          <svg
            className="h-5 w-5 sm:h-4 sm:w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
            />
          </svg>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDelete(task.id)}
          className="h-10 w-10 sm:h-8 sm:w-8 p-0 text-danger hover:text-danger hover:bg-danger/10 touch-manipulation"
          aria-label="Delete task"
        >
          <svg
            className="h-5 w-5 sm:h-4 sm:w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </Button>
      </div>
    </div>
  );
}
