---
id: "004"
title: Todo Chatbot Hackathon II Constitution
stage: constitution
date: 2026-03-02
surface: agent
model: claude-sonnet-4-6
feature: none
branch: master
user: zainub-nazish
command: /sp.constitution
labels: ["constitution", "phase-v", "event-driven", "dapr", "kafka", "todo-chatbot"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

/sp.constitution

# speckit.constitution

## Project Constitution – Todo Chatbot (Hackathon II: Spec-Driven Development)

**Version**: 1.0
**Last Updated**: March 2025
**Purpose**: This is the unbreakable foundation of the entire project.
Every specification, plan, task, code change, architecture decision, prompt to Claude, and deployment step **MUST** strictly obey this constitution.
Any violation must be explicitly justified with a new task that amends this file.

### 1. Core Project Goals & Non-Negotiable Outcomes
- Build a production-grade **event-driven Todo Chatbot** with full advanced features
- Complete **all** required features from Phase V:
  - Recurring Tasks (with auto-generation of next occurrence)
  - Due Dates + Reminders (exact-time delivery, no polling)
  - Priorities, Tags, Search, Filter, Sort (intermediate features)
- Use **Dapr** sidecars everywhere (Pub/Sub, State, Jobs/Scheduler, Secrets, Service Invocation)
- Use **Kafka** (or Redpanda) for decoupled event-driven architecture
- Deploy successfully on **Minikube** (local) → **Oracle OKE / AKS / GKE** (cloud)
- Zero manual coding → 100% agent-generated via Claude Code + Spec-KitPlus workflow
- Public GitHub repo with perfect documentation + 90-second demo video

### 2. Absolute Technology & Stack Rules (No Exceptions)
[Full tech stack table with FastAPI, SQLModel, Next.js 14, Neon DB, Kafka via Dapr, OKE, GitHub Actions, Dapr Jobs API, forbidden practices]

### 3. Architecture & Design Principles
[Event-First Mindset, Service Boundaries, Dapr Usage Mandatory & Full — 3 Kafka topics: task-events, reminders, task-updates]

### 4. Security & Safety Rules
[No secrets in code, input validation, prepared statements, HTTPS, rate limiting]

### 5. Code Quality & Agent Behavior Rules
[File header comment template for Python and YAML; PHR and ADR requirements]

## Response snapshot

- Loaded existing constitution template at `.specify/memory/constitution.md` (contained placeholder tokens)
- Identified all placeholder tokens: PROJECT_NAME, PRINCIPLE_1–6, SECTION_2–3, GOVERNANCE_RULES, CONSTITUTION_VERSION, RATIFICATION_DATE, LAST_AMENDED_DATE
- Derived values from provided constitution content (Hackathon II, March 2025, SDD workflow)
- Version set to **1.0.0** (initial ratification fill — no prior version)
- Replaced all placeholders with concrete content across 5 sections + Governance
- Constitution written to `.specify/memory/constitution.md` with SYNC IMPACT REPORT HTML comment
- Consistency propagation:
  - `plan-template.md` ✅ — Constitution Check gate already present
  - `spec-template.md` ✅ — aligned with SDD workflow requirements
  - `tasks-template.md` ✅ — task format matches code quality rules
- PHR 004 created at `history/prompts/constitution/004-todo-chatbot-hackathon-ii-constitution.constitution.prompt.md`

## Outcome

- ✅ Impact: Project constitution v1.0.0 ratified and written; all placeholder tokens resolved; SDD + Dapr + Kafka + OKE governance rules now encoded
- 🧪 Tests: N/A (constitution is a governance document, not code)
- 📁 Files: .specify/memory/constitution.md (updated), history/prompts/constitution/004-todo-chatbot-hackathon-ii-constitution.constitution.prompt.md (created)
- 🔁 Next prompts: `/speckit-specify-phase-v` → generate speckit.specify from this constitution; `/speckit-plan-phase-v` → generate architecture plan
- 🧠 Reflection: Constitution cleanly encoded 5 principles + full tech stack table. Section 5 header comment format established for all agent-generated files.

## Evaluation notes (flywheel)

- Failure modes observed: None — constitution filled completely from provided content
- Graders run and results (PASS/FAIL): All placeholder tokens resolved (PASS); Version line matches report (PASS); Dates ISO format (PASS); No bracket tokens remaining (PASS)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add NFR section to constitution for performance budgets (p95 latency, throughput caps)
