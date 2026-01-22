# Implementation Plan: Dark Theme Todo Web App UI

**Branch**: `005-dark-todo-ui` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-dark-todo-ui/spec.md`

## Summary

Transform the existing Todo application frontend from the current light theme (Indigo/Gray) to a modern dark theme with teal (#2DD4BF) and amber (#FBBF24) accents on a near-black background (#0F1115). This involves updating the Tailwind color configuration, global styles, and all UI components to use the new dark color palette while maintaining existing functionality.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 14+ (App Router)
**Primary Dependencies**: Next.js, React 18, Tailwind CSS, Better Auth
**Storage**: N/A (frontend-only, existing backend unchanged)
**Testing**: Manual visual testing, TypeScript type checking, ESLint
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend modification only)
**Performance Goals**: Page interactive within 2 seconds, smooth 60fps transitions
**Constraints**: Must maintain existing functionality, no backend changes
**Scale/Scope**: ~15 component files to update, 1 color config file, 1 global CSS file

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| Simplicity | PASS | Modifying existing components, no new abstractions |
| Minimal Change | PASS | Color/style updates only, no structural changes |
| Existing Patterns | PASS | Uses existing Tailwind + React component patterns |
| Test Coverage | PASS | Visual verification sufficient for UI theme changes |

## Project Structure

### Documentation (this feature)

```text
specs/005-dark-todo-ui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # N/A (no data model changes)
├── quickstart.md        # Theme implementation guide
└── contracts/           # N/A (no API changes)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── globals.css           # Update: dark theme base styles
│   ├── layout.tsx            # Update: dark body classes
│   ├── (auth)/               # Update: dark auth forms
│   └── (dashboard)/          # Update: dark dashboard
├── components/
│   ├── ui/                   # Update: button, input, card, toast colors
│   ├── layout/               # Update: header, user-menu dark styles
│   └── tasks/                # Update: task components dark styles
├── tailwind.config.ts        # Update: dark color palette
└── lib/                      # No changes needed
```

**Structure Decision**: Modifying existing frontend structure - no new directories needed.

## Complexity Tracking

No violations - this is a straightforward color theme update using existing patterns.

## Color Palette Mapping

| Purpose | Current (Light) | New (Dark) |
|---------|-----------------|------------|
| Background | bg-gray-50 (#f9fafb) | bg-dark (#0F1115) |
| Surface | bg-white | bg-surface (#1A1D23) |
| Primary | primary-600 (#4f46e5) | primary (#2DD4BF) - teal |
| Secondary | gray-* | secondary (#FBBF24) - amber |
| Success | success-* (green) | success (#22C55E) |
| Danger | danger-* (red) | danger (#EF4444) |
| Text | text-gray-900 | text-light (#E5E7EB) |
| Text Muted | text-gray-500 | text-muted (#9CA3AF) |

## Implementation Phases

### Phase 1: Tailwind Configuration
- Update `tailwind.config.ts` with new dark color palette
- Add custom color tokens for dark, surface, primary (teal), secondary (amber)

### Phase 2: Global Styles
- Update `globals.css` with dark theme base styles
- Update `layout.tsx` body classes

### Phase 3: UI Components
- Update button.tsx, input.tsx, card.tsx, toast.tsx, dialog.tsx, spinner.tsx
- Replace all color references to use new palette

### Phase 4: Layout Components
- Update header.tsx with dark navigation styles
- Update user-menu.tsx with dark dropdown

### Phase 5: Task Components
- Update task-item.tsx with dark card styles and status badges
- Update task-list.tsx, task-form.tsx, task-filter.tsx, empty-state.tsx, delete-dialog.tsx

### Phase 6: Auth Components
- Update login-form.tsx and signup-form.tsx with dark form styles
- Update auth layout.tsx

### Phase 7: Dashboard
- Add AI Assistant card component
- Update dashboard layout and header

## Key Design Decisions

1. **Teal as Primary**: Use #2DD4BF for focus states, active indicators, links
2. **Amber for Actions**: Use #FBBF24 for primary buttons, pending badges
3. **Green for Success**: Use #22C55E for completed badges, success states
4. **Surface Cards**: Use #1A1D23 for all card backgrounds
5. **Subtle Borders**: Use semi-transparent borders for card edges
