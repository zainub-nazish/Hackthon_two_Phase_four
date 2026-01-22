# Data Model: Frontend Application

**Feature**: 003-frontend-app
**Date**: 2026-01-13

## Overview

The frontend data model represents the client-side TypeScript types that mirror the backend API contracts. These types ensure type safety when consuming the REST API.

## Entities

### Task

Represents a todo item owned by a user.

```typescript
interface Task {
  id: string;           // UUID
  owner_id: string;     // User ID
  title: string;        // 1-255 characters
  description: string | null;  // Optional, max 2000 chars
  completed: boolean;   // Completion status
  created_at: string;   // ISO 8601 datetime
  updated_at: string;   // ISO 8601 datetime
}
```

**Validation Rules**:
- `title`: Required, 1-255 characters
- `description`: Optional, max 2000 characters
- `completed`: Defaults to false on creation

**State Transitions**:
- `pending` → `completed` (toggle via PATCH)
- `completed` → `pending` (toggle via PATCH)

---

### TaskCreate

Request payload for creating a new task.

```typescript
interface TaskCreate {
  title: string;        // Required, 1-255 chars
  description?: string; // Optional
  completed?: boolean;  // Defaults to false
}
```

---

### TaskUpdate

Request payload for updating an existing task (partial update).

```typescript
interface TaskUpdate {
  title?: string;       // Optional update
  description?: string | null; // Optional, can be null to clear
  completed?: boolean;  // Optional update
}
```

---

### TaskListResponse

Response from the list tasks endpoint.

```typescript
interface TaskListResponse {
  items: Task[];        // Array of tasks
  total: number;        // Total count before pagination
  limit: number | null; // Requested limit
  offset: number | null; // Requested offset
}
```

---

### User (Session)

Represents the authenticated user in the frontend context.

```typescript
interface User {
  id: string;           // User ID from JWT sub claim
  email?: string;       // Email if available from token
}
```

---

### AuthState

Frontend authentication state managed by AuthContext.

```typescript
interface AuthState {
  user: User | null;    // Current user or null if not authenticated
  token: string | null; // JWT token
  isAuthenticated: boolean;
  isLoading: boolean;   // True during auth check
}
```

---

### UIState

Component-level UI state patterns.

```typescript
// Generic async state
interface AsyncState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

// Form state
interface FormState {
  isSubmitting: boolean;
  errors: Record<string, string>;
}

// Toast notification
interface Toast {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
  duration?: number;
}
```

---

### ErrorResponse

API error response structure.

```typescript
interface ErrorResponse {
  detail: string | ValidationError[];
}

interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}
```

## Relationships

```
User (1) ────────< Task (*)
  │                  │
  └── owns ──────────┘

AuthState ────── User
     │
     └── contains token for API requests

TaskListResponse ────── Task[]
     │
     └── wraps with pagination metadata
```

## Type Export Structure

```typescript
// types/index.ts
export type { Task, TaskCreate, TaskUpdate, TaskListResponse };
export type { User, AuthState };
export type { AsyncState, FormState, Toast };
export type { ErrorResponse, ValidationError };
```

## Mapping to Backend

| Frontend Type | Backend Schema | Notes |
|---------------|----------------|-------|
| Task | TaskResponse | Direct mapping |
| TaskCreate | TaskCreate | Direct mapping |
| TaskUpdate | TaskUpdate | Direct mapping |
| TaskListResponse | TaskListResponse | Direct mapping |
| User | JWT payload | Extracted from token |
