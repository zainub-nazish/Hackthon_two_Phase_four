# Quickstart: JWT-Based Authentication

**Feature**: 001-jwt-auth
**Date**: 2026-01-12

## Overview

This guide provides step-by-step instructions for implementing JWT-based authentication between Better Auth (Next.js) and FastAPI.

---

## Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL (or your preferred database)

---

## Phase 1: Environment Setup

### 1.1 Generate Shared Secret

```bash
# Generate a 256-bit secret (run once, use in both services)
openssl rand -hex 32
# Example output: a3f8c9e2b1d4f6a7c9e2b1d4f6a7c9e2b1d4f6a7c9e2b1d4f6a7c9e2
```

### 1.2 Frontend Environment (.env.local)

```bash
# Next.js (frontend)
BETTER_AUTH_SECRET=<your-generated-secret>
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 1.3 Backend Environment (.env)

```bash
# FastAPI (backend)
BETTER_AUTH_SECRET=<same-secret-as-frontend>
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
DEBUG=true
ENVIRONMENT=development
```

---

## Phase 2: Better Auth Setup (Frontend)

### 2.1 Install Dependencies

```bash
npm install better-auth
```

### 2.2 Configure Better Auth

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  database: {
    // Your database adapter
  },
  secret: process.env.BETTER_AUTH_SECRET,
  session: {
    cookieCache: {
      enabled: true,
      strategy: "jwt",  // HS256 signed JWT
      maxAge: 60 * 5    // 5 minute cache
    }
  }
});
```

### 2.3 Create API Route Handler

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

### 2.4 Create Auth Client

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/client";

export const authClient = createAuthClient({
  baseURL: process.env.BETTER_AUTH_URL,
});
```

---

## Phase 3: FastAPI Setup (Backend)

### 3.1 Install Dependencies

```bash
pip install fastapi uvicorn python-jose[cryptography] pydantic-settings
```

### 3.2 Create Config

```python
# config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    jwt_secret: str = Field(alias="BETTER_AUTH_SECRET")
    jwt_algorithm: str = "HS256"
    database_url: str = Field(alias="DATABASE_URL")
    debug: bool = Field(default=False, alias="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### 3.3 Create Auth Dependency

```python
# auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import jwt, JWTError
from pydantic import BaseModel, Field
from typing import Optional
from config import settings

security = HTTPBearer()

class TokenPayload(BaseModel):
    sub: str = Field(..., description="User ID")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued-at timestamp")
    email: Optional[str] = None

class CurrentUser(BaseModel):
    user_id: str
    email: Optional[str] = None

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
) -> CurrentUser:
    """
    Verify JWT and extract user information.
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            key=settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp", "iat"]}
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return CurrentUser(
            user_id=user_id,
            email=payload.get("email")
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
```

### 3.4 Create Protected Routes

```python
# routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import List
from auth.dependencies import get_current_user, CurrentUser

router = APIRouter(prefix="/api/v1/users/{user_id}/tasks", tags=["Tasks"])

@router.get("")
async def list_tasks(
    user_id: str = Path(...),
    current_user: CurrentUser = Depends(get_current_user)
) -> List[TaskResponse]:
    """List all tasks for the authenticated user."""

    # Verify ownership
    if current_user.user_id != user_id:
        raise HTTPException(status_code=404, detail="Not found")

    # Fetch tasks (with owner filter)
    tasks = await db.get_tasks(owner_id=user_id)
    return tasks

@router.get("/{task_id}")
async def get_task(
    user_id: str = Path(...),
    task_id: str = Path(...),
    current_user: CurrentUser = Depends(get_current_user)
) -> TaskResponse:
    """Get a specific task."""

    # Verify ownership
    if current_user.user_id != user_id:
        raise HTTPException(status_code=404, detail="Not found")

    # Fetch task (with owner filter)
    task = await db.get_task(task_id=task_id, owner_id=user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Not found")

    return task
```

### 3.5 Create Main App

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks

app = FastAPI(
    title="Todo API",
    description="JWT-authenticated Todo API"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(tasks.router)
```

---

## Phase 4: Frontend API Integration

### 4.1 Create API Client

```typescript
// lib/api-client.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL;

async function getAuthToken(): Promise<string | null> {
  // Get JWT from Better Auth session
  const session = await authClient.getSession();
  return session?.token ?? null;
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken();

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
```

### 4.2 Use in Components

```typescript
// Example: Fetch user's tasks
import { apiClient } from "@/lib/api-client";

async function fetchTasks(userId: string) {
  return apiClient<TaskListResponse>(`/api/v1/users/${userId}/tasks`);
}
```

---

## Phase 5: Testing

### 5.1 Test JWT Verification

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient
from jose import jwt
from datetime import datetime, timedelta
from config import settings

@pytest.fixture
def valid_token():
    """Generate a valid test token"""
    payload = {
        "sub": "test-user-id",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

@pytest.fixture
def expired_token():
    """Generate an expired token"""
    payload = {
        "sub": "test-user-id",
        "exp": datetime.utcnow() - timedelta(hours=1),
        "iat": datetime.utcnow() - timedelta(hours=2)
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

async def test_protected_route_with_valid_token(client: AsyncClient, valid_token):
    response = await client.get(
        "/api/v1/users/test-user-id/tasks",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200

async def test_protected_route_without_token(client: AsyncClient):
    response = await client.get("/api/v1/users/test-user-id/tasks")
    assert response.status_code == 401

async def test_protected_route_with_expired_token(client: AsyncClient, expired_token):
    response = await client.get(
        "/api/v1/users/test-user-id/tasks",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()

async def test_cross_user_access_denied(client: AsyncClient, valid_token):
    # Token is for test-user-id, trying to access other-user-id
    response = await client.get(
        "/api/v1/users/other-user-id/tasks",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 404  # Returns 404, not 403
```

---

## Verification Checklist

- [ ] Secret generated and stored in both `.env` files
- [ ] Better Auth configured with `jwt` cookie strategy
- [ ] FastAPI `get_current_user` dependency created
- [ ] All task routes protected with dependency
- [ ] Ownership verification in all routes
- [ ] CORS configured for frontend origin
- [ ] Tests pass for valid/invalid/expired tokens
- [ ] Cross-user access returns 404

---

## Common Issues

### Token Not Sent
- Ensure `credentials: 'include'` in fetch calls
- Check CORS allows credentials

### 401 on Valid Token
- Verify same `BETTER_AUTH_SECRET` in both services
- Check algorithm matches (HS256)
- Verify token not expired

### 403 vs 404 Confusion
- Always use 404 for "access denied" to prevent info leakage
- 403 is not used in this implementation

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement authentication layer
3. Add comprehensive tests
4. Deploy with proper secret management
