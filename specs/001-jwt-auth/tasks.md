# Tasks: JWT-Based Authentication & Authorization

**Feature Branch**: `001-jwt-auth`
**Input**: Design documents from `/specs/001-jwt-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests included per plan.md testing strategy (security validation is critical for auth features)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- File paths follow web app structure: `backend/`, `frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure: backend/{auth,routes,models,tests}/__init__.py
- [x] T002 [P] Create backend/requirements.txt with FastAPI, uvicorn, python-jose[cryptography], pydantic-settings
- [x] T003 [P] Create frontend directory structure: frontend/lib/, frontend/app/api/auth/[...all]/
- [x] T004 [P] Create backend/.env.example with BETTER_AUTH_SECRET placeholder
- [x] T005 [P] Create frontend/.env.local.example with BETTER_AUTH_SECRET and API URL placeholders

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Implement Settings class with BETTER_AUTH_SECRET in backend/config.py
- [x] T007 Create TokenPayload Pydantic model in backend/models/schemas.py
- [x] T008 [P] Create CurrentUser Pydantic model in backend/models/schemas.py
- [x] T009 [P] Create ErrorResponse Pydantic model in backend/models/schemas.py
- [x] T010 Create HTTPBearer security scheme in backend/auth/dependencies.py
- [x] T011 Implement get_current_user dependency with JWT decode in backend/auth/dependencies.py
- [x] T012 Create FastAPI app with CORS configuration in backend/main.py
- [x] T013 [P] Configure Better Auth with jwt cookie strategy in frontend/lib/auth.ts
- [x] T014 [P] Create auth client helper in frontend/lib/auth-client.ts
- [x] T015 Create API client with Bearer token attachment in frontend/lib/api-client.ts
- [x] T016 Create Better Auth route handler in frontend/app/api/auth/[...all]/route.ts

**Checkpoint**: Foundation ready - JWT verification infrastructure complete, user story implementation can begin

---

## Phase 3: User Story 1 - Authenticated API Access (Priority: P1)

**Goal**: Logged-in users can make authenticated API requests with JWT tokens automatically attached and verified

**Independent Test**: Login, make API request to /api/v1/auth/session, verify 200 response with user data

### Tests for User Story 1

- [x] T017 [P] [US1] Test valid token returns 200 in backend/tests/test_auth.py::test_valid_token_returns_200
- [x] T018 [P] [US1] Test missing token returns 401 in backend/tests/test_auth.py::test_missing_token_returns_401
- [x] T019 [P] [US1] Test sequential requests with same token in backend/tests/test_auth.py::test_sequential_requests_authenticated

### Implementation for User Story 1

- [x] T020 [US1] Create test fixtures for valid/invalid tokens in backend/tests/conftest.py
- [x] T021 [US1] Implement GET /api/v1/auth/session endpoint in backend/routes/auth.py
- [x] T022 [US1] Register auth router in backend/main.py
- [x] T023 [US1] Verify token attachment in frontend API calls via frontend/lib/api-client.ts

**Checkpoint**: Users can login via Better Auth and access /api/v1/auth/session with valid JWT

---

## Phase 4: User Story 2 - User Isolation & Data Protection (Priority: P1)

**Goal**: Users can only access and modify their own tasks; cross-user access is blocked

**Independent Test**: Create task as User A, attempt access as User B, verify 404 response

### Tests for User Story 2

- [x] T024 [P] [US2] Test own tasks returns 200 in backend/tests/test_tasks.py::test_get_own_tasks_returns_200
- [x] T025 [P] [US2] Test cross-user access returns 404 in backend/tests/test_tasks.py::test_cross_user_access_returns_404
- [x] T026 [P] [US2] Test create task with owner verification in backend/tests/test_tasks.py::test_create_task_sets_owner
- [x] T027 [P] [US2] Test update other user task returns 404 in backend/tests/test_tasks.py::test_update_other_user_task_returns_404
- [x] T028 [P] [US2] Test delete other user task returns 404 in backend/tests/test_tasks.py::test_delete_other_user_task_returns_404

### Implementation for User Story 2

- [x] T029 [P] [US2] Create TaskBase, TaskCreate, TaskUpdate Pydantic models in backend/models/schemas.py
- [x] T030 [P] [US2] Create TaskResponse, TaskListResponse Pydantic models in backend/models/schemas.py
- [x] T031 [US2] Implement ownership verification helper in backend/auth/dependencies.py
- [x] T032 [US2] Implement GET /api/v1/users/{user_id}/tasks with ownership check in backend/routes/tasks.py
- [x] T033 [US2] Implement POST /api/v1/users/{user_id}/tasks with ownership check in backend/routes/tasks.py
- [x] T034 [US2] Implement GET /api/v1/users/{user_id}/tasks/{task_id} with ownership check in backend/routes/tasks.py
- [x] T035 [US2] Implement PATCH /api/v1/users/{user_id}/tasks/{task_id} with ownership check in backend/routes/tasks.py
- [x] T036 [US2] Implement DELETE /api/v1/users/{user_id}/tasks/{task_id} with ownership check in backend/routes/tasks.py
- [x] T037 [US2] Register tasks router in backend/main.py

**Checkpoint**: Users can CRUD their own tasks, cannot access other users' tasks (404 response)

---

## Phase 5: User Story 3 - Token Expiration Handling (Priority: P2)

**Goal**: Expired tokens are rejected with clear 401 response indicating expiration

**Independent Test**: Obtain token, wait/mock expiration, make request, verify 401 with expiration message

### Tests for User Story 3

- [x] T038 [P] [US3] Test expired token returns 401 in backend/tests/test_auth.py::test_expired_token_returns_401
- [x] T039 [P] [US3] Test valid token near expiry succeeds in backend/tests/test_auth.py::test_token_near_expiry_succeeds
- [x] T040 [P] [US3] Test clock skew tolerance (10s) in backend/tests/test_auth.py::test_clock_skew_tolerance

### Implementation for User Story 3

- [x] T041 [US3] Add expired token fixture in backend/tests/conftest.py
- [x] T042 [US3] Add ExpiredSignatureError handling in backend/auth/dependencies.py::get_current_user
- [x] T043 [US3] Add clock skew leeway (10s) to jwt.decode options in backend/auth/dependencies.py

**Checkpoint**: Expired tokens return 401 with "Token has expired" message, clock skew handled

---

## Phase 6: User Story 4 - Invalid Token Rejection (Priority: P2)

**Goal**: Malformed, tampered, or incorrectly signed tokens are rejected with 401

**Independent Test**: Send malformed token, verify 401 response with generic error

### Tests for User Story 4

- [x] T044 [P] [US4] Test malformed token returns 401 in backend/tests/test_auth.py::test_malformed_token_returns_401
- [x] T045 [P] [US4] Test wrong signature returns 401 in backend/tests/test_auth.py::test_wrong_signature_returns_401
- [x] T046 [P] [US4] Test tampered payload returns 401 in backend/tests/test_auth.py::test_tampered_payload_returns_401
- [x] T047 [P] [US4] Test missing sub claim returns 401 in backend/tests/test_auth.py::test_missing_sub_claim_returns_401
- [x] T048 [P] [US4] Test empty Authorization header returns 401 in backend/tests/test_auth.py::test_empty_auth_header_returns_401

### Implementation for User Story 4

- [x] T049 [US4] Add invalid token fixtures in backend/tests/conftest.py
- [x] T050 [US4] Add JWTError catch-all handling in backend/auth/dependencies.py::get_current_user
- [x] T051 [US4] Add required claims validation (sub, exp, iat) in backend/auth/dependencies.py
- [x] T052 [US4] Verify error messages are non-sensitive in backend/auth/dependencies.py

**Checkpoint**: All invalid tokens return 401 with generic "Invalid credentials" message

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [x] T053 [P] Verify all endpoints in openapi.yaml match implementation
- [x] T054 [P] Add startup validation for BETTER_AUTH_SECRET in backend/config.py
- [x] T055 Run all backend tests and verify pass in backend/tests/
- [ ] T056 Manual end-to-end test: login -> access tasks -> logout
- [ ] T057 Verify quickstart.md steps work correctly
- [ ] T058 Update CLAUDE.md with authentication documentation

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ─────────────────┐
                                │
                                ▼
Phase 2: Foundational ──────────┤ BLOCKS ALL USER STORIES
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
Phase 3: US1 (P1)       Phase 4: US2 (P1)       Phase 5: US3 (P2)
  Auth Access             User Isolation         Expiration
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
                        Phase 6: US4 (P2)
                          Invalid Tokens
                                │
                                ▼
                        Phase 7: Polish
```

### User Story Dependencies

- **US1 (Authenticated API Access)**: Independent - requires only Foundational phase
- **US2 (User Isolation)**: Independent - requires only Foundational phase
- **US3 (Token Expiration)**: Independent - requires only Foundational phase
- **US4 (Invalid Token Rejection)**: Independent - requires only Foundational phase

**Note**: US1 and US2 are both P1 (critical). US2 depends on auth working (US1), but they can be implemented in the same sprint since they share the auth dependency.

### Within Each User Story

1. Tests FIRST (T0XX tests) - must FAIL before implementation
2. Models/Fixtures
3. Services/Dependencies
4. Routes/Endpoints
5. Integration verification

### Parallel Opportunities

**Phase 1 (Setup)**:
```bash
# All can run in parallel
T002: requirements.txt
T003: frontend structure
T004: backend .env.example
T005: frontend .env.local.example
```

**Phase 2 (Foundational)**:
```bash
# After T006-T007 complete, these can run in parallel
T008: CurrentUser model
T009: ErrorResponse model
T013: Better Auth config
T014: Auth client
```

**Phase 3 (US1 Tests)**:
```bash
# All tests can run in parallel
T017: test_valid_token_returns_200
T018: test_missing_token_returns_401
T019: test_sequential_requests_authenticated
```

**Phase 4 (US2 Tests)**:
```bash
# All tests can run in parallel
T024-T028: All US2 tests
```

**Phase 4 (US2 Models)**:
```bash
# Models can run in parallel
T029: TaskBase, TaskCreate, TaskUpdate
T030: TaskResponse, TaskListResponse
```

---

## Parallel Example: User Story 2

```bash
# First: Launch all US2 tests in parallel
Task: "Test own tasks returns 200 in backend/tests/test_tasks.py"
Task: "Test cross-user access returns 404 in backend/tests/test_tasks.py"
Task: "Test create task with owner verification in backend/tests/test_tasks.py"

# Then: Launch models in parallel
Task: "Create TaskBase, TaskCreate, TaskUpdate in backend/models/schemas.py"
Task: "Create TaskResponse, TaskListResponse in backend/models/schemas.py"

# Then: Sequential route implementation (same file)
Task: "Implement GET /api/v1/users/{user_id}/tasks in backend/routes/tasks.py"
Task: "Implement POST /api/v1/users/{user_id}/tasks in backend/routes/tasks.py"
# ... etc
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: US1 (Authenticated API Access)
4. Complete Phase 4: US2 (User Isolation)
5. **STOP and VALIDATE**: Test authentication and isolation independently
6. Deploy/demo - core security working

### Full Implementation

1. Setup + Foundational → Foundation ready
2. US1 → Test → Users can authenticate
3. US2 → Test → Users isolated
4. US3 → Test → Expiration handled
5. US4 → Test → Invalid tokens rejected
6. Polish → Production ready

### Security-First Approach

Given this is an authentication feature:
- All tests should be written FIRST
- Tests should FAIL before implementation
- Security edge cases (US3, US4) are critical even at P2
- No shortcuts on error handling

---

## Summary

| Phase | Tasks | Parallel | Description |
|-------|-------|----------|-------------|
| 1. Setup | 5 | 4 | Project structure |
| 2. Foundational | 11 | 4 | Core auth infrastructure |
| 3. US1 | 7 | 3 | Authenticated API access |
| 4. US2 | 14 | 7 | User isolation |
| 5. US3 | 6 | 3 | Token expiration |
| 6. US4 | 9 | 5 | Invalid token handling |
| 7. Polish | 6 | 2 | Final validation |
| **Total** | **58** | **28** | |

**MVP Scope**: Phases 1-4 (37 tasks) delivers authenticated access with user isolation
**Full Scope**: All phases (58 tasks) delivers complete security layer

---

## Notes

- All 401 responses use generic "Invalid credentials" to prevent information leakage
- All cross-user access attempts return 404 (not 403) per OWASP IDOR guidance
- Tests use fixtures to generate valid/invalid/expired tokens
- Clock skew tolerance of 10 seconds handles minor server time differences
- BETTER_AUTH_SECRET must be same value in frontend and backend
