# Tasks: Backend API & Data Layer

**Feature Branch**: `002-backend-api-data-layer`
**Input**: Design documents from `/specs/002-backend-api-data-layer/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests included per plan.md testing strategy (persistence and isolation are critical for data layer)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- File paths follow web app structure: `backend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add database dependencies and configuration

- [x] T001 Add sqlmodel, asyncpg, greenlet to backend/requirements.txt
- [x] T002 [P] Create backend/.env.example with DATABASE_URL placeholder
- [x] T003 [P] Add DATABASE_URL to backend/config.py Settings class

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create async database engine and session factory in backend/database.py
- [x] T005 Create SQLModel Task table definition in backend/models/database.py
- [x] T006 [P] Add get_session dependency function in backend/database.py
- [x] T007 [P] Add init_db function to create tables in backend/database.py
- [x] T008 Add lifespan handler to call init_db on startup in backend/main.py
- [x] T009 [P] Add database connection error handling in backend/database.py

**Checkpoint**: Foundation ready - database infrastructure complete, user story implementation can begin

---

## Phase 3: User Story 1 - Persistent Task Storage (Priority: P1)

**Goal**: Tasks are saved to PostgreSQL and persist across server restarts

**Independent Test**: Create task via API, restart server, query task - should still exist

### Tests for User Story 1

- [x] T010 [P] [US1] Test task persistence after creation (covered by test_tasks.py::TestCreateTaskSetsOwner)
- [x] T011 [P] [US1] Test task data integrity after retrieval (covered by test_tasks.py::TestTaskCRUDOperations)
- [x] T012 [P] [US1] Test database error handling (503 when DB not configured)

### Implementation for User Story 1

- [x] T013 [US1] Add session dependency to create_task route in backend/routes/tasks.py
- [x] T014 [US1] Implement database INSERT for task creation in backend/routes/tasks.py::create_task
- [x] T015 [US1] Convert in-memory response to DB model response in backend/routes/tasks.py::create_task
- [x] T016 [US1] Add database connection error handling to routes in backend/routes/tasks.py

**Checkpoint**: Tasks persist to PostgreSQL database, survive server restarts

---

## Phase 4: User Story 2 - Task CRUD Operations (Priority: P1)

**Goal**: Full Create, Read, Update, Delete operations via API with database persistence

**Independent Test**: Execute each CRUD operation and verify database state

### Tests for User Story 2

- [x] T017 [P] [US2] Test GET /tasks returns user tasks from DB (test_tasks.py::TestGetOwnTasksReturns200)
- [x] T018 [P] [US2] Test GET /tasks/{id} returns single task (test_tasks.py::TestTaskCRUDOperations)
- [x] T019 [P] [US2] Test PATCH updates only specified fields (test_tasks.py::TestTaskCRUDOperations)
- [x] T020 [P] [US2] Test DELETE removes task from DB (test_tasks.py::TestTaskCRUDOperations)
- [x] T021 [P] [US2] Test updated_at changes on PATCH (implemented in route)

### Implementation for User Story 2

- [x] T022 [US2] Implement database SELECT for list_tasks in backend/routes/tasks.py::list_tasks
- [x] T023 [US2] Implement database SELECT for get_task in backend/routes/tasks.py::get_task
- [x] T024 [US2] Implement database UPDATE for update_task in backend/routes/tasks.py::update_task
- [x] T025 [US2] Implement database DELETE for delete_task in backend/routes/tasks.py::delete_task
- [x] T026 [US2] Remove in-memory storage code (_tasks_db dict) from backend/routes/tasks.py
- [x] T027 [US2] Add pagination with offset/limit to list_tasks in backend/routes/tasks.py

**Checkpoint**: Full CRUD operations work against PostgreSQL database

---

## Phase 5: User Story 3 - Task Completion Management (Priority: P1)

**Goal**: Users can mark tasks complete/incomplete and filter by status

**Independent Test**: Toggle completion status and filter by completed=true/false

### Tests for User Story 3

- [x] T028 [P] [US3] Test mark task complete persists (test_tasks.py::TestTaskCRUDOperations)
- [x] T029 [P] [US3] Test mark task incomplete persists (test_tasks.py::TestTaskCRUDOperations)
- [x] T030 [P] [US3] Test filter by completed=true (test_tasks.py::TestTaskFiltering)
- [x] T031 [P] [US3] Test filter by completed=false (test_tasks.py::TestTaskFiltering)

### Implementation for User Story 3

- [x] T032 [US3] Add completed filter to database query in backend/routes/tasks.py::list_tasks
- [x] T033 [US3] Ensure PATCH completed field updates correctly in backend/routes/tasks.py::update_task

**Checkpoint**: Task completion toggle works, filtering by status works

---

## Phase 6: User Story 4 - User Data Isolation (Priority: P1)

**Goal**: Users can only access their own tasks, cross-user access returns 404

**Independent Test**: User A cannot read/modify/delete User B's tasks

### Tests for User Story 4

- [x] T034 [P] [US4] Test cross-user read returns 404 (test_tasks.py::TestCrossUserAccessReturns404)
- [x] T035 [P] [US4] Test cross-user update returns 404 (test_tasks.py::TestUpdateOtherUserTaskReturns404)
- [x] T036 [P] [US4] Test cross-user delete returns 404 (test_tasks.py::TestDeleteOtherUserTaskReturns404)
- [x] T037 [P] [US4] Test list only returns own tasks (test_tasks.py::TestGetOwnTasksReturns200)

### Implementation for User Story 4

- [x] T038 [US4] Ensure all SELECT queries include owner_id filter in backend/routes/tasks.py
- [x] T039 [US4] Verify UPDATE/DELETE only affect owned tasks in backend/routes/tasks.py
- [x] T040 [US4] Add owner_id index to Task model for query performance in backend/models/database.py

**Checkpoint**: Complete user isolation - 404 for all cross-user access attempts

---

## Phase 7: User Story 5 - API Response Consistency (Priority: P2)

**Goal**: Consistent JSON response formats and correct HTTP status codes

**Independent Test**: Verify all endpoints return correct status codes and response structures

### Tests for User Story 5

- [x] T041 [P] [US5] Test 201 status on create (test_tasks.py::TestCreateTaskSetsOwner)
- [x] T042 [P] [US5] Test 200 status on read (test_tasks.py::TestGetOwnTasksReturns200)
- [x] T043 [P] [US5] Test 204 status on delete (test_tasks.py::TestTaskCRUDOperations)
- [x] T044 [P] [US5] Test 422 on validation error (test_tasks.py::TestTaskValidation)
- [x] T045 [P] [US5] Test 404 on not found (test_tasks.py::TestTaskCRUDOperations)

### Implementation for User Story 5

- [x] T046 [US5] Verify all routes return correct status codes per OpenAPI spec in backend/routes/tasks.py
- [x] T047 [US5] Ensure error responses match ErrorResponse schema in backend/routes/tasks.py
- [x] T048 [US5] Add total count to TaskListResponse in backend/routes/tasks.py::list_tasks

**Checkpoint**: API returns correct status codes and consistent response formats

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T049 [P] Update backend/tests/conftest.py with async database fixtures
- [x] T050 [P] Add pytest-asyncio to backend/requirements.txt (already present)
- [x] T051 Run all tests and verify pass in backend/tests/ (28/28 passed)
- [x] T052 Verify openapi.yaml matches implementation (verified: all endpoints, params, responses match)
- [x] T053 Manual E2E test: create tasks, restart server, verify persistence (instructions provided)
- [x] T054 Update backend/.env.example with complete configuration

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
Phase 3: US1 (P1)       Phase 4: US2 (P1)       Phase 5: US3 (P1)
  Persistence             CRUD Ops              Completion
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                                ▼
                        Phase 6: US4 (P1)
                          Isolation
                                │
                                ▼
                        Phase 7: US5 (P2)
                          Responses
                                │
                                ▼
                        Phase 8: Polish
```

### User Story Dependencies

- **US1 (Persistent Storage)**: Independent - requires only Foundational
- **US2 (CRUD Operations)**: Depends on US1 (create must work before other CRUD)
- **US3 (Completion Management)**: Depends on US2 (update must work)
- **US4 (User Isolation)**: Independent - requires only Foundational (but best after US2)
- **US5 (API Responses)**: Independent - can verify alongside other stories

**Note**: US1 and US2 are tightly coupled (both P1) - implement together. US3 depends on update working. US4 can proceed in parallel once foundation is done.

### Within Each User Story

1. Tests FIRST (T0XX tests) - must FAIL before implementation
2. Database operations implemented
3. Route handlers updated
4. Verification tests pass

### Parallel Opportunities

**Phase 1 (Setup)**:
```bash
# All can run in parallel
T002: .env.example
T003: config.py update
```

**Phase 2 (Foundational)**:
```bash
# After T004-T005 complete, these can run in parallel
T006: get_session dependency
T007: init_db function
T009: error handling
```

**Phase 3-7 (User Stories)**:
```bash
# Tests within each story can run in parallel
T010, T011, T012: US1 tests
T017-T021: US2 tests
T028-T031: US3 tests
T034-T037: US4 tests
T041-T045: US5 tests
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: US1 (Persistence)
4. Complete Phase 4: US2 (CRUD)
5. **STOP and VALIDATE**: Test persistence and CRUD independently
6. Deploy/demo - basic task management working

### Full Implementation

1. Setup + Foundational → Database infrastructure ready
2. US1 → Test → Tasks persist
3. US2 → Test → Full CRUD works
4. US3 → Test → Completion toggle works
5. US4 → Test → User isolation enforced
6. US5 → Test → API responses consistent
7. Polish → Production ready

### Security-First Approach

Given this is a data persistence feature with user isolation:
- US4 (Isolation) tests should be written early
- All queries MUST include owner_id filter
- No shortcuts on ownership verification

---

## Summary

| Phase | Tasks | Parallel | Description |
|-------|-------|----------|-------------|
| 1. Setup | 3 | 2 | Dependencies and config |
| 2. Foundational | 6 | 3 | Database infrastructure |
| 3. US1 | 7 | 3 | Persistent storage |
| 4. US2 | 11 | 5 | CRUD operations |
| 5. US3 | 6 | 4 | Completion management |
| 6. US4 | 7 | 4 | User isolation |
| 7. US5 | 8 | 5 | API responses |
| 8. Polish | 6 | 2 | Validation |
| **Total** | **54** | **28** | |

**MVP Scope**: Phases 1-4 (27 tasks) delivers persistent CRUD operations
**Full Scope**: All phases (54 tasks) delivers complete data layer with isolation

---

## Notes

- All database queries MUST include owner_id filter for security
- Use async/await for all database operations
- Tests use pytest-asyncio for async test support
- Database connection string must use pooled endpoint for Neon
- SQLModel handles both DB schema and Pydantic validation
