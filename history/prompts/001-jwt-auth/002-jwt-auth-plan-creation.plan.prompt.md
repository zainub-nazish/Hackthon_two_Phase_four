---
id: 002
title: JWT Auth Implementation Plan
stage: plan
date: 2026-01-12
surface: agent
model: claude-opus-4-5-20251101
feature: 001-jwt-auth
branch: 001-jwt-auth
user: user
command: /sp.plan
labels: ["authentication", "jwt", "architecture", "fastapi", "better-auth", "security"]
links:
  spec: specs/001-jwt-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-jwt-auth/plan.md
  - specs/001-jwt-auth/research.md
  - specs/001-jwt-auth/data-model.md
  - specs/001-jwt-auth/quickstart.md
  - specs/001-jwt-auth/contracts/openapi.yaml
tests:
  - null
---

## Prompt

Create:
- High-level authentication architecture sketch (Frontend → Auth → Backend)
- JWT lifecycle flow (issue → attach → verify → decode → enforce)
- Middleware and request flow section structure
- Step-by-step implementation approach using Claude Code
- Security validation and enforcement checkpoints

Decisions needing documentation:
- JWT-based stateless authentication vs server-side sessions
- Better Auth as frontend auth provider vs custom auth logic
- JWT verification in FastAPI middleware vs per-route dependency
- Shared secret strategy via environment variables
- User identity source of truth (JWT claims vs URL parameters)
- Token expiration duration and handling strategy
- Error handling approach for invalid, missing, or expired tokens

Testing strategy:
- Verify JWT is issued on successful login
- Confirm Authorization: Bearer <token> header is attached on all API requests
- Validate FastAPI rejects requests without JWT (401 Unauthorized)
- Validate FastAPI rejects invalid or tampered JWTs
- Validate decoded user ID matches `{user_id}` in API routes
- Confirm cross-user access is impossible
- Validate token expiration behavior
- Confirm protected routes cannot be accessed without authentication

Technical details:
- Use spec-first, plan-driven approach (no manual coding)
- Organize work by phases:
  - Foundation: Define auth flow, JWT claims, and shared secret usage
  - Integration: Connect Better Auth JWT with FastAPI verification
  - Enforcement: Apply middleware and route-level protection
  - Validation: Security checks and failure case verification
- All secrets managed via environment variables (`BETTER_AUTH_SECRET`)
- Follow Spec-Kit Plus workflow strictly:
  Write spec → Generate plan → Break into tasks → Implement via Claude Code
- Ensure plan supports future extensibility without breaking security guarantees

## Response snapshot

Created comprehensive implementation plan with:

**Research Findings (research.md)**:
- JWT algorithm: HS256 (HMAC-SHA256)
- Library: python-jose[cryptography]
- Pattern: FastAPI dependency injection over middleware
- User identity: JWT `sub` claim is authoritative
- Error responses: 404 for unauthorized (IDOR prevention)
- Token expiration: Better Auth defaults with 10s clock skew leeway

**Key Architectural Decisions**:
- ADR-001: JWT-based stateless authentication (horizontal scaling, no session state)
- ADR-002: Dependency injection over middleware (fine-grained control, testable)
- ADR-003: 404 for unauthorized access (OWASP IDOR prevention)

**Implementation Phases**:
1. Foundation: Config, JWT dependency, Pydantic models
2. Backend Integration: Protected routes, ownership verification, CORS
3. Frontend Integration: Better Auth config, API client with token attachment
4. Validation: Security tests for all failure cases

**Artifacts Generated**:
- plan.md (architecture, phases, decisions)
- research.md (technology decisions)
- data-model.md (entities, relationships)
- contracts/openapi.yaml (API specification)
- quickstart.md (implementation guide)

## Outcome

- Impact: Complete architectural plan ready for task generation
- Tests: Testing strategy defined (unit + integration)
- Files: 5 planning artifacts created
- Next prompts: /sp.tasks to generate implementation tasks
- Reflection: Plan covers security requirements comprehensively with clear phases

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully
- Graders run and results (PASS/FAIL): All architectural decisions documented
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
