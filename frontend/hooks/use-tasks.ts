"use client";

import { useState, useCallback, useEffect } from "react";
import { get, post, patch, del, ApiError } from "@/lib/api-client";
import { useAuth } from "@/hooks/use-auth";
import type {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskListResponse,
  TaskListParams,
  AsyncState,
} from "@/types";

interface UseTasksReturn extends AsyncState<Task[]> {
  total: number;
  fetchTasks: (params?: TaskListParams) => Promise<void>;
  createTask: (data: TaskCreate) => Promise<Task>;
  updateTask: (id: string, data: TaskUpdate) => Promise<Task>;
  toggleComplete: (id: string) => Promise<Task>;
  deleteTask: (id: string) => Promise<void>;
  refreshTasks: () => Promise<void>;
}

export function useTasks(initialParams?: TaskListParams): UseTasksReturn {
  const { user } = useAuth();
  const [data, setData] = useState<Task[] | null>(null);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentParams, setCurrentParams] = useState<TaskListParams | undefined>(initialParams);

  const getTasksEndpoint = useCallback(
    (params?: TaskListParams) => {
      if (!user?.id) return null;

      const queryParams = new URLSearchParams();
      if (params?.completed !== undefined) {
        queryParams.set("completed", String(params.completed));
      }
      if (params?.limit) {
        queryParams.set("limit", String(params.limit));
      }
      if (params?.offset) {
        queryParams.set("offset", String(params.offset));
      }

      const queryString = queryParams.toString();
      return `/api/v1/users/${user.id}/tasks${queryString ? `?${queryString}` : ""}`;
    },
    [user?.id]
  );

  const fetchTasks = useCallback(
    async (params?: TaskListParams) => {
      const endpoint = getTasksEndpoint(params);
      if (!endpoint) {
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);
      setCurrentParams(params);

      try {
        const response = await get<TaskListResponse>(endpoint);
        setData(response.items);
        setTotal(response.total);
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : "Failed to fetch tasks";
        setError(message);
        setData(null);
      } finally {
        setIsLoading(false);
      }
    },
    [getTasksEndpoint]
  );

  const refreshTasks = useCallback(() => {
    return fetchTasks(currentParams);
  }, [fetchTasks, currentParams]);

  const createTask = useCallback(
    async (taskData: TaskCreate): Promise<Task> => {
      if (!user?.id) {
        throw new Error("Not authenticated");
      }

      const endpoint = `/api/v1/users/${user.id}/tasks`;
      const newTask = await post<Task>(endpoint, taskData);

      // Add to local state
      setData((prev) => (prev ? [newTask, ...prev] : [newTask]));
      setTotal((prev) => prev + 1);

      return newTask;
    },
    [user?.id]
  );

  const updateTask = useCallback(
    async (id: string, taskData: TaskUpdate): Promise<Task> => {
      if (!user?.id) {
        throw new Error("Not authenticated");
      }

      const endpoint = `/api/v1/users/${user.id}/tasks/${id}`;
      const updatedTask = await patch<Task>(endpoint, taskData);

      // Update local state
      setData((prev) =>
        prev
          ? prev.map((task) => (task.id === id ? updatedTask : task))
          : null
      );

      return updatedTask;
    },
    [user?.id]
  );

  const toggleComplete = useCallback(
    async (id: string): Promise<Task> => {
      if (!user?.id) {
        throw new Error("Not authenticated");
      }

      // Find current task state for optimistic update
      const currentTask = data?.find((t) => t.id === id);
      if (!currentTask) {
        throw new Error("Task not found");
      }

      // Optimistic update
      const optimisticTask = { ...currentTask, completed: !currentTask.completed };
      setData((prev) =>
        prev ? prev.map((t) => (t.id === id ? optimisticTask : t)) : null
      );

      try {
        const endpoint = `/api/v1/users/${user.id}/tasks/${id}`;
        const updatedTask = await patch<Task>(endpoint, {
          completed: !currentTask.completed,
        });

        // Update with server response
        setData((prev) =>
          prev ? prev.map((t) => (t.id === id ? updatedTask : t)) : null
        );

        return updatedTask;
      } catch (err) {
        // Rollback on error
        setData((prev) =>
          prev ? prev.map((t) => (t.id === id ? currentTask : t)) : null
        );
        throw err;
      }
    },
    [user?.id, data]
  );

  const deleteTask = useCallback(
    async (id: string): Promise<void> => {
      if (!user?.id) {
        throw new Error("Not authenticated");
      }

      const endpoint = `/api/v1/users/${user.id}/tasks/${id}`;
      await del(endpoint);

      // Remove from local state
      setData((prev) => (prev ? prev.filter((task) => task.id !== id) : null));
      setTotal((prev) => Math.max(0, prev - 1));
    },
    [user?.id]
  );

  // Initial fetch
  useEffect(() => {
    if (user?.id) {
      fetchTasks(initialParams);
    }
  }, [user?.id, fetchTasks, initialParams]);

  return {
    data,
    total,
    isLoading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    toggleComplete,
    deleteTask,
    refreshTasks,
  };
}
