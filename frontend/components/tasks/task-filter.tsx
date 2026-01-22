"use client";

import { cn } from "@/lib/utils";
import type { TaskFilter } from "@/types";

interface TaskFilterProps {
  value: TaskFilter;
  onChange: (filter: TaskFilter) => void;
  counts?: {
    all: number;
    pending: number;
    completed: number;
  };
}

const filters: { value: TaskFilter; label: string }[] = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "completed", label: "Completed" },
];

export function TaskFilterTabs({ value, onChange, counts }: TaskFilterProps) {
  return (
    <div className="flex gap-1 rounded-lg bg-surface p-1" role="tablist">
      {filters.map((filter) => {
        const count = counts?.[filter.value];
        const isActive = value === filter.value;

        return (
          <button
            key={filter.value}
            type="button"
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange(filter.value)}
            className={cn(
              "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
              "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-dark",
              isActive
                ? "bg-dark text-light border border-primary"
                : "text-muted hover:text-light"
            )}
          >
            {filter.label}
            {count !== undefined && (
              <span
                className={cn(
                  "rounded-full px-1.5 py-0.5 text-xs",
                  isActive
                    ? "bg-primary/20 text-primary"
                    : "bg-white/10 text-muted"
                )}
              >
                {count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
