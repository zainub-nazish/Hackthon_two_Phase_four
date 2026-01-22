# Data Model: JWT-Based Authentication & Authorization

**Feature**: 001-jwt-auth
**Date**: 2026-01-12

## Overview

This document defines the data models and entities for JWT-based authentication between Better Auth (Next.js) and FastAPI. The focus is on stateless authentication without server-side session storage.

---

## Core Entities

### 1. User

The authenticated individual using the system.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string (UUID) | Yes | Unique identifier, stored in JWT `sub` claim |
| email | string | Yes | User's email address |
| name | string | No | Display name |
| created_at | datetime | Yes | Account creation timestamp |
| updated_at | datetime | Yes | Last update timestamp |

**Notes**:
- User records managed by Better Auth
- User ID is the single source of truth for identity
- Password hashing handled by Better Auth (not stored in application DB)

### 2. JWT Token (Transient)

A signed token containing user identity claims. Not persisted - exists only during request lifecycle.

| Claim | Type | Required | Description |
|-------|------|----------|-------------|
| sub | string | Yes | User ID (primary identifier) |
| exp | integer | Yes | Expiration timestamp (Unix) |
| iat | integer | Yes | Issued-at timestamp (Unix) |
| email | string | No | User's email |
| sessionId | string | No | Session identifier for tracking |

**Example Payload**:
```json
{
  "sub": "usr_abc123def456",
  "exp": 1704067200,
  "iat": 1704063600,
  "email": "user@example.com",
  "sessionId": "sess_xyz789"
}
```

### 3. Task

A user-owned resource that requires ownership verification.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string (UUID) | Yes | Unique task identifier |
| owner_id | string (UUID) | Yes | FK to User.id - ownership reference |
| title | string | Yes | Task title |
| description | string | No | Task details |
| completed | boolean | Yes | Completion status |
| created_at | datetime | Yes | Creation timestamp |
| updated_at | datetime | Yes | Last update timestamp |

**Relationships**:
- Task.owner_id → User.id (many-to-one)
- Only the owner can read/write their tasks

### 4. Protected Endpoint (Conceptual)

An API route that requires valid authentication.

| Attribute | Type | Description |
|-----------|------|-------------|
| path | string | URL path pattern (e.g., `/users/{user_id}/tasks`) |
| method | string | HTTP method (GET, POST, PUT, DELETE) |
| requires_auth | boolean | Whether JWT verification is required |
| requires_ownership | boolean | Whether user must own the resource |

---

## Data Flow

### Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│  Better Auth │────▶│   FastAPI   │
│  (Next.js)  │     │   (Next.js)  │     │   Backend   │
└─────────────┘     └─────────────┘     └─────────────┘
      │                   │                    │
      │  1. Login         │                    │
      │  (email/password) │                    │
      ├──────────────────▶│                    │
      │                   │                    │
      │  2. Verify creds  │                    │
      │  3. Generate JWT  │                    │
      │  (sign with       │                    │
      │   BETTER_AUTH_    │                    │
      │   SECRET)         │                    │
      │                   │                    │
      │  4. Return JWT    │                    │
      │  (httpOnly cookie │                    │
      │   or header)      │                    │
      │◀──────────────────│                    │
      │                   │                    │
      │  5. API Request   │                    │
      │  Authorization:   │                    │
      │  Bearer <token>   │                    │
      ├────────────────────────────────────────▶
      │                   │                    │
      │                   │  6. Verify JWT     │
      │                   │  (same SECRET)     │
      │                   │  7. Extract sub    │
      │                   │  8. Verify owner   │
      │                   │  9. Query DB       │
      │                   │                    │
      │  10. Response     │                    │
      │◀────────────────────────────────────────
```

### Token Lifecycle

```
┌──────────────┐
│  User Login  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  JWT Issued  │ iat = now
│  (Better     │ exp = now + TTL
│   Auth)      │
└──────┬───────┘
       │
       ▼
┌──────────────┐    ┌──────────────┐
│  Token Used  │───▶│  Verify JWT  │
│  (API Call)  │    │  (FastAPI)   │
└──────────────┘    └──────┬───────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
   ┌──────────────┐           ┌──────────────┐
   │    Valid     │           │   Invalid    │
   │  (proceed)   │           │  (401 error) │
   └──────┬───────┘           └──────────────┘
          │
          ▼
   ┌──────────────┐
   │  Token Exp?  │
   │   (exp < now)│
   └──────┬───────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌────────┐  ┌────────┐
│ Valid  │  │Expired │
│(200 OK)│  │ (401)  │
└────────┘  └────────┘
```

---

## Validation Rules

### JWT Validation

| Rule | Description | Error |
|------|-------------|-------|
| Signature Valid | HMAC-SHA256 with BETTER_AUTH_SECRET | 401 |
| Not Expired | exp > current_time | 401 |
| Required Claims | sub, exp, iat present | 401 |
| Valid Format | Well-formed JWT structure | 401 |

### Ownership Validation

| Rule | Description | Error |
|------|-------------|-------|
| Path Match | JWT.sub == path.user_id | 404 |
| Resource Exists | Task found in DB | 404 |
| Owner Match | Task.owner_id == JWT.sub | 404 |

---

## State Transitions

### Task States

```
┌─────────────────┐
│   Not Started   │
│ (completed=false)│
└────────┬────────┘
         │
         │ Mark complete
         ▼
┌─────────────────┐
│    Completed    │
│ (completed=true) │
└────────┬────────┘
         │
         │ Mark incomplete
         ▼
┌─────────────────┐
│   Not Started   │
└─────────────────┘
```

### Authentication States

```
┌─────────────────┐
│  Unauthenticated │
│   (no token)     │
└────────┬────────┘
         │
         │ Login successful
         ▼
┌─────────────────┐
│  Authenticated   │
│ (valid token)    │
└────────┬────────┘
         │
         │ Token expires
         ▼
┌─────────────────┐
│   Expired       │
│ (must re-login) │
└─────────────────┘
```

---

## Pydantic Models (FastAPI)

### Token Payload Model

```python
from pydantic import BaseModel, Field
from typing import Optional

class TokenPayload(BaseModel):
    """JWT claims structure from Better Auth"""
    sub: str = Field(..., description="User ID")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued-at timestamp")
    email: Optional[str] = Field(None, description="User email")
    session_id: Optional[str] = Field(None, alias="sessionId")

    class Config:
        populate_by_name = True
```

### Current User Model

```python
class CurrentUser(BaseModel):
    """Verified user extracted from JWT"""
    user_id: str = Field(..., description="Authenticated user ID")
    email: Optional[str] = None
```

### Task Models

```python
from datetime import datetime
from uuid import UUID

class TaskBase(BaseModel):
    """Base task attributes"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    completed: bool = Field(default=False)

class TaskCreate(TaskBase):
    """Create task request"""
    pass

class TaskUpdate(BaseModel):
    """Update task request (partial)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    completed: Optional[bool] = None

class TaskResponse(TaskBase):
    """Task response with all fields"""
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### Error Response Model

```python
class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str = Field(..., description="Error message")
```

---

## Database Constraints

### Tasks Table

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index for owner queries (critical for user isolation)
CREATE INDEX idx_tasks_owner_id ON tasks(owner_id);

-- Composite index for efficient ownership lookup
CREATE INDEX idx_tasks_owner_id_id ON tasks(owner_id, id);
```

---

## Security Considerations

1. **JWT Payload Size**: Keep minimal - only essential claims
2. **No Sensitive Data**: Never store passwords, secrets, or PII in JWT
3. **Owner Filtering**: Always include owner_id in database queries
4. **No Implicit Trust**: Verify ownership even with valid JWT
5. **Consistent 404**: Return same error for "not found" and "not authorized"
