"use client";

import { TaskItem } from "./task-item";
import { EmptyState } from "./empty-state";
import { Spinner } from "@/components/ui/spinner";
import type { Task, TaskFilter } from "@/types";

interface TaskListProps {
  tasks: Task[] | null;
  isLoading: boolean;
  error: string | null;
  filter: TaskFilter;
  onToggle: (id: string) => Promise<void>;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
  onAddTask?: () => void;
}

export function TaskList({
  tasks,
  isLoading,
  error,
  filter,
  onToggle,
  onEdit,
  onDelete,
  onAddTask,
}: TaskListProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-danger/30 bg-danger/20 p-4 text-center">
        <p className="text-sm text-danger">{error}</p>
      </div>
    );
  }

  if (!tasks || tasks.length === 0) {
    const emptyMessages = {
      all: {
        title: "No tasks yet",
        description: "Get started by creating your first task.",
      },
      pending: {
        title: "No pending tasks",
        description: "All tasks are completed! Great job!",
      },
      completed: {
        title: "No completed tasks",
        description: "Complete a task to see it here.",
      },
    };

    const { title, description } = emptyMessages[filter];

    return (
      <EmptyState
        title={title}
        description={description}
        action={
          filter === "all" && onAddTask
            ? { label: "Add task", onClick: onAddTask }
            : undefined
        }
      />
    );
  }

  return (
    <ul className="space-y-3" role="list" aria-label="Task list">
      {tasks.map((task) => (
        <li key={task.id}>
          <TaskItem
            task={task}
            onToggle={onToggle}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        </li>
      ))}
    </ul>
  );
}
