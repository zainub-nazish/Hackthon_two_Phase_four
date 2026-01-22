# Tasks: Todo Full-Stack Web Application (Beautiful UI)

**Input**: Design documents from `/specs/004-fullstack-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this task list (not explicitly requested). Add testing phase if needed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` directory
- **Frontend**: `frontend/` directory

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project structure and configuration

- [x] T001 Verify project structure matches plan.md layout
- [x] T002 [P] Verify frontend dependencies in frontend/package.json (Next.js, Better Auth, Tailwind)
- [x] T003 [P] Verify backend dependencies in backend/requirements.txt (FastAPI, SQLModel, asyncpg)
- [x] T004 [P] Verify environment files exist (frontend/.env.local, backend/.env)
- [x] T005 Verify database connection works for both frontend and backend

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**Note**: Much of this already exists but may need UI enhancement per research.md decisions

- [x] T006 Enhance frontend/app/layout.tsx with design system (Inter font, base styles)
- [x] T007 [P] Update frontend/tailwind.config.ts with color palette (Indigo primary, Green success, Red danger)
- [x] T008 [P] Enhance frontend/components/ui/button.tsx with design system variants
- [x] T009 [P] Enhance frontend/components/ui/input.tsx with consistent styling
- [x] T010 [P] Enhance frontend/components/ui/card.tsx with shadow and border styling
- [x] T011 [P] Enhance frontend/components/ui/spinner.tsx with proper sizing variants
- [x] T012 [P] Enhance frontend/components/ui/dialog.tsx with modal styling and animations
- [x] T013 [P] Enhance frontend/components/ui/toast.tsx with success/error/info variants
- [x] T014 Verify backend/auth/dependencies.py session verification works correctly
- [x] T015 [P] Remove debug console.log statements from frontend/lib/api-client.ts (added during debugging)
- [x] T016 [P] Remove debug console.log statements from frontend/lib/auth-client.ts
- [x] T017 [P] Remove debug console.log statements from frontend/hooks/use-tasks.ts

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - New User Registration (Priority: P1)

**Goal**: New users can create accounts with email/password and access their dashboard

**Independent Test**: Complete signup flow → verify redirect to dashboard → user can see empty task list

### Implementation for User Story 1

- [x] T018 [P] [US1] Enhance frontend/app/(auth)/layout.tsx with centered card layout, professional styling
- [x] T019 [P] [US1] Enhance frontend/app/(auth)/signup/page.tsx with proper page title and meta
- [x] T020 [US1] Enhance frontend/components/auth/signup-form.tsx with:
  - Professional form styling per design system
  - Email validation with inline error messages
  - Password requirements display (min 8 characters)
  - Loading state on submit button
  - Error toast for duplicate email
  - Success redirect to dashboard
- [x] T021 [US1] Add link to login page from signup form ("Already have an account?")
- [x] T022 [US1] Verify Better Auth signup endpoint works in frontend/lib/auth.ts

**Checkpoint**: User Story 1 complete - new users can register

---

## Phase 4: User Story 2 - Returning User Sign In (Priority: P1)

**Goal**: Existing users can sign in and access their tasks

**Independent Test**: Sign in with valid credentials → redirect to dashboard → see task list

### Implementation for User Story 2

- [x] T023 [P] [US2] Enhance frontend/app/(auth)/login/page.tsx with proper page title and meta
- [x] T024 [US2] Enhance frontend/components/auth/login-form.tsx with:
  - Professional form styling matching signup
  - Email/password validation
  - Loading state on submit button
  - Error message for invalid credentials
  - Success redirect to dashboard
- [x] T025 [US2] Add link to signup page from login form ("Don't have an account?")
- [x] T026 [US2] Verify session persistence across browser close (7-day validity)

**Checkpoint**: User Story 2 complete - returning users can sign in

---

## Phase 5: User Story 3 - Create a Task (Priority: P1)

**Goal**: Authenticated users can create tasks with title and optional description

**Independent Test**: Click "Add Task" → enter title → submit → see task appear in list

### Implementation for User Story 3

- [x] T027 [P] [US3] Enhance frontend/components/tasks/task-form.tsx with:
  - Professional styling (Input components from design system)
  - Title field (required) with validation
  - Description field (optional, textarea)
  - Cancel and Submit buttons
  - Loading state during submission
- [x] T028 [US3] Verify POST /api/v1/users/{user_id}/tasks endpoint works
- [x] T029 [US3] Add success toast after task creation in frontend/app/(dashboard)/tasks/page.tsx
- [x] T030 [US3] Verify new task appears at top of list without page refresh (optimistic update)

**Checkpoint**: User Story 3 complete - users can create tasks

---

## Phase 6: User Story 4 - View Task List (Priority: P1)

**Goal**: Authenticated users can view all their tasks with filter options

**Independent Test**: Navigate to dashboard → see all tasks → filter by pending/completed

### Implementation for User Story 4

- [x] T031 [P] [US4] Enhance frontend/app/(dashboard)/layout.tsx with dashboard layout styling
- [x] T032 [P] [US4] Enhance frontend/components/layout/header.tsx with:
  - Logo/brand on left
  - User menu on right
  - Professional top-nav styling
  - Responsive padding
- [x] T033 [P] [US4] Enhance frontend/components/layout/user-menu.tsx with avatar/dropdown styling
- [x] T034 [US4] Enhance frontend/app/(dashboard)/tasks/page.tsx with:
  - Page header with title and Add Task button
  - Professional spacing and layout
- [x] T035 [P] [US4] Enhance frontend/components/tasks/task-filter.tsx with:
  - Tab-style filter (All/Pending/Completed)
  - Active state indication
  - Count badges for each filter
- [x] T036 [US4] Enhance frontend/components/tasks/task-list.tsx with:
  - Card-based task layout
  - Loading state (spinner)
  - Error state with retry option
- [x] T037 [P] [US4] Enhance frontend/components/tasks/empty-state.tsx with:
  - Friendly illustration or icon
  - Contextual message based on filter
  - Call-to-action button

**Checkpoint**: User Story 4 complete - users can view and filter tasks

---

## Phase 7: User Story 5 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Users can toggle task completion with visual feedback

**Independent Test**: Click checkbox on pending task → see visual change → refresh → state persisted

### Implementation for User Story 5

- [x] T038 [US5] Enhance frontend/components/tasks/task-item.tsx with:
  - Checkbox/toggle for completion status
  - Strikethrough styling for completed tasks
  - Muted colors for completed state
  - Loading state during toggle
  - Optimistic update with rollback on error
- [x] T039 [US5] Verify PATCH /api/v1/users/{user_id}/tasks/{task_id} endpoint works for completion toggle
- [x] T040 [US5] Add subtle animation for completion toggle

**Checkpoint**: User Story 5 complete - users can toggle task completion

---

## Phase 8: User Story 6 - Edit a Task (Priority: P2)

**Goal**: Users can modify task title and description

**Independent Test**: Click edit → modify title → save → see updated task

### Implementation for User Story 6

- [x] T041 [US6] Add edit button to frontend/components/tasks/task-item.tsx
- [x] T042 [US6] Wire edit dialog in frontend/app/(dashboard)/tasks/page.tsx (reuse TaskForm)
- [x] T043 [US6] Pre-populate form with existing task data when editing
- [x] T044 [US6] Add success toast after task update
- [x] T045 [US6] Verify PATCH endpoint works for title/description updates

**Checkpoint**: User Story 6 complete - users can edit tasks

---

## Phase 9: User Story 7 - Delete a Task (Priority: P2)

**Goal**: Users can permanently delete tasks with confirmation

**Independent Test**: Click delete → confirm in dialog → task removed from list

### Implementation for User Story 7

- [x] T046 [US7] Add delete button to frontend/components/tasks/task-item.tsx
- [x] T047 [P] [US7] Enhance frontend/components/tasks/delete-dialog.tsx with:
  - Warning styling (red accent)
  - Task title in confirmation message
  - Cancel and Delete buttons
  - Loading state during deletion
- [x] T048 [US7] Verify DELETE /api/v1/users/{user_id}/tasks/{task_id} endpoint works
- [x] T049 [US7] Add success toast after task deletion
- [x] T050 [US7] Remove task from list without page refresh

**Checkpoint**: User Story 7 complete - users can delete tasks

---

## Phase 10: User Story 8 - Sign Out (Priority: P3)

**Goal**: Users can sign out and end their session

**Independent Test**: Click sign out → redirect to login → cannot access dashboard

### Implementation for User Story 8

- [x] T051 [US8] Ensure sign out option in frontend/components/layout/user-menu.tsx
- [x] T052 [US8] Implement sign out in frontend/hooks/use-auth.ts (already exists, verify)
- [x] T053 [US8] Verify redirect to login page after sign out
- [x] T054 [US8] Verify protected routes redirect to login when not authenticated

**Checkpoint**: User Story 8 complete - users can sign out

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Production-ready improvements

- [x] T055 [P] Add responsive breakpoints testing (320px, 768px, 1024px, 1920px)
- [x] T056 [P] Add keyboard navigation support for task actions
- [x] T057 [P] Add focus indicators for accessibility
- [x] T058 [P] Add loading skeleton for initial page load
- [x] T059 Verify error handling for network failures (toast with retry)
- [x] T060 [P] Add truncation for long task titles with tooltip on hover
- [x] T061 Verify session expiry handling (redirect to login with message)
- [x] T062 Run quickstart.md validation (full flow test)
- [x] T063 Remove any remaining debug code or console statements
- [x] T064 Final visual QA pass against design system

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - verification only
- **Foundational (Phase 2)**: Setup complete - BLOCKS all user stories
- **User Stories (Phase 3-10)**: Foundational complete
  - US1 (Registration) and US2 (Sign In): Can run in parallel
  - US3 (Create) and US4 (View): Depend on US1 or US2 (need auth)
  - US5-7 (Complete/Edit/Delete): Depend on US3 (need tasks)
  - US8 (Sign Out): Independent, low priority
- **Polish (Phase 11)**: All user stories complete

### User Story Dependencies

```
US1 (Register) ──┐
                 ├──> US3 (Create) ──┐
US2 (Sign In) ──┘                    │
                                     ├──> US5 (Complete)
US4 (View) ─────────────────────────>├──> US6 (Edit)
                                     └──> US7 (Delete)

US8 (Sign Out): Independent
```

### Parallel Opportunities

**Phase 2 (Foundational)**: All [P] tasks can run in parallel:
- T007, T008, T009, T010, T011, T012, T013, T015, T016, T017

**Phase 3 (US1)**: T018 and T019 can run in parallel

**Phase 4 (US2)**: T023 can run with US1 tasks (different files)

**Phase 6 (US4)**: T031, T032, T033, T035, T037 can run in parallel

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch all UI component enhancements together:
Task: "Update frontend/tailwind.config.ts with color palette"
Task: "Enhance frontend/components/ui/button.tsx with variants"
Task: "Enhance frontend/components/ui/input.tsx with styling"
Task: "Enhance frontend/components/ui/card.tsx with shadows"
Task: "Enhance frontend/components/ui/spinner.tsx with sizes"
Task: "Enhance frontend/components/ui/dialog.tsx with modal styling"
Task: "Enhance frontend/components/ui/toast.tsx with variants"
```

---

## Implementation Strategy

### MVP First (User Stories 1-4)

1. Complete Phase 1: Setup (verify)
2. Complete Phase 2: Foundational (UI components)
3. Complete Phase 3: User Story 1 (Registration)
4. Complete Phase 4: User Story 2 (Sign In)
5. Complete Phase 5: User Story 3 (Create Task)
6. Complete Phase 6: User Story 4 (View Tasks)
7. **STOP and VALIDATE**: Full auth + task creation flow works
8. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → UI foundation ready
2. Add US1 + US2 → Auth flow complete
3. Add US3 + US4 → Core task management (MVP!)
4. Add US5 → Task completion toggle
5. Add US6 + US7 → Full CRUD operations
6. Add US8 → Sign out
7. Polish → Production ready

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story should be independently testable
- Commit after each task or logical group
- Many tasks are "Enhance" (improve existing) vs "Create" (new)
- Focus is on UI quality per research.md decisions
- Avoid: vague tasks, same file conflicts, breaking existing functionality
