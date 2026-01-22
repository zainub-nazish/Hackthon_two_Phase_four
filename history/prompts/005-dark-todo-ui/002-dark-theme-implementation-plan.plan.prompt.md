---
id: 002
title: Dark Theme Implementation Plan
stage: plan
date: 2026-01-15
surface: agent
model: claude-opus-4-5-20251101
feature: 005-dark-todo-ui
branch: 005-dark-todo-ui
user: system
command: /sp.plan
labels: ["plan", "ui", "dark-theme", "tailwind", "frontend"]
links:
  spec: specs/005-dark-todo-ui/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-dark-todo-ui/plan.md
  - specs/005-dark-todo-ui/research.md
  - specs/005-dark-todo-ui/quickstart.md
tests:
  - N/A (planning document)
---

## Prompt

/sp.plan # Frontend UI Plan — Todo Web App

## Objective
Build a clean, dark, responsive UI enabling authenticated users to create, view, and manage tasks.

## Phases
1. Research - Dark mode contrast & usability
2. Foundation - Tailwind + global layout
3. Structure - Pages and components
4. Interaction - States and feedback
5. Auth Awareness - Better Auth integration
6. API Integration - REST endpoints
7. Responsive Polish
8. Validation

## Response snapshot

Created comprehensive implementation plan for Dark Theme Todo Web App UI:

**Technical Context**:
- TypeScript 5.x with Next.js 14+ (App Router)
- Tailwind CSS for styling
- Better Auth for session management
- ~15 component files to update

**Color Palette Mapping**:
| Purpose | New (Dark) |
|---------|------------|
| Background | #0F1115 |
| Surface | #1A1D23 |
| Primary (Teal) | #2DD4BF |
| Secondary (Amber) | #FBBF24 |
| Success | #22C55E |
| Text | #E5E7EB |

**Research Decisions (7 total)**:
1. WCAG 2.1 AA contrast compliance
2. Custom Tailwind color tokens (no dark: prefix)
3. Teal focus rings with 2px width
4. Pill-shaped status badges
5. Teal underline for active navigation
6. Subtle borders instead of shadows for cards
7. Amber primary buttons, surface secondary

**Implementation Phases (7)**:
1. Tailwind Configuration
2. Global Styles
3. UI Components
4. Layout Components
5. Task Components
6. Auth Components
7. Dashboard + AI Card

## Outcome

- Impact: Complete plan for dark theme transformation
- Tests: N/A (planning document)
- Files: 3 files created (plan.md, research.md, quickstart.md)
- Next prompts: `/sp.tasks` to generate implementation tasks
- Reflection: Frontend-only change, no backend or data model modifications needed

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check - PASS (all gates passed)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
