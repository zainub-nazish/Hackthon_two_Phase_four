# Research: Frontend Application

**Feature**: 003-frontend-app
**Date**: 2026-01-13
**Status**: Complete

## Technical Decisions

### TD-001: Framework Selection

**Decision**: Next.js 15+ with App Router

**Rationale**:
- User constraint explicitly requires Next.js with App Router
- App Router provides React Server Components for better performance
- Built-in routing, layouts, and loading states reduce boilerplate
- Native support for streaming and suspense

**Alternatives Considered**:
- Next.js Pages Router: Legacy, less performant, not specified
- Plain React + Vite: Missing server-side rendering, routing complexity
- Remix: Good alternative but user explicitly requested Next.js

---

### TD-002: Component Structure

**Decision**: Modular component architecture with feature-based organization

**Rationale**:
- Separates concerns: UI components, feature components, layouts
- Enables reuse of common UI elements (buttons, inputs, cards)
- Matches Next.js App Router file conventions
- Easier testing and maintenance

**Structure**:
```
frontend/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Auth route group (login/signup)
│   ├── (dashboard)/       # Protected routes
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/
│   ├── ui/                # Reusable UI primitives
│   └── features/          # Feature-specific components
├── lib/                   # Utilities and helpers
│   ├── api/              # API client
│   └── auth/             # Auth utilities
└── types/                 # TypeScript types
```

**Alternatives Considered**:
- Flat structure: Simpler but doesn't scale well
- Atomic design: More complex than needed for this scope

---

### TD-003: State Management

**Decision**: React hooks + Context API (minimal)

**Rationale**:
- User constraint: "All state management handled via React (hooks, context as needed)"
- App is simple enough that external state libraries add unnecessary complexity
- Server Components reduce client-side state needs
- Auth context for user session, local state for task operations

**Pattern**:
- `useAuth()` context for authentication state
- `useState/useReducer` for local component state
- Server Components fetch data directly (no client state needed)
- React Query/SWR NOT needed due to simple CRUD operations

**Alternatives Considered**:
- Redux/Zustand: Overkill for this application scope
- React Query: Good but adds dependency; manual fetch sufficient
- Jotai: Atomic state unnecessary for this use case

---

### TD-004: Styling Approach

**Decision**: Tailwind CSS

**Rationale**:
- User constraint explicitly mentions "Tailwind CSS or equivalent"
- Utility-first approach enables rapid UI development
- Built-in responsive design utilities
- No runtime CSS-in-JS overhead
- Excellent for SaaS-style minimal UI

**Configuration**:
- Default Tailwind config with minimal customization
- Use `cn()` utility for conditional classes (clsx + tailwind-merge)
- Consistent color palette for professional appearance

**Alternatives Considered**:
- CSS Modules: More verbose, less rapid development
- Styled Components: Runtime overhead, not specified
- shadcn/ui: Consider for pre-built components on top of Tailwind

---

### TD-005: API Client Integration

**Decision**: Global API client wrapper with automatic JWT attachment

**Rationale**:
- Centralizes authentication header logic
- Consistent error handling across all requests
- Single point for base URL configuration
- Matches FR-003: "System MUST attach the JWT token to all API requests automatically"

**Implementation**:
```typescript
// lib/api/client.ts
const apiClient = {
  async fetch(endpoint, options) {
    const token = getAuthToken();
    return fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });
  }
};
```

**Alternatives Considered**:
- Per-component fetch: Duplicates auth logic, error-prone
- Axios: Adds dependency; native fetch sufficient
- tRPC: Overkill without shared types with backend

---

### TD-006: Loading, Error, and Empty States

**Decision**: Consistent UI patterns with component-level handling

**Rationale**:
- Matches FR-011: "System MUST provide visual feedback for all user actions"
- Next.js App Router provides `loading.tsx` and `error.tsx` conventions
- Component-level states for inline feedback

**Patterns**:
- **Loading**: Skeleton loaders for lists, spinner for actions
- **Error**: Toast notifications for recoverable errors, error boundaries for fatal
- **Empty**: Friendly illustrations with call-to-action

**Components**:
- `<Skeleton />` - Loading placeholder
- `<Toast />` - Notification system
- `<EmptyState />` - No data placeholder

---

### TD-007: Animation and Transitions

**Decision**: CSS transitions + Tailwind animation utilities

**Rationale**:
- User requirement: "Smooth user interactions (animations, transitions)"
- CSS-native transitions are performant and simple
- Tailwind provides animation utilities out of the box
- Framer Motion NOT needed for this scope

**Usage**:
- `transition-all duration-200` for hover states
- `animate-pulse` for loading skeletons
- `transition-opacity` for fade effects on task completion
- Subtle scale transforms on button interactions

**Alternatives Considered**:
- Framer Motion: More powerful but adds 50KB+ bundle size
- React Spring: Overkill for simple transitions
- CSS Keyframes: Used via Tailwind when needed

---

### TD-008: Authentication Flow

**Decision**: Token stored in localStorage with AuthContext

**Rationale**:
- User constraint: "Custom authentication logic (handled by backend + JWT)"
- Frontend only manages token storage and attachment
- Better Auth on backend provides the actual auth

**Flow**:
1. User signs in via Better Auth UI/API
2. JWT token returned and stored in localStorage
3. AuthContext provides `user`, `token`, `isAuthenticated`
4. API client reads token from context/storage
5. Token expiry triggers redirect to login

**Security Considerations**:
- Use httpOnly cookies if available from backend (preferred)
- localStorage fallback for SPA compatibility
- Clear token on logout and expiry

---

### TD-009: Testing Strategy

**Decision**: Vitest + React Testing Library + Playwright E2E

**Rationale**:
- Vitest: Fast, ESM-native, Next.js compatible
- React Testing Library: Component behavior testing
- Playwright: Cross-browser E2E testing

**Coverage**:
- Unit tests for utility functions
- Component tests for UI behavior
- E2E tests for critical user flows (auth, CRUD)

---

## Dependency Summary

| Package | Version | Purpose |
|---------|---------|---------|
| next | ^15.0.0 | Framework |
| react | ^19.0.0 | UI Library |
| tailwindcss | ^3.4.0 | Styling |
| clsx | ^2.1.0 | Class utilities |
| tailwind-merge | ^2.2.0 | Class merging |
| typescript | ^5.3.0 | Type safety |
| vitest | ^2.0.0 | Unit testing |
| @testing-library/react | ^15.0.0 | Component testing |
| playwright | ^1.42.0 | E2E testing |

## API Integration

**Backend API Base URL**: `http://localhost:8000` (dev) / `https://api.example.com` (prod)

**Endpoints** (from 002-backend-api-data-layer OpenAPI):
- `GET /api/v1/users/{user_id}/tasks` - List tasks
- `POST /api/v1/users/{user_id}/tasks` - Create task
- `GET /api/v1/users/{user_id}/tasks/{task_id}` - Get task
- `PATCH /api/v1/users/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/v1/users/{user_id}/tasks/{task_id}` - Delete task

**Authentication**: Bearer JWT in Authorization header

## Resolved Unknowns

All technical context items have been resolved:
- Language/Version: TypeScript 5.3+ on Node.js 20+
- Primary Dependencies: Next.js 15+, React 19+, Tailwind CSS 3.4+
- Storage: N/A (backend handles persistence)
- Testing: Vitest + React Testing Library + Playwright
- Target Platform: Web (modern browsers)
- Project Type: Web application (frontend only)
- Performance Goals: <3s page load, <200ms interaction response
- Constraints: Responsive 320px-2560px, keyboard accessible
- Scale/Scope: Single user session, ~100 tasks typical usage
