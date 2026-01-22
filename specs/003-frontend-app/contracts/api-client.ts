/**
 * API Client Contract: Frontend Application
 *
 * This file defines the TypeScript interface contract for the API client.
 * Implementation should follow this contract exactly.
 *
 * Feature: 003-frontend-app
 * Date: 2026-01-13
 */

// =============================================================================
// Type Definitions (from data-model.md)
// =============================================================================

export interface Task {
  id: string;
  owner_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  completed?: boolean;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  completed?: boolean;
}

export interface TaskListResponse {
  items: Task[];
  total: number;
  limit: number | null;
  offset: number | null;
}

export interface TaskListParams {
  completed?: boolean;
  limit?: number;
  offset?: number;
}

export interface ErrorResponse {
  detail: string | ValidationError[];
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

// =============================================================================
// API Client Interface
// =============================================================================

export interface ApiClientConfig {
  baseUrl: string;
  getToken: () => string | null;
  onUnauthorized?: () => void;
}

export interface ApiClient {
  // Task Operations
  tasks: {
    list(userId: string, params?: TaskListParams): Promise<TaskListResponse>;
    create(userId: string, data: TaskCreate): Promise<Task>;
    get(userId: string, taskId: string): Promise<Task>;
    update(userId: string, taskId: string, data: TaskUpdate): Promise<Task>;
    delete(userId: string, taskId: string): Promise<void>;
  };
}

// =============================================================================
// API Response Handling
// =============================================================================

export type ApiResult<T> =
  | { success: true; data: T }
  | { success: false; error: string; status: number };

export interface ApiError extends Error {
  status: number;
  detail: string;
}

// =============================================================================
// Factory Function Signature
// =============================================================================

export type CreateApiClient = (config: ApiClientConfig) => ApiClient;

// =============================================================================
// Usage Example (for implementation reference)
// =============================================================================

/**
 * Example usage:
 *
 * ```typescript
 * const client = createApiClient({
 *   baseUrl: 'http://localhost:8000',
 *   getToken: () => localStorage.getItem('auth_token'),
 *   onUnauthorized: () => router.push('/login'),
 * });
 *
 * // List tasks
 * const response = await client.tasks.list(userId, { completed: false });
 *
 * // Create task
 * const newTask = await client.tasks.create(userId, { title: 'New task' });
 *
 * // Toggle completion
 * const updated = await client.tasks.update(userId, taskId, { completed: true });
 *
 * // Delete task
 * await client.tasks.delete(userId, taskId);
 * ```
 */
