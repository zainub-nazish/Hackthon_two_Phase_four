# Implementation Plan: Todo Full-Stack Web Application (Beautiful UI)

**Branch**: `004-fullstack-todo-app` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-fullstack-todo-app/spec.md`

## Summary

Build a production-ready Todo web application with secure, multi-user authentication via Better Auth and a modern, professional UI. The application uses Next.js App Router for the frontend with custom Tailwind components and FastAPI for the backend REST API, connected to Neon Serverless PostgreSQL.

**Focus**: Beautiful & Professional UI with clean SaaS-style design, responsive layout, and smooth user interactions.

## Technical Context

**Language/Version**: TypeScript 5.x (Frontend), Python 3.11+ (Backend)
**Primary Dependencies**:
- Frontend: Next.js 14+ (App Router), Better Auth, Tailwind CSS
- Backend: FastAPI, SQLModel, asyncpg
**Storage**: Neon Serverless PostgreSQL (shared by frontend auth and backend tasks)
**Testing**: Jest/React Testing Library (Frontend), pytest (Backend)
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Task operations < 2s, Page loads < 3s
**Constraints**: Responsive 320px-1920px, 7-day session validity
**Scale/Scope**: Single-user to multi-user, ~50 concurrent users initial capacity

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Simplicity | PASS | Custom components over heavy UI library, minimal dependencies |
| Test-First | ADVISORY | Testing recommended but not blocking for UI-focused feature |
| Security | PASS | Session-based auth, user isolation enforced at API level |
| Observability | PASS | Console logging for debugging, error states in UI |

No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/004-fullstack-todo-app/
├── plan.md              # This file
├── research.md          # Phase 0 output - UI patterns research
├── data-model.md        # Phase 1 output - entity definitions
├── quickstart.md        # Phase 1 output - setup guide
├── contracts/           # Phase 1 output - API contracts
│   └── openapi.yaml     # REST API specification
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── __init__.py
├── main.py              # FastAPI application entry
├── config.py            # Environment configuration
├── database.py          # Database connection management
├── auth/
│   ├── __init__.py
│   └── dependencies.py  # Auth middleware and session verification
├── models/
│   ├── __init__.py
│   ├── database.py      # SQLModel Task entity
│   └── schemas.py       # Pydantic request/response schemas
├── routes/
│   ├── __init__.py
│   ├── auth.py          # Auth-related routes
│   └── tasks.py         # Task CRUD endpoints
└── tests/
    └── ...

frontend/
├── app/
│   ├── layout.tsx       # Root layout with providers
│   ├── page.tsx         # Landing/redirect page
│   ├── (auth)/
│   │   ├── layout.tsx   # Auth pages layout
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx   # Dashboard layout with header
│   │   ├── page.tsx     # Dashboard home (redirects to /tasks)
│   │   └── tasks/page.tsx  # Main tasks page
│   └── api/auth/[...all]/route.ts  # Better Auth API handler
├── components/
│   ├── ui/              # Base UI components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   ├── spinner.tsx
│   │   └── toast.tsx
│   ├── auth/            # Auth-specific components
│   │   ├── auth-guard.tsx
│   │   ├── login-form.tsx
│   │   └── signup-form.tsx
│   ├── layout/          # Layout components
│   │   ├── header.tsx
│   │   └── user-menu.tsx
│   └── tasks/           # Task-specific components
│       ├── task-list.tsx
│       ├── task-item.tsx
│       ├── task-form.tsx
│       ├── task-filter.tsx
│       ├── delete-dialog.tsx
│       └── empty-state.tsx
├── hooks/
│   ├── use-auth.ts      # Authentication hook
│   ├── use-tasks.ts     # Tasks data management
│   └── use-toast.ts     # Toast notifications
├── lib/
│   ├── auth.ts          # Better Auth server config
│   ├── auth-client.ts   # Better Auth client utilities
│   ├── api-client.ts    # Authenticated API client
│   └── utils.ts         # Utility functions
├── types/
│   └── index.ts         # TypeScript type definitions
└── ...
```

**Structure Decision**: Web application with separate frontend (Next.js) and backend (FastAPI) directories. Both share the same Neon PostgreSQL database - Better Auth manages user/session tables, backend manages task table.

## Design Decisions

### UI Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Component Library | Custom Tailwind | Maximum flexibility, smaller bundle, no design conflicts |
| Layout Pattern | Top navigation | Simpler for task-focused app, better mobile experience |
| Task Display | Card-based | Better visual hierarchy, easier touch interactions |
| State Management | React hooks + context | Sufficient for app complexity, no Redux needed |
| Styling | Tailwind CSS | Rapid prototyping, consistent design tokens |

### UI Component Hierarchy

```
App Layout
├── Header (top-nav)
│   ├── Logo/Brand
│   └── UserMenu (avatar, sign out)
├── Main Content
│   └── TasksPage
│       ├── PageHeader (title, Add Task button)
│       ├── TaskFilterTabs (All/Pending/Completed)
│       └── TaskList
│           ├── TaskItem[] (cards)
│           │   ├── Checkbox (completion toggle)
│           │   ├── Title + Description
│           │   └── Actions (edit, delete)
│           └── EmptyState
└── Dialogs (portals)
    ├── AddTaskDialog
    ├── EditTaskDialog
    └── DeleteConfirmDialog
```

### Visual Design System

**Colors**:
- Primary: Indigo (#4F46E5) - buttons, links, focus states
- Success: Green (#10B981) - completed tasks
- Danger: Red (#EF4444) - delete actions
- Neutral: Gray scale for text and backgrounds

**Typography**:
- Font: System font stack (Inter, sans-serif fallback)
- Headings: Bold, larger sizes
- Body: Regular weight, comfortable line-height

**Spacing**:
- Base unit: 4px (Tailwind default)
- Card padding: 16-24px
- Section gaps: 24-32px

**Shadows & Borders**:
- Cards: Subtle shadow (shadow-sm to shadow-md)
- Borders: Light gray (border-gray-200)
- Rounded corners: rounded-lg (8px)

## Complexity Tracking

No violations requiring justification. The design follows simplicity principles:
- Minimal dependencies (no heavy UI frameworks)
- Standard patterns (REST API, session auth)
- Clear separation of concerns
