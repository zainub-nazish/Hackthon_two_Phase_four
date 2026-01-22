# Tasks: Frontend Application

**Input**: Design documents from `/specs/003-frontend-app/`

**Organization**: Tasks grouped by user story for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: User story label (US1, US2, etc.)

---

## Phase 1: Setup

- [x] T001 Initialize Next.js with TypeScript and Tailwind in frontend/
- [x] T002 [P] Create TypeScript types in frontend/types/index.ts
- [x] T003 [P] Create cn utility in frontend/lib/utils.ts
- [x] T004 [P] Configure Tailwind in frontend/tailwind.config.ts
- [x] T005 Update root layout in frontend/app/layout.tsx
- [x] T006 Update globals.css in frontend/app/globals.css

---

## Phase 2: Foundational

- [x] T007 [P] Create Button in frontend/components/ui/button.tsx
- [x] T008 [P] Create Input in frontend/components/ui/input.tsx
- [x] T009 [P] Create Card in frontend/components/ui/card.tsx
- [x] T010 [P] Create Spinner in frontend/components/ui/spinner.tsx
- [x] T011 [P] Create Dialog in frontend/components/ui/dialog.tsx
- [x] T012 Create Toast in frontend/components/ui/toast.tsx
- [x] T013 Create useToast in frontend/hooks/use-toast.ts
- [x] T014 Create useAuth in frontend/hooks/use-auth.ts
- [x] T015 Create AuthGuard in frontend/components/auth/auth-guard.tsx
- [x] T016 Create Header in frontend/components/layout/header.tsx
- [x] T017 Create UserMenu in frontend/components/layout/user-menu.tsx

---

## Phase 3: US1 - Authentication (P1)

- [x] T018 [P] [US1] Create login page in frontend/app/(auth)/login/page.tsx
- [x] T019 [P] [US1] Create signup page in frontend/app/(auth)/signup/page.tsx
- [x] T020 [P] [US1] Create LoginForm in frontend/components/auth/login-form.tsx
- [x] T021 [P] [US1] Create SignupForm in frontend/components/auth/signup-form.tsx
- [x] T022 [US1] Create auth layout in frontend/app/(auth)/layout.tsx
- [x] T023 [US1] Wire LoginForm to Better Auth signIn
- [x] T024 [US1] Wire SignupForm to Better Auth signUp
- [x] T025 [US1] Create root redirect in frontend/app/page.tsx
- [x] T026 [US1] Create dashboard layout in frontend/app/(dashboard)/layout.tsx
- [x] T027 [US1] Create dashboard home in frontend/app/(dashboard)/page.tsx
- [x] T028 [US1] Add logout to UserMenu
- [x] T029 [US1] Handle token expiration in use-auth.ts

---

## Phase 4: US2 - Task Viewing (P1)

- [x] T030 [P] [US2] Create useTasks in frontend/hooks/use-tasks.ts
- [x] T031 [P] [US2] Create TaskItem in frontend/components/tasks/task-item.tsx
- [x] T032 [P] [US2] Create EmptyState in frontend/components/tasks/empty-state.tsx
- [x] T033 [P] [US2] Create TaskFilter in frontend/components/tasks/task-filter.tsx
- [x] T034 [US2] Create TaskList in frontend/components/tasks/task-list.tsx
- [x] T035 [US2] Create tasks page in frontend/app/(dashboard)/tasks/page.tsx
- [x] T036 [US2] Add visual distinction for completed tasks
- [x] T037 [US2] Implement filter logic in tasks/page.tsx
- [x] T038 [US2] Add loading state to TaskList

---

## Phase 5: US3 - Task Creation (P1)

- [x] T039 [P] [US3] Create TaskForm in frontend/components/tasks/task-form.tsx
- [x] T040 [US3] Add createTask to useTasks hook
- [x] T041 [US3] Add Add Task button and dialog in tasks/page.tsx
- [x] T042 [US3] Wire TaskForm to createTask API
- [x] T043 [US3] Add form validation (title required)
- [x] T044 [US3] Add success toast on creation
- [x] T045 [US3] Refresh task list after creation

---

## Phase 6: US4 - Task Toggle (P1)

- [x] T046 [US4] Add toggleComplete to useTasks
- [x] T047 [US4] Add checkbox UI to TaskItem
- [x] T048 [US4] Implement optimistic update
- [x] T049 [US4] Add CSS transition (150ms)
- [x] T050 [US4] Handle toggle error with rollback
- [x] T051 [US4] Update list state after toggle

---

## Phase 7: US5 - Task Editing (P2)

- [x] T052 [US5] Add updateTask to useTasks
- [x] T053 [US5] Add edit mode to TaskItem
- [x] T054 [US5] Reuse TaskForm for edit
- [x] T055 [US5] Wire edit to updateTask API
- [x] T056 [US5] Add cancel functionality
- [x] T057 [US5] Add validation error display
- [x] T058 [US5] Add success toast on edit

---

## Phase 8: US6 - Task Deletion (P2)

- [x] T059 [US6] Add deleteTask to useTasks
- [x] T060 [US6] Add delete button to TaskItem
- [x] T061 [US6] Create delete confirmation dialog
- [x] T062 [US6] Wire confirmation to deleteTask API
- [x] T063 [US6] Remove task from list on success
- [x] T064 [US6] Add error handling toast

---

## Phase 9: US7 - Responsive (P2)

- [x] T065 [P] [US7] Add responsive styles to Header
- [x] T066 [P] [US7] Add responsive styles to TaskList
- [x] T067 [P] [US7] Add responsive styles to TaskItem
- [x] T068 [P] [US7] Add responsive styles to TaskForm
- [x] T069 [US7] Add mobile nav in frontend/components/layout/nav.tsx
- [x] T070 [US7] Test touch targets
- [x] T071 [US7] Verify responsive breakpoints

---

## Phase 10: Polish

- [x] T072 [P] Add keyboard navigation
- [x] T073 [P] Add ARIA labels
- [x] T074 [P] Add focus indicators
- [x] T075 Add error boundary in frontend/app/error.tsx
- [x] T076 Add loading.tsx in frontend/app/(dashboard)/loading.tsx
- [x] T077 Verify user-friendly toast messages
- [x] T078 Add prefers-reduced-motion support
- [x] T079 Run accessibility audit
- [x] T080 Verify page load under 3s

---

## Summary

**Total Tasks**: 80 | **MVP (Phases 1-6)**: 51 | **Completed**: 80 | **Remaining**: 0

## Notes

- Use existing: frontend/lib/auth.ts, auth-client.ts, api-client.ts
- All UI uses Tailwind CSS
- All API calls via api-client.ts
