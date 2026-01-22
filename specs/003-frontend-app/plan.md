# Implementation Plan: Frontend Application

**Branch**: `003-frontend-app` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-frontend-app/spec.md`

## Summary

Build a professional, responsive SaaS-style UI for a multi-user Todo application using Next.js App Router. The frontend integrates with an existing FastAPI backend via JWT authentication (Better Auth) and provides full CRUD operations for task management. Foundation auth and API client infrastructure already exists; this plan focuses on building the user-facing pages, components, and state management.

## Technical Context

**Language/Version**: TypeScript 5.x, React 18, Next.js 14+ (App Router)
**Primary Dependencies**: Better Auth (auth), Tailwind CSS (styling), React Hook Form (forms), React Query/SWR (data fetching)
**Storage**: N/A (backend handles persistence; frontend uses session storage for JWT)
**Testing**: Jest + React Testing Library, Playwright (E2E)
**Target Platform**: Web (mobile-responsive: 320px - 2560px)
**Project Type**: Web frontend (Next.js App Router)
**Performance Goals**: <3s initial load, <200ms visual feedback on user actions
**Constraints**: Must work with existing Better Auth setup, JWT token flow, and FastAPI backend API contract
**Scale/Scope**: ~10 pages/routes, ~15-20 components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Library-First | N/A | Frontend app, not library |
| CLI Interface | N/A | UI application |
| Test-First | PASS | Will write tests before implementation |
| Integration Testing | PASS | E2E tests for auth flow and API integration |
| Observability | PASS | Console logging, error tracking |
| Simplicity | PASS | Minimal dependencies, standard patterns |

**Gate Result**: PASS - No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/003-frontend-app/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── (auth)/                    # Auth route group (no layout nesting)
│   │   ├── login/
│   │   │   └── page.tsx           # Login page
│   │   └── signup/
│   │       └── page.tsx           # Signup page
│   ├── (dashboard)/               # Protected route group
│   │   ├── layout.tsx             # Dashboard layout with nav/sidebar
│   │   ├── tasks/
│   │   │   ├── page.tsx           # Task list page
│   │   │   └── [id]/
│   │   │       └── page.tsx       # Task detail page (optional)
│   │   └── page.tsx               # Dashboard home (redirect to tasks)
│   ├── api/
│   │   └── auth/
│   │       └── [...all]/
│   │           └── route.ts       # Better Auth handler (EXISTS)
│   ├── layout.tsx                 # Root layout
│   ├── page.tsx                   # Landing/redirect page
│   └── globals.css                # Global styles
├── components/
│   ├── ui/                        # Reusable UI primitives
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── spinner.tsx
│   │   └── toast.tsx
│   ├── auth/                      # Auth-specific components
│   │   ├── login-form.tsx
│   │   ├── signup-form.tsx
│   │   └── auth-guard.tsx
│   ├── tasks/                     # Task-specific components
│   │   ├── task-list.tsx
│   │   ├── task-item.tsx
│   │   ├── task-form.tsx
│   │   ├── task-filter.tsx
│   │   └── empty-state.tsx
│   └── layout/                    # Layout components
│       ├── header.tsx
│       ├── nav.tsx
│       └── user-menu.tsx
├── hooks/                         # Custom React hooks
│   ├── use-tasks.ts               # Task CRUD operations
│   ├── use-auth.ts                # Auth state wrapper
│   └── use-toast.ts               # Toast notifications
├── lib/                           # Utilities (EXISTS)
│   ├── auth.ts                    # Better Auth server config (EXISTS)
│   ├── auth-client.ts             # Better Auth client (EXISTS)
│   ├── api-client.ts              # API client with JWT (EXISTS)
│   └── utils.ts                   # General utilities
├── types/                         # TypeScript types
│   └── index.ts                   # Shared type definitions
├── public/                        # Static assets
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.js
```

**Structure Decision**: Web application frontend structure using Next.js App Router conventions with route groups for auth vs protected routes. Component organization follows feature-based grouping (auth/, tasks/, ui/) for maintainability.

## Architectural Decisions

### Decision 1: Component Structure - Modular Feature-Based

**Decision**: Use modular feature-based component organization (auth/, tasks/, ui/, layout/) rather than flat structure.

**Rationale**:
- Clear separation of concerns by feature domain
- Easier navigation in larger codebases
- Encapsulates related components, hooks, and types together
- Scales well as features are added

**Alternatives Rejected**:
- Flat structure: Becomes unwieldy with 15+ components
- Atomic design: Over-engineered for this scope

### Decision 2: State Management - React Hooks + Context

**Decision**: Use React's built-in hooks (useState, useEffect) with Context for auth state, and custom hooks wrapping the API client for server state.

**Rationale**:
- No additional dependencies required
- Better Auth already provides useSession hook
- Task data is primarily server state (fetch on demand)
- Keeps bundle size small
- Sufficient for application complexity

**Alternatives Rejected**:
- Redux/Zustand: Over-engineered for this use case; no complex client state
- React Query/TanStack Query: Considered but custom hooks provide adequate caching; can add later if needed

### Decision 3: Styling - Tailwind CSS

**Decision**: Use Tailwind CSS for styling with custom configuration for design tokens.

**Rationale**:
- Industry standard for modern Next.js apps
- Utility-first approach speeds development
- Built-in responsive design utilities
- Small production bundle with purging
- Works seamlessly with Next.js

**Alternatives Rejected**:
- CSS Modules: Less productive for rapid development
- Styled Components: Runtime overhead, not needed for this scope
- Chakra/shadcn: Added complexity; Tailwind is sufficient

### Decision 4: API Client Integration - Global Wrapper (EXISTS)

**Decision**: Use existing global API client wrapper (`lib/api-client.ts`) with custom hooks per feature.

**Rationale**:
- API client already handles JWT attachment automatically
- Custom hooks (e.g., `useTasks`) provide clean interface for components
- Centralized error handling and response parsing
- Single point for auth token injection

**Implementation Pattern**:
```typescript
// hooks/use-tasks.ts
export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  // ... uses lib/api-client.ts under the hood
}
```

### Decision 5: Loading, Error, and Empty States

**Decision**: Implement consistent UI patterns for async states with dedicated components.

**Rationale**:
- Consistent user experience across all features
- FR-011 requires visual feedback for all actions
- Reusable components reduce code duplication

**Implementation Pattern**:
- `<Spinner />` - Inline and full-page loading indicators
- `<Toast />` - Success/error notifications
- `<EmptyState />` - Friendly empty list messaging
- Error boundary with fallback UI

### Decision 6: Animation and Transitions

**Decision**: Minimal, purposeful animations using CSS transitions and Tailwind's built-in animation utilities.

**Rationale**:
- SC-003 requires <200ms visual feedback
- Subtle transitions improve perceived performance
- No heavy animation library needed
- Accessibility-friendly (respects prefers-reduced-motion)

**Implementation**:
- Task completion toggle: checkbox fill animation (150ms)
- List updates: fade-in for new items (200ms)
- Page transitions: none (instant navigation)
- Toast notifications: slide-in/fade-out

## Complexity Tracking

> No violations requiring justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | - | - |

## Implementation Phases

### Phase 1: Foundation (UI Structure & Pages)

1. Initialize Next.js project with TypeScript and Tailwind CSS
2. Create base UI components (Button, Input, Card, Spinner, Toast)
3. Build root layout with global styles
4. Create auth route group with login/signup pages
5. Create protected dashboard route group with layout
6. Implement AuthGuard component for protected routes

**Validation Checkpoint**:
- [ ] `npm run dev` starts without errors
- [ ] Login page renders at `/login`
- [ ] Signup page renders at `/signup`
- [ ] Unauthenticated users redirected to login

### Phase 2: Integration (API Client + Auth)

1. Wire up Better Auth hooks in auth forms
2. Connect login form to signIn flow
3. Connect signup form to signUp flow
4. Implement logout functionality
5. Build user menu with session info
6. Handle token expiration redirect

**Validation Checkpoint**:
- [ ] Signup creates account successfully
- [ ] Login authenticates and redirects to dashboard
- [ ] Logout clears session and redirects to login
- [ ] Expired token shows "Session expired" and redirects

### Phase 3: Task Management (CRUD + UI)

1. Create task list component with API integration
2. Implement task item with completion toggle
3. Build task creation form/dialog
4. Add task editing inline or modal
5. Implement task deletion with confirmation
6. Add filter by completion status

**Validation Checkpoint**:
- [ ] Task list displays user's tasks
- [ ] New tasks appear after creation
- [ ] Completion toggle persists
- [ ] Edit updates task details
- [ ] Delete removes task after confirmation
- [ ] Filter shows correct subset

### Phase 4: Polish (States, Responsive, Accessibility)

1. Implement loading states for all async operations
2. Add error handling with toast notifications
3. Create empty state for no tasks
4. Ensure responsive layout (320px - 2560px)
5. Add keyboard navigation support
6. Test and fix accessibility issues

**Validation Checkpoint**:
- [ ] Loading spinners appear during fetch
- [ ] API errors show user-friendly toasts
- [ ] Empty state guides user to create first task
- [ ] Layout works on mobile (320px)
- [ ] Tab navigation works for all interactive elements
- [ ] Screen reader announces key actions

## API Contract Summary

The frontend consumes the existing backend API:

### Authentication
- `GET /api/v1/auth/session` - Verify session (returns user info)

### Tasks
- `GET /api/v1/users/{user_id}/tasks` - List tasks (supports ?completed=bool&limit=int&offset=int)
- `POST /api/v1/users/{user_id}/tasks` - Create task
- `GET /api/v1/users/{user_id}/tasks/{task_id}` - Get single task
- `PATCH /api/v1/users/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/v1/users/{user_id}/tasks/{task_id}` - Delete task

### Request/Response Models
```typescript
interface Task {
  id: string;           // UUID
  owner_id: string;
  title: string;        // 1-255 chars
  description?: string; // 0-2000 chars
  completed: boolean;
  created_at: string;   // ISO timestamp
  updated_at: string;   // ISO timestamp
}

interface TaskListResponse {
  items: Task[];
  total: number;
  limit: number;
  offset: number;
}

interface TaskCreate {
  title: string;
  description?: string;
  completed?: boolean;
}

interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}
```

## Testing Strategy

### Unit Tests (Jest + React Testing Library)
- Component rendering tests
- Form validation logic
- Hook behavior (mock API responses)
- State transitions

### Integration Tests
- Auth flow (login → dashboard)
- Task CRUD operations with mocked API
- Error state handling

### E2E Tests (Playwright)
- Full signup → create task → complete task → logout flow
- Responsive layout verification
- Auth token expiration handling

### Manual Testing Checklist
- [ ] Mobile (320px): All features functional
- [ ] Tablet (768px): Layout adapts correctly
- [ ] Desktop (1440px): Full experience
- [ ] Keyboard navigation complete
- [ ] Screen reader announces actions

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Better Auth session/token format changes | Auth breaks | Pin version, test on upgrade |
| API contract changes | Data mismatch | Generate types from OpenAPI |
| Slow network conditions | Poor UX | Optimistic updates, loading states |

## Success Criteria Mapping

| Spec SC | Implementation |
|---------|---------------|
| SC-001: 60s login-to-task flow | Minimal form fields, auto-redirect |
| SC-002: 2-click task creation | Floating action button + modal |
| SC-003: 200ms toggle feedback | CSS transition, optimistic update |
| SC-004: 95% first-attempt success | Clear validation, helpful errors |
| SC-005: 320px - 2560px support | Tailwind responsive utilities |
| SC-006: User-friendly errors | Toast with plain language |
| SC-007: <3s load time | Next.js optimizations, lazy loading |
| SC-008: Keyboard navigable | Focus management, ARIA labels |
