# Implementation Plan: Backend API & Data Layer

**Branch**: `002-backend-api-data-layer` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-backend-api-data-layer/spec.md`

## Summary

Replace in-memory task storage with persistent PostgreSQL database using SQLModel ORM and Neon Serverless PostgreSQL. This feature builds on the existing FastAPI backend from 001-jwt-auth, adding database connectivity while preserving the existing authentication and route structure.

**Key Technical Approach**:
- SQLModel ORM for database modeling (combines SQLAlchemy + Pydantic)
- Async database operations with `asyncpg` driver
- Neon Serverless PostgreSQL for persistence
- Existing auth dependencies preserved (JWT verification, ownership checks)
- Same endpoint structure, replacing in-memory dict with DB queries

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.109+, SQLModel 0.0.16+, asyncpg 0.29+, pydantic-settings 2.0+
**Storage**: Neon Serverless PostgreSQL (connection pooling enabled)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Web application (Linux server deployment)
**Project Type**: Web application (backend only - extends existing structure)
**Performance Goals**: <500ms CRUD operations, 100 concurrent requests
**Constraints**: Stateless auth (JWT), serverless DB (cold start handling)
**Scale/Scope**: Multi-user task application, ~10k users expected

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution template has not been customized for this project. Using standard development best practices:

| Principle | Status | Notes |
|-----------|--------|-------|
| Security First | PASS | User isolation enforced at DB query level |
| Environment Secrets | PASS | DATABASE_URL via env var, not hardcoded |
| Smallest Viable Change | PASS | Only replacing storage layer, preserving routes |
| Testable Components | PASS | Async session dependency enables mocking |
| ACID Guarantees | PASS | PostgreSQL provides transaction safety |

---

## Project Structure

### Documentation (this feature)

```text
specs/002-backend-api-data-layer/
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
backend/
├── __init__.py
├── main.py                 # FastAPI app with lifespan handler
├── config.py               # Settings (add DATABASE_URL)
├── database.py             # NEW: Async engine and session factory
├── auth/
│   ├── __init__.py
│   └── dependencies.py     # Existing JWT verification
├── models/
│   ├── __init__.py
│   ├── schemas.py          # Existing Pydantic request/response models
│   └── database.py         # NEW: SQLModel Task table definition
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Existing session endpoint
│   └── tasks.py            # MODIFY: Replace in-memory with DB queries
└── tests/
    ├── __init__.py
    ├── conftest.py         # MODIFY: Add async DB fixtures
    ├── test_auth.py        # Existing auth tests
    └── test_tasks.py       # MODIFY: Test with real DB operations
```

**Structure Decision**: Extends existing `backend/` structure from 001-jwt-auth. Adds new database module and SQLModel definition while modifying existing routes and tests.

---

## Architecture Overview

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         REQUEST FLOW                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Request arrives                                                        │
│       │                                                                  │
│       ▼                                                                  │
│  ┌─────────────┐                                                        │
│  │ HTTPBearer  │  Extract JWT from Authorization header                 │
│  │ (existing)  │                                                        │
│  └──────┬──────┘                                                        │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────┐                                                        │
│  │get_current_ │  Verify JWT, extract user_id                          │
│  │user (existing)│                                                      │
│  └──────┬──────┘                                                        │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────┐                                                        │
│  │verify_user_ │  Compare JWT sub with path user_id                    │
│  │owns_resource│  Return 404 if mismatch                               │
│  │ (existing)  │                                                        │
│  └──────┬──────┘                                                        │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────┐                                                        │
│  │ get_session │  NEW: Inject async DB session                         │
│  │ (new)       │                                                        │
│  └──────┬──────┘                                                        │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────┐                                                        │
│  │   Route     │  Execute DB query with owner_id filter                │
│  │  Handler    │  Return response or 404                               │
│  └──────┬──────┘                                                        │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────┐                                                        │
│  │  Neon       │  PostgreSQL with connection pooling                   │
│  │ PostgreSQL  │                                                        │
│  └─────────────┘                                                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Database Connection

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATABASE CONNECTION FLOW                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │
│  │  FastAPI    │────▶│  AsyncPG    │────▶│   Neon      │               │
│  │  Backend    │     │  Driver     │     │  Pooler     │               │
│  └─────────────┘     └─────────────┘     └──────┬──────┘               │
│                                                  │                      │
│                                                  ▼                      │
│                                           ┌─────────────┐               │
│                                           │  Neon       │               │
│                                           │ PostgreSQL  │               │
│                                           │  Database   │               │
│                                           └─────────────┘               │
│                                                                          │
│  Features:                                                               │
│  - Connection pooling (handles serverless cold starts)                  │
│  - SSL/TLS encryption                                                   │
│  - Async operations (non-blocking)                                      │
│  - Auto-reconnect on failures                                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Architectural Decisions

### ADR-001: SQLModel ORM

**Decision**: Use SQLModel for database modeling instead of raw SQLAlchemy or raw SQL.

**Context**: Need ORM for PostgreSQL integration with existing Pydantic models.

**Rationale**:
- Single model definition for DB schema AND validation
- Native FastAPI integration (same author)
- Type hints throughout, excellent IDE support
- Built on SQLAlchemy 2.0 for reliability

**Consequences**:
- Slightly newer library than pure SQLAlchemy
- Learning curve for hybrid model approach

### ADR-002: Async Database Operations

**Decision**: Use async SQLModel with asyncpg driver for all database operations.

**Context**: FastAPI is async-native; blocking DB calls waste resources.

**Rationale**:
- asyncpg is fastest PostgreSQL driver for Python
- Non-blocking I/O matches FastAPI architecture
- Connection pooling at driver level

**Consequences**:
- More complex testing setup (pytest-asyncio required)
- Must use async session dependency injection

### ADR-003: Neon Serverless PostgreSQL

**Decision**: Use Neon as the PostgreSQL provider.

**Context**: Need managed PostgreSQL with serverless scaling.

**Rationale**:
- Scales to zero (cost-effective for dev/MVP)
- Built-in connection pooling
- Standard PostgreSQL compatibility
- Easy setup, free tier available

**Consequences**:
- Cold start latency on first request
- Connection limits on free tier (100 connections)

### ADR-004: Owner Filtering at Query Level

**Decision**: Always include `owner_id` filter in every database query.

**Context**: Need defense in depth for user data isolation.

**Rationale**:
- Auth layer validates, DB layer enforces
- No risk of accidentally returning other users' data
- Query planner uses owner_id index efficiently

**Consequences**:
- More verbose queries
- Must remember to add filter (enforced by code review)

---

## Implementation Phases

### Phase 1: Foundation

**Objective**: Set up database infrastructure

1. Add DATABASE_URL to config
2. Create database module with async engine
3. Create SQLModel Task definition
4. Add database initialization to app lifespan

**Deliverables**:
- `backend/config.py` (modified)
- `backend/database.py` (new)
- `backend/models/database.py` (new)
- `backend/main.py` (modified)

### Phase 2: Route Migration

**Objective**: Replace in-memory storage with database queries

1. Add session dependency to task routes
2. Implement CREATE operation with DB insert
3. Implement READ operations with DB select
4. Implement UPDATE operation with DB update
5. Implement DELETE operation with DB delete
6. Remove in-memory storage code

**Deliverables**:
- `backend/routes/tasks.py` (modified)

### Phase 3: Testing

**Objective**: Verify all operations work correctly

1. Add async test fixtures for DB session
2. Update test_tasks.py for database operations
3. Add persistence verification tests
4. Add cross-user isolation tests

**Deliverables**:
- `backend/tests/conftest.py` (modified)
- `backend/tests/test_tasks.py` (modified)

### Phase 4: Validation

**Objective**: Verify system meets requirements

1. Run all tests and verify pass
2. Manual end-to-end test with real Neon DB
3. Verify persistence across restarts
4. Load test with 100 concurrent requests

---

## Security Checkpoints

| Checkpoint | Verification Method | Expected Result |
|------------|---------------------|-----------------|
| Owner isolation | Query another user's task | 404 Not Found |
| SQL injection | Send malicious input | Input sanitized by ORM |
| Missing auth | Request without token | 401 Unauthorized |
| Data persistence | Restart server | Data intact |
| Connection security | Check connection | SSL/TLS enabled |

---

## Testing Strategy

### Unit Tests

```python
# Test categories
1. Database Operations
   - Create task → task in DB
   - Read tasks → correct data returned
   - Update task → only specified fields changed
   - Delete task → task removed from DB

2. User Isolation
   - Query with owner filter → only user's tasks
   - Access other user's task → 404 returned
   - Create task → owner_id set correctly

3. Validation
   - Empty title → 422 error
   - Title too long → 422 error
   - Invalid task ID format → 422 error
```

### Integration Tests

```python
# End-to-end scenarios
1. Create → Read → Verify match
2. Create → Update → Read → Verify changes
3. Create → Delete → Read → Verify 404
4. Create as User A → Access as User B → Verify 404
5. Server restart → Read → Verify persistence
```

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Neon cold start latency | Medium | Low | Connection pooling, keep-alive |
| Connection limit exceeded | Low | Medium | Pool size limits, connection reuse |
| Data loss | Low | Critical | ACID transactions, backups |
| SQL injection | Low | Critical | ORM parameterization |

---

## Dependencies

### Required Packages

**Backend (Python)**:
```
sqlmodel>=0.0.16
asyncpg>=0.29.0
python-dotenv>=1.0.0
```

### External Dependencies

- Neon PostgreSQL account
- DATABASE_URL environment variable
- Existing 001-jwt-auth implementation

---

## Artifacts Generated

| Artifact | Path | Description |
|----------|------|-------------|
| Research | `specs/002-backend-api-data-layer/research.md` | Technology decisions |
| Data Model | `specs/002-backend-api-data-layer/data-model.md` | Entity definitions |
| API Contract | `specs/002-backend-api-data-layer/contracts/openapi.yaml` | OpenAPI specification |
| Quickstart | `specs/002-backend-api-data-layer/quickstart.md` | Implementation guide |
| Plan | `specs/002-backend-api-data-layer/plan.md` | This document |

---

## Next Steps

1. Run `/sp.tasks` to generate actionable implementation tasks
2. Set up Neon PostgreSQL database
3. Implement Phase 1 (Foundation) first
4. Validate with tests before Phase 4

---

## Complexity Tracking

No constitution violations requiring justification. The implementation uses standard patterns:
- Single ORM (SQLModel, not layered abstractions)
- Direct database queries (no repository pattern)
- Standard async session management
- Existing route structure preserved
