---
id: 006
title: Phase IV K8s Deployment Tasks
stage: tasks
date: 2026-02-24
surface: agent
model: claude-sonnet-4-6
feature: 013-todo-ai-chatbot
branch: 013-todo-ai-chatbot
user: system
command: /sp.tasks
labels: ["tasks", "kubernetes", "minikube", "gordon", "kubectl-ai", "kagent", "helm", "cloud-native", "phase-iv", "infra"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - specs/014-cloud-native-deployment/tasks.md
tests:
  - null
---

## Prompt

(empty — /sp.tasks invoked on active feature 013-todo-ai-chatbot / Phase IV deployment plan)

## Response snapshot

Generated `specs/014-cloud-native-deployment/tasks.md` with 37 tasks across 8 phases for
the Phase IV Cloud-Native Minikube deployment:

**Phase structure**:
- Phase 1 (Setup, 3 tasks): audit log + Helm skeleton initialisation
- Phase 2 (Foundational, 3 tasks): Minikube start, eval docker-env, verify context
- Phase 3/US1 (Backend Containerisation, 4 tasks): Gordon prompt → Dockerfile.backend → build → verify
- Phase 4/US2 (Frontend Containerisation, 5 tasks): Gordon prompt → Dockerfile.frontend → next.config.js check → build → verify
- Phase 5/US3 (K8s Scaffolding, 6 tasks): 5 parallel kubectl-ai manifest prompts + audit log
- Phase 6/US4 (Helm Deploy, 5 tasks): values.yaml → helm lint → create secret → helm install → log
- Phase 7/US5 (Kagent Verification, 7 tasks): pods watch → Kagent pass 1 → pass 2 → apply recommendations → UI verify
- Phase 8 (Polish, 4 tasks): audit completeness, lint, quickstart update, commit

**Key task design decisions**:
- Each Dockerfile/manifest task contains the EXACT agent prompt to delegate (immediately executable)
- US1 + US2 + US3 are fully parallel after Phase 2 (Foundational)
- US3 has 5 internal parallel kubectl-ai calls (T016–T020)
- Kagent tasks include failure protocol: refine prompt, never manually fix
- All tasks follow strict `- [ ] TXXX [P?] [US?] description` checklist format

## Outcome

- ✅ Impact: 37 tasks generated; all phases have independent verification checkpoints
- 🧪 Tests: N/A — verification via Kagent + minikube service (infra, not unit tests)
- 📁 Files: specs/014-cloud-native-deployment/tasks.md created
- 🔁 Next prompts: /sp.implement or launch infra-orchestrator agent to execute tasks
- 🧠 Reflection: Infrastructure tasks differ from software tasks — "tests" are replaced by
  health-check gates (Kagent, kubectl get pods, docker images). The agent delegation prompts
  embedded in each task make this immediately executable by the infra-orchestrator agent.

## Evaluation notes (flywheel)

- Failure modes observed: check-prerequisites.ps1 pointed to 013 (branch-based detection)
  instead of 014. Resolved by reading 014 artifacts directly.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): Infrastructure tasks with embedded agent prompts
- Next experiment (smallest change to try): Launch infra-orchestrator agent with tasks.md
  to validate that embedded prompts produce valid Gordon/kubectl-ai output
