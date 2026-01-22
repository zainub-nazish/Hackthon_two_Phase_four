"use client";

import { useState, useMemo, useCallback } from "react";
import { useTasks } from "@/hooks/use-tasks";
import { useToast } from "@/hooks/use-toast";
import { TaskList } from "@/components/tasks/task-list";
import { TaskFilterTabs } from "@/components/tasks/task-filter";
import { TaskForm } from "@/components/tasks/task-form";
import { DeleteDialog } from "@/components/tasks/delete-dialog";
import { Button } from "@/components/ui/button";
import { ToastContainer } from "@/components/ui/toast";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { Task, TaskFilter, TaskCreate, TaskUpdate } from "@/types";

export default function TasksPage() {
  const {
    data: tasks,
    isLoading,
    error,
    createTask,
    updateTask,
    toggleComplete,
    deleteTask,
  } = useTasks();

  const { toasts, dismissToast, success, error: showError } = useToast();

  const [filter, setFilter] = useState<TaskFilter>("all");
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [deletingTaskId, setDeletingTaskId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Filter tasks based on current filter
  const filteredTasks = useMemo(() => {
    if (!tasks) return null;

    switch (filter) {
      case "pending":
        return tasks.filter((t) => !t.completed);
      case "completed":
        return tasks.filter((t) => t.completed);
      default:
        return tasks;
    }
  }, [tasks, filter]);

  // Calculate counts for filter tabs
  const counts = useMemo(() => {
    if (!tasks) return undefined;
    return {
      all: tasks.length,
      pending: tasks.filter((t) => !t.completed).length,
      completed: tasks.filter((t) => t.completed).length,
    };
  }, [tasks]);

  // Get the task being deleted (for dialog title)
  const deletingTask = useMemo(
    () => tasks?.find((t) => t.id === deletingTaskId),
    [tasks, deletingTaskId]
  );

  // Handle task creation
  const handleCreate = useCallback(
    async (data: TaskCreate | TaskUpdate) => {
      setIsSubmitting(true);
      try {
        await createTask(data as TaskCreate);
        setIsAddDialogOpen(false);
        success("Task created successfully");
      } catch (err) {
        showError(err instanceof Error ? err.message : "Failed to create task");
      } finally {
        setIsSubmitting(false);
      }
    },
    [createTask, success, showError]
  );

  // Handle task update
  const handleUpdate = useCallback(
    async (data: TaskCreate | TaskUpdate) => {
      if (!editingTask) return;

      setIsSubmitting(true);
      try {
        await updateTask(editingTask.id, data as TaskUpdate);
        setEditingTask(null);
        success("Task updated successfully");
      } catch (err) {
        showError(err instanceof Error ? err.message : "Failed to update task");
      } finally {
        setIsSubmitting(false);
      }
    },
    [editingTask, updateTask, success, showError]
  );

  // Handle toggle complete
  const handleToggle = useCallback(
    async (id: string) => {
      try {
        await toggleComplete(id);
      } catch (err) {
        showError(err instanceof Error ? err.message : "Failed to update task");
      }
    },
    [toggleComplete, showError]
  );

  // Handle delete
  const handleDelete = useCallback(async () => {
    if (!deletingTaskId) return;

    setIsSubmitting(true);
    try {
      await deleteTask(deletingTaskId);
      setDeletingTaskId(null);
      success("Task deleted successfully");
    } catch (err) {
      showError(err instanceof Error ? err.message : "Failed to delete task");
    } finally {
      setIsSubmitting(false);
    }
  }, [deletingTaskId, deleteTask, success, showError]);

  return (
    <div className="space-y-6">
      {/* Dashboard Header */}
      <div className="text-center py-4">
        <h1 className="text-3xl font-bold text-light">Manage Your Tasks</h1>
        <p className="mt-2 text-muted">
          Plan, track, and complete efficiently
        </p>
      </div>

      {/* Tasks Section Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-light">Your Tasks</h2>
          <p className="mt-1 text-sm text-muted">
            Manage your tasks and stay organized
          </p>
        </div>
        <Button onClick={() => setIsAddDialogOpen(true)}>
          <svg
            className="mr-2 h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          Add task
        </Button>
      </div>

      {/* Filter tabs */}
      <TaskFilterTabs value={filter} onChange={setFilter} counts={counts} />

      {/* Task list */}
      <TaskList
        tasks={filteredTasks}
        isLoading={isLoading}
        error={error}
        filter={filter}
        onToggle={handleToggle}
        onEdit={setEditingTask}
        onDelete={setDeletingTaskId}
        onAddTask={() => setIsAddDialogOpen(true)}
      />

      {/* Add task dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add new task</DialogTitle>
          </DialogHeader>
          <TaskForm
            onSubmit={handleCreate}
            onCancel={() => setIsAddDialogOpen(false)}
            isLoading={isSubmitting}
          />
        </DialogContent>
      </Dialog>

      {/* Edit task dialog */}
      <Dialog
        open={!!editingTask}
        onOpenChange={(open) => !open && setEditingTask(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit task</DialogTitle>
          </DialogHeader>
          {editingTask && (
            <TaskForm
              initialData={editingTask}
              onSubmit={handleUpdate}
              onCancel={() => setEditingTask(null)}
              isLoading={isSubmitting}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Delete confirmation dialog */}
      <DeleteDialog
        open={!!deletingTaskId}
        onOpenChange={(open) => !open && setDeletingTaskId(null)}
        onConfirm={handleDelete}
        isLoading={isSubmitting}
        taskTitle={deletingTask?.title}
      />

      {/* Toast notifications */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}
