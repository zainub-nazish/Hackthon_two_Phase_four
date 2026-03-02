<!--
SYNC IMPACT REPORT
==================
Version change: template (unversioned) → 1.0.0
Modified principles: N/A (initial fill from template)
Added sections:
  - Core Project Goals & Non-Negotiable Outcomes
  - Absolute Technology & Stack Rules
  - Architecture & Design Principles
  - Security & Safety Rules
  - Code Quality & Agent Behavior Rules
  - Governance
Removed sections: None (template placeholders replaced)
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ aligned (Constitution Check gate already present)
  - .specify/templates/spec-template.md ✅ aligned (no constitution-specific refs needed)
  - .specify/templates/tasks-template.md ✅ aligned (task format matches code quality rules)
Follow-up TODOs:
  - Section 5 (Code Quality) header comment format is partially defined; team should confirm
    Python vs YAML header style matches all services
  - RATIFICATION_DATE kept as 2025-03-01 (closest to "March 2025" stated in doc)
-->

# Todo Chatbot Constitution

## 1. Core Project Goals & Non-Negotiable Outcomes

Every specification, plan, task, code change, architecture decision, prompt to Claude, and
deployment step MUST strictly obey this constitution. Any violation must be explicitly
justified with a new task that amends this file.

- Build a production-grade **event-driven Todo Chatbot** with full advanced features.
- Complete **all** required features from Phase V:
  - Recurring Tasks (with auto-generation of next occurrence)
  - Due Dates + Reminders (exact-time delivery, no polling)
  - Priorities, Tags, Search, Filter, Sort (intermediate features)
- Use **Dapr** sidecars everywhere — Pub/Sub, State, Jobs/Scheduler, Secrets, Service Invocation.
- Use **Kafka** (or Redpanda) for decoupled, event-driven architecture.
- Deploy successfully on **Minikube** (local) → **Oracle OKE / AKS / GKE** (cloud).
- Zero manual coding — 100% agent-generated via Claude Code + Spec-KitPlus workflow.
- Public GitHub repo with perfect documentation + 90-second demo video.

## 2. Absolute Technology & Stack Rules

The following stack choices are non-negotiable. Deviations require an explicit constitution
amendment task.

| Layer               | Technology / Choice                                     | Constraint                                                       |
|---------------------|---------------------------------------------------------|------------------------------------------------------------------|
| Backend             | FastAPI + Python 3.11+                                  | Async, modern, excellent OpenAPI                                 |
| ORM / Models        | SQLModel                                                | Type-safe; combines Pydantic + SQLAlchemy                        |
| Frontend            | Next.js 14+ (App Router) + Chat UI components           | Vercel-friendly, good for real-time                              |
| Database            | Neon Serverless PostgreSQL                              | Free tier, branching, scale-to-zero                              |
| Pub/Sub             | Kafka via Dapr (preferred: Redpanda Cloud free tier)    | No Zookeeper pain, fast, Kafka-compatible                        |
| Distributed Runtime | Dapr (sidecar in every pod)                             | Abstracts Kafka, DB, secrets, scheduling — zero vendor lock-in   |
| Kubernetes          | Minikube → Oracle OKE (always free) preferred           | 4 OCPU / 24 GB free forever — best learning platform             |
| CI/CD               | GitHub Actions                                          | Free, integrates with repo                                       |
| Secrets             | Dapr + Kubernetes secret store                          | Portable, secure, no env var leakage                             |
| Scheduling          | Dapr Jobs API (not cron bindings)                       | Exact-time execution, no polling overhead                        |

**Strictly forbidden** (no exceptions without constitution amendment):
- Direct kafka-python / aiokafka usage — MUST go through Dapr Pub/Sub.
- Polling for reminders or recurring tasks.
- Blocking I/O in event handlers.
- Hardcoded URLs or credentials anywhere in source or Helm values.
- Adding new databases (Redis, Mongo, etc.) without amending this constitution.

## 3. Architecture & Design Principles

### I. Event-First Mindset

Every important action MUST publish an event to the appropriate Kafka topic via Dapr Pub/Sub.
Services MUST NOT call each other directly except via Dapr Service Invocation when synchronous
communication is genuinely required.

Core Kafka topics:
- `task-events`  — CRUD operations, task completion, recurring spawn
- `reminders`    — due-date set → scheduled reminder delivery
- `task-updates` — real-time WebSocket broadcast to connected clients

### II. Service Boundaries

Each service MUST have exactly one responsibility and communicate only via its defined topic
subscriptions. The boundaries are:

- **Chat API / MCP Backend** — only entry point for all user commands
- **Recurring Task Service** — consumes `task-events`; creates next task instance
- **Notification Service** — consumes `reminders` topic; sends push/email
- **Audit Service** — logs every event to an immutable append-only store
- **WebSocket Service** — broadcasts `task-updates` to connected clients

### III. Dapr Usage — Mandatory and Full

All inter-service communication and infrastructure access MUST go through Dapr building blocks:

| Building Block      | Usage                                                    |
|---------------------|----------------------------------------------------------|
| Pub/Sub             | All Kafka communication (publish + subscribe)            |
| State               | Conversation memory + short-lived task cache             |
| Jobs API            | Exact-time reminder & recurring spawn triggers           |
| Secrets             | All credentials (Neon, Kafka, OpenAI, etc.)              |
| Service Invocation  | Internal service-to-service synchronous calls            |

### IV. Test-Driven Implementation

All implementation tasks MUST follow Red-Green-Refactor:
1. Write failing tests that define the expected behavior (Red).
2. Implement the minimum code to make tests pass (Green).
3. Refactor for clarity and quality without changing behavior (Refactor).

No task may be marked complete unless its tests pass.

### V. Spec-Driven Development (SDD) Workflow

All work MUST flow through the SDD pipeline in sequence:

```
speckit.specify → speckit.plan → speckit.tasks → implement → validate
```

- No code without an approved Task ID from `speckit.tasks`.
- No task without a traceable requirement in `speckit.specify`.
- No architecture change without updating `speckit.plan`.

## 4. Security & Safety Rules

- MUST NOT commit secrets — use Dapr / Kubernetes secrets exclusively.
- MUST validate and sanitize every user input at system boundaries.
- MUST use prepared statements / SQLModel — no raw SQL string concatenation.
- MUST NOT store or process illegal or harmful content.
- MUST enforce HTTPS everywhere in production.
- MUST rate-limit public endpoints when exposed to the internet.

## 5. Code Quality & Agent Behavior Rules

Every generated file MUST contain this header comment (adapted for language):

**Python:**
```python
# ============================================================
# Task ID  : T-XXX-000
# Title    : <task title from speckit.tasks>
# Spec Ref : speckit.specify → <section and requirement ID>
# Plan Ref : speckit.plan → <section and component>
# ============================================================
```

**YAML / Helm templates:**
```yaml
# Task ID  : T-XXX-000
# Spec Ref : speckit.specify → <section>
# Plan Ref : speckit.plan → <section>
```

Additional rules:
- Every Prompt History Record (PHR) MUST be created after every user prompt.
- ADR suggestions MUST be surfaced for every architecturally significant decision.
- Agent MUST NOT implement features not present in `speckit.specify`.
- Agent MUST NOT change architecture defined in `speckit.plan` without user approval.
- Agent MUST stop and report rather than brute-force past blockers.

## Governance

This constitution SUPERSEDES all other project practices and documentation.

**Amendment procedure:**
1. Create a new task that explicitly targets this file.
2. Document the change rationale in an ADR.
3. Update all dependent artifacts (speckit.specify, speckit.plan, templates) in the same PR.
4. Bump the constitution version according to semantic versioning:
   - MAJOR: removal or redefinition of a non-negotiable rule
   - MINOR: addition of a new principle or mandatory section
   - PATCH: clarification, wording, or non-semantic refinement

**Compliance review:**
- Every PR MUST verify the Constitution Check gates in `plan.md`.
- Every spec MUST reference at least one constitutionally mandated requirement.
- Any violation found post-merge MUST be corrected in the next sprint with a new task.

**Version**: 1.0.0 | **Ratified**: 2025-03-01 | **Last Amended**: 2026-03-02
