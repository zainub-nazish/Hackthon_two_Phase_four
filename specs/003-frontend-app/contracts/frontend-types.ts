/**
 * Frontend TypeScript Types
 *
 * Contract types for the Todo Application frontend.
 * These types mirror the backend API schemas for type-safe API consumption.
 *
 * Feature: 003-frontend-app
 * Generated: 2026-01-13
 */

// =============================================================================
// Task Types
// =============================================================================

/**
 * Task entity as returned from the API.
 */
export interface Task {
  /** Unique task identifier (UUID) */
  id: string;
  /** User ID of task owner */
  owner_id: string;
  /** Task title (1-255 characters) */
  title: string;
  /** Optional task description (max 2000 characters) */
  description: string | null;
  /** Whether the task is completed */
  completed: boolean;
  /** ISO 8601 creation timestamp */
  created_at: string;
  /** ISO 8601 last update timestamp */
  updated_at: string;
}

/**
 * Request body for creating a new task.
 */
export interface TaskCreate {
  /** Task title (required, 1-255 characters) */
  title: string;
  /** Optional task description (max 2000 characters) */
  description?: string;
  /** Initial completion status (defaults to false) */
  completed?: boolean;
}

/**
 * Request body for updating an existing task (partial update).
 */
export interface TaskUpdate {
  /** Updated title (optional) */
  title?: string;
  /** Updated description (optional, can be null to clear) */
  description?: string | null;
  /** Updated completion status (optional) */
  completed?: boolean;
}

/**
 * Paginated list response for tasks.
 */
export interface TaskListResponse {
  /** Array of tasks */
  items: Task[];
  /** Total count of tasks (before pagination) */
  total: number;
  /** Requested limit */
  limit: number | null;
  /** Requested offset */
  offset: number | null;
}

/**
 * Query parameters for listing tasks.
 */
export interface TaskListParams {
  /** Filter by completion status */
  completed?: boolean;
  /** Maximum number of tasks to return (1-100) */
  limit?: number;
  /** Number of tasks to skip */
  offset?: number;
}

// =============================================================================
// Authentication Types
// =============================================================================

/**
 * Authenticated user information.
 */
export interface User {
  /** User ID (from JWT sub claim) */
  id: string;
  /** User email (if available from token) */
  email?: string;
}

/**
 * Session response from auth verification endpoint.
 */
export interface SessionResponse {
  /** Authenticated user ID */
  user_id: string;
  /** User email if available */
  email?: string;
  /** Authentication status */
  authenticated: boolean;
}

/**
 * Frontend authentication state.
 */
export interface AuthState {
  /** Current authenticated user (null if not authenticated) */
  user: User | null;
  /** JWT token (null if not authenticated) */
  token: string | null;
  /** Whether user is authenticated */
  isAuthenticated: boolean;
  /** Whether auth check is in progress */
  isLoading: boolean;
}

// =============================================================================
// API Error Types
// =============================================================================

/**
 * Standard API error response.
 */
export interface ErrorResponse {
  /** Human-readable error message or validation errors */
  detail: string | ValidationError[];
}

/**
 * Validation error detail (from 422 responses).
 */
export interface ValidationError {
  /** Location of the error (e.g., ["body", "title"]) */
  loc: (string | number)[];
  /** Error message */
  msg: string;
  /** Error type identifier */
  type: string;
}

// =============================================================================
// UI State Types
// =============================================================================

/**
 * Generic async state for data fetching.
 */
export interface AsyncState<T> {
  /** Fetched data (null if not loaded or error) */
  data: T | null;
  /** Whether fetch is in progress */
  isLoading: boolean;
  /** Error message (null if no error) */
  error: string | null;
}

/**
 * Form submission state.
 */
export interface FormState {
  /** Whether form is being submitted */
  isSubmitting: boolean;
  /** Field-level validation errors */
  errors: Record<string, string>;
}

/**
 * Toast notification.
 */
export interface Toast {
  /** Unique toast ID */
  id: string;
  /** Toast type (determines styling) */
  type: "success" | "error" | "info" | "warning";
  /** Toast message */
  message: string;
  /** Auto-dismiss duration in ms (default: 5000) */
  duration?: number;
}

// =============================================================================
// API Endpoint Contracts
// =============================================================================

/**
 * API endpoint definitions.
 * Base URL: Configured via NEXT_PUBLIC_API_URL environment variable.
 */
export const API_ENDPOINTS = {
  AUTH_SESSION: "/api/v1/auth/session",
  TASKS: (userId: string) => `/api/v1/users/${userId}/tasks`,
  TASK: (userId: string, taskId: string) => `/api/v1/users/${userId}/tasks/${taskId}`,
} as const;
