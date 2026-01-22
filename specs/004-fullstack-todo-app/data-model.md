# Data Model: Todo Full-Stack Web Application

**Feature**: 004-fullstack-todo-app
**Date**: 2026-01-15
**Source**: [spec.md](./spec.md) Key Entities section

## Entity Overview

```
┌─────────────────┐     1:N     ┌─────────────────┐
│      User       │─────────────│     Session     │
│  (Better Auth)  │             │  (Better Auth)  │
└────────┬────────┘             └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│      Task       │
│   (Backend)     │
└─────────────────┘
```

---

## Entities

### 1. User (Managed by Better Auth)

**Description**: Represents an authenticated user in the system. Managed entirely by Better Auth library.

**Table**: `user` (created by Better Auth)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | VARCHAR(32) | PK, NOT NULL | Unique identifier (Better Auth format) |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| name | VARCHAR(255) | NULL | Optional display name |
| emailVerified | BOOLEAN | DEFAULT FALSE | Email verification status |
| image | TEXT | NULL | Profile image URL |
| createdAt | TIMESTAMP | NOT NULL | Account creation timestamp |
| updatedAt | TIMESTAMP | NOT NULL | Last update timestamp |

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Email must be unique across all users

**Notes**: Do not modify this table directly. Better Auth manages all user operations.

---

### 2. Session (Managed by Better Auth)

**Description**: Represents an active user session. Managed by Better Auth library.

**Table**: `session` (created by Better Auth)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | VARCHAR(32) | PK, NOT NULL | Session identifier |
| userId | VARCHAR(32) | FK -> user.id, NOT NULL | Owner of session |
| token | VARCHAR(255) | UNIQUE, NOT NULL | Session token for API auth |
| expiresAt | TIMESTAMP | NOT NULL | Session expiration time |
| ipAddress | VARCHAR(45) | NULL | Client IP address |
| userAgent | TEXT | NULL | Client user agent |
| createdAt | TIMESTAMP | NOT NULL | Session creation time |
| updatedAt | TIMESTAMP | NOT NULL | Last activity time |

**Validation Rules**:
- Token must be cryptographically random
- expiresAt default: 7 days from creation
- Session refreshed on activity (updateAge: 24 hours)

**Notes**: Backend verifies sessions by querying this table directly.

---

### 3. Task (Managed by Backend)

**Description**: Represents a todo item owned by a user.

**Table**: `tasks`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, DEFAULT uuid4() | Unique task identifier |
| owner_id | VARCHAR(32) | FK -> user.id, INDEX, NOT NULL | Task owner |
| title | VARCHAR(255) | NOT NULL | Task title |
| description | VARCHAR(2000) | NULL | Optional task description |
| completed | BOOLEAN | DEFAULT FALSE, NOT NULL | Completion status |
| created_at | TIMESTAMP | DEFAULT NOW(), NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW(), NOT NULL | Last update timestamp |

**Validation Rules**:
- Title: Required, 1-255 characters
- Description: Optional, max 2000 characters
- owner_id must reference valid user
- completed must be boolean

**State Transitions**:
```
[Created] ──toggle──> [Completed]
    ▲                      │
    │                      │
    └───────toggle─────────┘
```

**Indexes**:
- `idx_tasks_owner_id` on `owner_id` for user task queries
- Primary key on `id`

---

## Relationships

### User -> Task (One-to-Many)
- One user can have many tasks
- Each task belongs to exactly one user
- Deleting a user should cascade delete tasks (if implemented)
- Tasks are isolated by `owner_id` - users cannot access others' tasks

### User -> Session (One-to-Many)
- One user can have multiple active sessions (multi-device)
- Session references user via `userId`
- Managed by Better Auth

---

## SQLModel Implementation (Backend)

```python
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique task identifier"
    )
    owner_id: str = Field(
        index=True,
        nullable=False,
        description="User ID from session"
    )
    title: str = Field(
        max_length=255,
        nullable=False,
        description="Task title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional task description"
    )
    completed: bool = Field(
        default=False,
        nullable=False,
        description="Task completion status"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp"
    )
```

---

## TypeScript Types (Frontend)

```typescript
// User type (from Better Auth session)
interface User {
  id: string;
  email: string;
  name?: string;
}

// Task type (from backend API)
interface Task {
  id: string;           // UUID as string
  owner_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;   // ISO 8601 timestamp
  updated_at: string;   // ISO 8601 timestamp
}

// Task creation payload
interface TaskCreate {
  title: string;
  description?: string;
  completed?: boolean;
}

// Task update payload (partial)
interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}
```

---

## Database Notes

**Shared Database**: Both Better Auth (frontend) and backend share the same Neon PostgreSQL database.

**Table Ownership**:
- `user`, `session`, `account`, `verification`: Better Auth
- `tasks`: Backend application

**Connection Strings**:
- Frontend (Better Auth): Standard PostgreSQL (`postgresql://...`)
- Backend (asyncpg): Async format (`postgresql+asyncpg://...?ssl=require`)
