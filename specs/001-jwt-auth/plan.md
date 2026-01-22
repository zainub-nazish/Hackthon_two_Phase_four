# Implementation Plan: JWT-Based Authentication & Authorization

**Branch**: `001-jwt-auth` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-jwt-auth/spec.md`

## Summary

Implement stateless JWT-based authentication between Better Auth (Next.js frontend) and FastAPI (Python backend). The system uses HS256-signed JWTs with a shared secret (`BETTER_AUTH_SECRET`) to authenticate API requests and enforce strict user isolation for task resources.

**Key Technical Approach**:
- Better Auth issues JWT tokens using `jwt` cookie cache strategy (HS256)
- Frontend attaches JWT via `Authorization: Bearer <token>` header
- FastAPI verifies JWT using `python-jose` library via dependency injection
- User ID extracted from JWT `sub` claim for ownership verification
- All protected endpoints return 404 for unauthorized access (IDOR prevention)

---

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Node.js 18+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.109+, python-jose[cryptography], pydantic-settings 2.0+
- Frontend: Next.js 14+, Better Auth (latest)

**Storage**: PostgreSQL (tasks table with owner_id foreign key)
**Testing**: pytest (backend), Jest/Vitest (frontend)
**Target Platform**: Web application (Linux server deployment)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <50ms JWT verification latency, 100 concurrent authenticated requests
**Constraints**: Stateless authentication only (no server-side sessions), shared secret via environment variable
**Scale/Scope**: Multi-user task application, strict user data isolation

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution template has not been customized for this project. Using standard security and development best practices:

| Principle | Status | Notes |
|-----------|--------|-------|
| Security First | PASS | JWT verification, user isolation, 404 for unauthorized |
| Environment Secrets | PASS | BETTER_AUTH_SECRET via env var, not hardcoded |
| Smallest Viable Change | PASS | Auth layer only, no extra features |
| Testable Components | PASS | Dependency injection enables easy mocking |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-jwt-auth/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output - technology decisions
├── data-model.md        # Phase 1 output - entity definitions
├── quickstart.md        # Phase 1 output - implementation guide
├── contracts/
│   └── openapi.yaml     # Phase 1 output - API contracts
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
# Web application structure
backend/
├── main.py                 # FastAPI application entry
├── config.py               # Settings with BETTER_AUTH_SECRET
├── auth/
│   ├── __init__.py
│   └── dependencies.py     # JWT verification dependency
├── routes/
│   ├── __init__.py
│   └── tasks.py            # Protected task endpoints
├── models/
│   ├── __init__.py
│   └── schemas.py          # Pydantic models
└── tests/
    ├── __init__.py
    ├── conftest.py         # Test fixtures (tokens)
    └── test_auth.py        # JWT verification tests

frontend/
├── lib/
│   ├── auth.ts             # Better Auth configuration
│   ├── auth-client.ts      # Client-side auth helper
│   └── api-client.ts       # API client with JWT attachment
├── app/
│   └── api/
│       └── auth/
│           └── [...all]/
│               └── route.ts # Better Auth handler
└── tests/
    └── auth.test.ts        # Frontend auth tests
```

**Structure Decision**: Web application with separate `backend/` and `frontend/` directories. Backend uses FastAPI with modular auth, routes, and models. Frontend uses Next.js App Router with Better Auth integration.

---

## Architecture Overview

### High-Level Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AUTHENTICATION FLOW                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────┐     ┌─────────────┐     ┌────────────┐     ┌──────────┐  │
│   │  User    │────▶│  Next.js    │────▶│  Better    │────▶│  JWT     │  │
│   │  Login   │     │  Frontend   │     │  Auth      │     │  Token   │  │
│   └──────────┘     └─────────────┘     └────────────┘     └────┬─────┘  │
│                                                                 │        │
│                          ┌──────────────────────────────────────┘        │
│                          │                                               │
│                          ▼                                               │
│   ┌──────────┐     ┌─────────────┐     ┌────────────┐     ┌──────────┐  │
│   │  Task    │◀────│  FastAPI    │◀────│  JWT       │◀────│ API Req  │  │
│   │  Data    │     │  Backend    │     │  Verify    │     │ + Token  │  │
│   └──────────┘     └─────────────┘     └────────────┘     └──────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### JWT Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          JWT LIFECYCLE                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. ISSUE                 2. ATTACH                 3. VERIFY            │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐        │
│  │ Better Auth │         │ Frontend    │         │ FastAPI     │        │
│  │ signs JWT   │────────▶│ adds Bearer │────────▶│ verifies    │        │
│  │ with secret │         │ header      │         │ signature   │        │
│  └─────────────┘         └─────────────┘         └──────┬──────┘        │
│                                                          │               │
│  4. DECODE                5. ENFORCE                     │               │
│  ┌─────────────┐         ┌─────────────┐                │               │
│  │ Extract     │◀────────│ Check user  │◀───────────────┘               │
│  │ sub claim   │         │ owns task   │                                │
│  └─────────────┘         └─────────────┘                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Request Flow with Middleware

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       REQUEST PROCESSING FLOW                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Request arrives                                                         │
│       │                                                                  │
│       ▼                                                                  │
│  ┌─────────────┐                                                        │
│  │ HTTPBearer  │  Extract Authorization header                          │
│  │ Security    │  Format: "Bearer <token>"                              │
│  └──────┬──────┘                                                        │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────┐                                                        │
│  │ get_current │  Dependency injection                                  │
│  │ _user()     │  - Verify signature (HS256)                            │
│  │             │  - Check expiration                                    │
│  │             │  - Extract sub claim                                   │
│  └──────┬──────┘                                                        │
│         │                                                               │
│    ┌────┴────┐                                                          │
│    │         │                                                          │
│    ▼         ▼                                                          │
│  VALID    INVALID                                                       │
│    │         │                                                          │
│    │         └──▶ 401 Unauthorized                                      │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────┐                                                        │
│  │ Route       │  - user.sub == path.user_id?                           │
│  │ Handler     │  - Query DB with owner_id                              │
│  └──────┬──────┘                                                        │
│         │                                                               │
│    ┌────┴────┐                                                          │
│    │         │                                                          │
│    ▼         ▼                                                          │
│  OWNER    NOT OWNER                                                     │
│    │         │                                                          │
│    │         └──▶ 404 Not Found                                         │
│    │                                                                    │
│    ▼                                                                    │
│  200 OK + Data                                                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Architectural Decisions

### ADR-001: JWT-Based Stateless Authentication

**Decision**: Use stateless JWT authentication instead of server-side sessions.

**Context**: Need authentication between separate frontend (Next.js) and backend (FastAPI) services.

**Rationale**:
- No session state to manage on backend
- Scales horizontally without session affinity
- Token contains all needed user info
- Better Auth supports JWT cookie strategy

**Consequences**:
- Token revocation requires short expiration + refresh pattern
- Token size affects request payload
- Must protect against XSS (httpOnly cookies)

### ADR-002: Dependency Injection over Middleware

**Decision**: Implement JWT verification via FastAPI dependency injection, not middleware.

**Context**: Need to protect routes while allowing some public endpoints.

**Rationale**:
- Fine-grained control per route
- Easier testing with dependency overrides
- Aligns with FastAPI design philosophy
- Clear, explicit dependencies

**Consequences**:
- Must remember to add dependency to each protected route
- Slightly more boilerplate than global middleware

### ADR-003: 404 for Unauthorized Access (IDOR Prevention)

**Decision**: Return HTTP 404 for both "not found" and "access denied" scenarios.

**Context**: Need to prevent information leakage about resource existence.

**Rationale**:
- OWASP recommendation for IDOR prevention
- Attacker cannot enumerate resources
- Consistent user experience

**Consequences**:
- Less specific error messages for legitimate users
- Must document expected behavior for debugging

---

## Implementation Phases

### Phase 1: Foundation

**Objective**: Set up authentication infrastructure

1. Configure environment variables (shared secret)
2. Create FastAPI config with pydantic-settings
3. Implement JWT verification dependency
4. Create TokenPayload and CurrentUser models

**Deliverables**:
- `backend/config.py`
- `backend/auth/dependencies.py`
- `backend/models/schemas.py`

### Phase 2: Backend Integration

**Objective**: Protect API endpoints

1. Create task routes with authentication
2. Implement ownership verification
3. Add consistent error responses
4. Configure CORS for frontend

**Deliverables**:
- `backend/routes/tasks.py`
- `backend/main.py`

### Phase 3: Frontend Integration

**Objective**: Connect frontend to authenticated backend

1. Configure Better Auth with JWT strategy
2. Create API client with token attachment
3. Create auth route handler
4. Wire up auth client

**Deliverables**:
- `frontend/lib/auth.ts`
- `frontend/lib/auth-client.ts`
- `frontend/lib/api-client.ts`
- `frontend/app/api/auth/[...all]/route.ts`

### Phase 4: Validation

**Objective**: Verify security requirements

1. Test valid token authentication
2. Test expired token rejection
3. Test invalid signature rejection
4. Test cross-user access prevention
5. Test missing token handling

**Deliverables**:
- `backend/tests/test_auth.py`
- `frontend/tests/auth.test.ts`

---

## Security Checkpoints

| Checkpoint | Verification Method | Expected Result |
|------------|---------------------|-----------------|
| Token signature | Send tampered token | 401 Unauthorized |
| Token expiration | Send expired token | 401 Unauthorized |
| Missing token | Send no Authorization header | 401 Unauthorized |
| Wrong user access | User A access User B's task | 404 Not Found |
| Secret not set | Unset BETTER_AUTH_SECRET | Application fails to start |
| Clock skew | Token with slight time diff | Request succeeds (10s leeway) |

---

## Testing Strategy

### Unit Tests (Backend)

```python
# Test categories
1. JWT Verification
   - Valid token → 200 OK
   - Expired token → 401 Unauthorized
   - Invalid signature → 401 Unauthorized
   - Missing claims → 401 Unauthorized
   - Malformed token → 401 Unauthorized

2. Ownership Verification
   - Own resource → 200 OK
   - Other user's resource → 404 Not Found
   - Non-existent resource → 404 Not Found

3. Configuration
   - Missing secret → Startup failure
   - Valid secret → Normal operation
```

### Integration Tests

```python
# End-to-end scenarios
1. Login → Get Token → Access Tasks → Success
2. Login → Get Token → Access Other User's Tasks → 404
3. Login → Wait for Expiry → Access Tasks → 401
4. No Login → Access Tasks → 401
```

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Secret exposure | Medium | Critical | Use env vars, never commit |
| Token theft (XSS) | Medium | High | httpOnly cookies, CSP headers |
| Clock skew issues | Low | Medium | 10-second leeway in verification |
| Brute force | Low | Medium | Rate limiting (future feature) |

---

## Dependencies

### Required Packages

**Backend (Python)**:
```
fastapi>=0.109.0
uvicorn>=0.27.0
python-jose[cryptography]>=3.3.0
pydantic-settings>=2.0.0
```

**Frontend (Node.js)**:
```
better-auth@latest
```

### External Dependencies

- PostgreSQL database (for user/task storage)
- Secure secret management (production)

---

## Artifacts Generated

| Artifact | Path | Description |
|----------|------|-------------|
| Research | `specs/001-jwt-auth/research.md` | Technology decisions |
| Data Model | `specs/001-jwt-auth/data-model.md` | Entity definitions |
| API Contract | `specs/001-jwt-auth/contracts/openapi.yaml` | OpenAPI specification |
| Quickstart | `specs/001-jwt-auth/quickstart.md` | Implementation guide |
| Plan | `specs/001-jwt-auth/plan.md` | This document |

---

## Next Steps

1. Run `/sp.tasks` to generate actionable implementation tasks
2. Implement Phase 1 (Foundation) first
3. Validate with security tests before Phase 4

---

## Complexity Tracking

No constitution violations requiring justification. The implementation uses standard patterns:
- Single auth dependency (not over-engineered)
- Direct database queries (no repository pattern)
- Standard JWT library (no custom crypto)
