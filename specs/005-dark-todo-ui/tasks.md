# Tasks: Dark Theme Todo Web App UI

**Input**: Design documents from `/specs/005-dark-todo-ui/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, quickstart.md

**Tests**: No automated tests required - visual verification as specified in spec.md

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/` directory with Next.js App Router structure
- **Components**: `frontend/components/` (ui/, layout/, tasks/, auth/)
- **Config**: `frontend/tailwind.config.ts`, `frontend/app/globals.css`

---

## Phase 1: Setup (Tailwind Configuration)

**Purpose**: Configure the dark theme color palette in Tailwind

- [x] T001 Update Tailwind config with dark theme colors in `frontend/tailwind.config.ts`
  - Add `dark: '#0F1115'` (background)
  - Add `surface: '#1A1D23'` (card backgrounds)
  - Update `primary` to teal `#2DD4BF` with hover `#14B8A6`
  - Add `secondary` amber `#FBBF24` with hover `#F59E0B`
  - Update `success: '#22C55E'` and `danger: '#EF4444'`
  - Add `light: '#E5E7EB'` and `muted: '#9CA3AF'` for text

---

## Phase 2: Foundational (Global Styles)

**Purpose**: Apply dark theme base styles that all components inherit

**⚠️ CRITICAL**: Must complete before any component updates

- [x] T002 Update global CSS with dark theme base in `frontend/app/globals.css`
  - Set body background to `bg-dark`
  - Set default text color to `text-light`
  - Add antialiased font smoothing

- [x] T003 Update root layout dark theme classes in `frontend/app/layout.tsx`
  - Apply `bg-dark text-light` to body element

**Checkpoint**: Foundation ready - dark background and light text visible across app

---

## Phase 3: User Story 1 - View Dashboard with Dark Theme (Priority: P1) 🎯 MVP

**Goal**: Users see dark-themed dashboard with proper colors, header, and layout

**Independent Test**: Load dashboard and verify background #0F1115, surface cards #1A1D23, centered header

### Implementation for User Story 1

- [x] T004 [P] [US1] Update Card component with surface background in `frontend/components/ui/card.tsx`
  - Change `bg-white` to `bg-surface`
  - Update border to `border-white/10`
  - Remove shadows, use subtle border instead

- [x] T005 [P] [US1] Update Spinner component colors in `frontend/components/ui/spinner.tsx`
  - Update spinner color to use `primary` (teal)

- [x] T006 [P] [US1] Update Dialog component dark styles in `frontend/components/ui/dialog.tsx`
  - Update overlay background
  - Update dialog surface to `bg-surface`
  - Update text colors to `text-light`

- [x] T007 [P] [US1] Update Toast component dark styles in `frontend/components/ui/toast.tsx`
  - Update success toast with `bg-success/20 text-success`
  - Update error toast with `bg-danger/20 text-danger`
  - Update default toast with `bg-surface`

- [x] T008 [US1] Update Dashboard page with dark theme in `frontend/app/(dashboard)/page.tsx`
  - Add centered header "Manage Your Tasks" with subtitle
  - Apply dark background classes
  - Style header text with `text-light`

- [x] T009 [US1] Update Dashboard layout dark styles in `frontend/app/(dashboard)/layout.tsx`
  - Apply `bg-dark` background
  - Ensure content area uses dark theme

- [x] T010 [US1] Update Dashboard loading state in `frontend/app/(dashboard)/loading.tsx`
  - Style loading spinner with dark theme

**Checkpoint**: Dashboard displays with near-black background, charcoal cards, light text

---

## Phase 4: User Story 2 - Create Task with Dark Form UI (Priority: P1)

**Goal**: Users create tasks with dark-themed form, teal focus states, amber submit button

**Independent Test**: Focus input fields (verify teal ring), click Create Task button (verify amber)

### Implementation for User Story 2

- [x] T011 [P] [US2] Update Input component with dark styling in `frontend/components/ui/input.tsx`
  - Change background to `bg-surface` or `bg-dark`
  - Update border to `border-white/20`
  - Add teal focus ring `focus:ring-primary focus:border-primary`
  - Update placeholder text to `text-muted`

- [x] T012 [P] [US2] Update Button component with dark theme variants in `frontend/components/ui/button.tsx`
  - Primary: `bg-secondary text-dark hover:bg-secondary-hover` (amber)
  - Secondary: `bg-surface text-light border-white/10 hover:bg-white/5`
  - Destructive: `bg-danger text-white hover:bg-danger/90`
  - Ghost: `text-light hover:bg-white/5`
  - Link: `text-primary underline-offset-4 hover:underline`

- [x] T013 [US2] Update Task Form component with dark styling in `frontend/components/tasks/task-form.tsx`
  - Apply dark card background
  - Style form labels with `text-light`
  - Ensure teal focus states on inputs
  - Style Create Task button with amber

**Checkpoint**: Task form has dark surface, teal focus rings, amber Create button

---

## Phase 5: User Story 3 - View Task Status with Visual Badges (Priority: P1)

**Goal**: Users see amber badges for pending tasks, green badges for completed tasks

**Independent Test**: View tasks with both statuses, verify badge colors match spec

### Implementation for User Story 3

- [x] T014 [P] [US3] Update Task Item component with dark styles and badges in `frontend/components/tasks/task-item.tsx`
  - Apply `bg-surface` card background
  - Add amber badge: `bg-secondary/20 text-secondary rounded-full px-2 py-0.5 text-xs`
  - Add green badge: `bg-success/20 text-success rounded-full px-2 py-0.5 text-xs`
  - Style task title with `text-light`
  - Style description with `text-muted`
  - Add hover state `hover:bg-white/5`

- [x] T015 [US3] Update Task List component with dark styling in `frontend/components/tasks/task-list.tsx`
  - Apply spacing and dark background
  - Ensure list container uses dark theme

- [x] T016 [US3] Update Task Filter component with dark styling in `frontend/components/tasks/task-filter.tsx`
  - Style filter buttons with dark theme
  - Active filter shows teal indicator

- [x] T017 [US3] Update Empty State component with dark styling in `frontend/components/tasks/empty-state.tsx`
  - Style empty message with `text-muted`
  - Add encouraging CTA text

- [x] T018 [US3] Update Delete Dialog with dark styling in `frontend/components/tasks/delete-dialog.tsx`
  - Apply dark surface background
  - Style destructive button with danger color

**Checkpoint**: Task list shows amber pending badges, green completed badges, dark cards

---

## Phase 6: User Story 4 - Navigate with Dark Top Navigation (Priority: P2)

**Goal**: Users navigate with dark nav bar, teal active indicator, user info displayed

**Independent Test**: Click nav links, verify teal underline on active link, user dropdown works

### Implementation for User Story 4

- [x] T019 [US4] Update Header component with dark navigation in `frontend/components/layout/header.tsx`
  - Apply `bg-surface` background to nav bar
  - Style app name "Task Management" with `text-light`
  - Add nav links: Dashboard, Tasks, AI Assistant
  - Active link: `text-primary border-b-2 border-primary`
  - Inactive link: `text-muted hover:text-light`
  - Add subtle bottom border `border-white/10`

- [x] T020 [US4] Update User Menu component with dark dropdown in `frontend/components/layout/user-menu.tsx`
  - Style dropdown with `bg-surface`
  - Style menu items with `text-light hover:bg-white/5`
  - Style user email with `text-muted`
  - Logout button with appropriate styling

**Checkpoint**: Dark nav bar with teal active indicator, working user dropdown

---

## Phase 7: User Story 5 - Access AI Assistant Card (Priority: P3)

**Goal**: Users see AI Assistant card placeholder with CTA button

**Independent Test**: View dashboard, verify AI card appears with proper styling and CTA

### Implementation for User Story 5

- [x] T021 [US5] Create AI Assistant card component in `frontend/components/dashboard/ai-assistant-card.tsx`
  - Create new component file
  - Apply `bg-surface` with teal accent border
  - Add icon and title "AI Assistant"
  - Add description text
  - Add "Open AI Assistant" CTA button (amber)
  - Style with rounded corners and subtle shadow/border

- [x] T022 [US5] Integrate AI Assistant card into Dashboard in `frontend/app/(dashboard)/page.tsx`
  - Import and render AI Assistant card
  - Position alongside task creation card

**Checkpoint**: AI Assistant card visible on dashboard with proper dark styling

---

## Phase 8: User Story 6 - Authenticated User Experience (Priority: P2)

**Goal**: Auth pages match dark theme, user isolation maintained

**Independent Test**: View login/signup pages, verify dark styling matches theme

### Implementation for User Story 6

- [ ] T023 [P] [US6] Update Login Form with dark styling in `frontend/components/auth/login-form.tsx`
  - Apply `bg-surface` card background
  - Style inputs with dark theme (teal focus)
  - Style login button with amber
  - Style link text with `text-primary`

- [ ] T024 [P] [US6] Update Signup Form with dark styling in `frontend/components/auth/signup-form.tsx`
  - Apply `bg-surface` card background
  - Style inputs with dark theme (teal focus)
  - Style signup button with amber
  - Style link text with `text-primary`

- [ ] T025 [P] [US6] Update Auth Layout with dark styling in `frontend/app/(auth)/layout.tsx`
  - Apply `bg-dark` background
  - Center form vertically
  - Add branding/logo area if present

- [ ] T026 [P] [US6] Update Login Page with dark styling in `frontend/app/(auth)/login/page.tsx`
  - Apply page-level dark styles
  - Style page title/heading

- [ ] T027 [P] [US6] Update Signup Page with dark styling in `frontend/app/(auth)/signup/page.tsx`
  - Apply page-level dark styles
  - Style page title/heading

- [ ] T028 [US6] Update Auth Guard component if needed in `frontend/components/auth/auth-guard.tsx`
  - Ensure loading state uses dark theme
  - Style redirect/loading message

**Checkpoint**: Login and signup pages fully styled with dark theme

---

## Phase 9: User Story 4 Extension - Tasks Page (Priority: P2)

**Goal**: Dedicated tasks page has full dark theme styling

**Independent Test**: Navigate to /tasks, verify all elements use dark theme

### Implementation for Tasks Page

- [x] T029 [US4] Update Tasks Page with dark styling in `frontend/app/(dashboard)/tasks/page.tsx`
  - Apply dark background
  - Style page header
  - Ensure task list integration works

**Checkpoint**: Tasks page fully styled with dark theme

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements and validation

- [ ] T030 Verify WCAG 2.1 AA contrast compliance across all components
- [ ] T031 Test responsive design at 320px, 768px, 1024px, 1920px viewports
- [ ] T032 Verify all focus states show teal ring (keyboard navigation)
- [ ] T033 Verify hover states work correctly on all interactive elements
- [ ] T034 Test all async operations show proper loading/error states
- [ ] T035 Run quickstart.md verification checklist
- [ ] T036 Remove any remaining light theme artifacts (white backgrounds, gray borders)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start here
- **Foundational (Phase 2)**: Depends on Phase 1 - BLOCKS all component work
- **User Stories (Phase 3-9)**: All depend on Phase 2 completion
  - P1 stories (US1, US2, US3) can run in parallel after Phase 2
  - P2 stories (US4, US6) can run in parallel after Phase 2
  - P3 story (US5) can run in parallel after Phase 2
- **Polish (Phase 10)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (Dashboard)**: Core layout, can start after Phase 2
- **US2 (Task Form)**: Depends on Button/Input from US1 components
- **US3 (Task Status)**: Can run parallel to US2
- **US4 (Navigation)**: Can run parallel to US1-3
- **US5 (AI Card)**: Depends on Card component, can start after US1
- **US6 (Auth)**: Independent, can run parallel to all others

### Parallel Opportunities

```bash
# After Phase 2 completes, these can run in parallel:

# US1 Components (Phase 3):
Task: T004 [P] [US1] Card component
Task: T005 [P] [US1] Spinner component
Task: T006 [P] [US1] Dialog component
Task: T007 [P] [US1] Toast component

# US2 Components (Phase 4):
Task: T011 [P] [US2] Input component
Task: T012 [P] [US2] Button component

# US3 Components (Phase 5):
Task: T014 [P] [US3] Task Item component

# US6 Components (Phase 8):
Task: T023 [P] [US6] Login Form
Task: T024 [P] [US6] Signup Form
Task: T025 [P] [US6] Auth Layout
Task: T026 [P] [US6] Login Page
Task: T027 [P] [US6] Signup Page
```

---

## Implementation Strategy

### MVP First (User Stories 1-3)

1. Complete Phase 1: Tailwind Configuration
2. Complete Phase 2: Global Styles (CRITICAL)
3. Complete Phase 3: US1 - Dashboard dark theme
4. Complete Phase 4: US2 - Task form dark styling
5. Complete Phase 5: US3 - Status badges
6. **STOP and VALIDATE**: Core functionality with dark theme complete
7. Demo/Deploy MVP

### Incremental Delivery

1. Setup + Foundational → Dark base ready
2. Add US1 (Dashboard) → Dark cards visible → Demo
3. Add US2 (Task Form) → Teal focus, amber buttons → Demo
4. Add US3 (Status Badges) → Amber/green badges → Demo (MVP Complete!)
5. Add US4 (Navigation) → Full dark nav → Demo
6. Add US5 (AI Card) → AI placeholder → Demo
7. Add US6 (Auth) → Dark login/signup → Demo
8. Polish phase → Final validation → Release

---

## Summary

| Phase | Story | Tasks | Priority |
|-------|-------|-------|----------|
| 1 | Setup | 1 | - |
| 2 | Foundational | 2 | - |
| 3 | US1 - Dashboard | 7 | P1 🎯 |
| 4 | US2 - Task Form | 3 | P1 |
| 5 | US3 - Task Status | 5 | P1 |
| 6 | US4 - Navigation | 2 | P2 |
| 7 | US5 - AI Card | 2 | P3 |
| 8 | US6 - Auth | 6 | P2 |
| 9 | US4 Ext - Tasks Page | 1 | P2 |
| 10 | Polish | 7 | - |
| **Total** | | **36** | |

---

## Notes

- [P] tasks = different files, no dependencies on each other
- [Story] label maps task to specific user story
- No backend changes required - frontend only
- Color reference: `quickstart.md` has all hex values and class mappings
- Research decisions: `research.md` has design rationale
- Visual verification is sufficient - no automated tests needed
