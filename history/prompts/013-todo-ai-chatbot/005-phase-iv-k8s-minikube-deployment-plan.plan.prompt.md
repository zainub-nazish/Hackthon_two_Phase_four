---
id: 005
title: Phase IV K8s Minikube Deployment Plan
stage: plan
date: 2026-02-24
surface: agent
model: claude-sonnet-4-6
feature: 013-todo-ai-chatbot
branch: 013-todo-ai-chatbot
user: system
command: /sp.plan
labels: ["plan", "kubernetes", "minikube", "gordon", "kubectl-ai", "kagent", "helm", "cloud-native", "phase-iv"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - specs/014-cloud-native-deployment/plan.md
  - specs/014-cloud-native-deployment/research.md
  - specs/014-cloud-native-deployment/data-model.md
  - specs/014-cloud-native-deployment/quickstart.md
  - specs/014-cloud-native-deployment/contracts/helm-values-schema.yaml
tests:
  - null
---

## Prompt

"Phase IV: Cloud Native Todo Chatbot Deployment on Minikube"

Objective: Deploy the Phase III Todo Chatbot using the Agentic Dev Stack (No manual coding).

Steps to generate:
1. **Environment Initialization**:
   - Verify `minikube` status and context.
   - Set up Docker environment to point to Minikube: `eval $(minikube docker-env)`.

2. **Containerization (via Gordon/Docker AI)**:
   - Use `docker ai` to generate optimized Multi-stage Dockerfiles for Frontend and Backend.
   - Build and tag images (`todo-frontend:latest`, `todo-backend:latest`) using Gordon's suggestions.

3. **Kubernetes Scaffolding (via kubectl-ai)**:
   - Use `kubectl-ai` to generate Deployment and Service manifests.
   - Requirements: 2 replicas for frontend, ClusterIP for backend, NodePort for frontend.

4. **Helm Chart Refactoring**:
   - Organize the generated manifests into a `/charts/todo-app` directory.
   - Use Claude to parameterize `values.yaml` for replica counts and image tags.

5. **Deployment & Audit (via Kagent)**:
   - Deploy using `helm install`.
   - Use `kagent "analyze the cluster health"` to verify pod stability.
   - Use `kagent "optimize resource allocation"` to set CPU/Memory limits based on initial runs.

Constraints:
- Every implementation task must start with a specific prompt for Gordon or kubectl-ai.
- Use `minikube service todo-frontend` to verify the final UI access.
- Document every AI-generated output in a `phase-iv-audit.log` file.

## Response snapshot

Generated a complete Phase IV implementation plan for cloud-native deployment of the
Todo Chatbot to Minikube using the Agentic Dev Stack:

**Artifacts created** (all under `specs/014-cloud-native-deployment/`):
- `plan.md` — full plan with Technical Context, Constitution Check (10/10 gates PASS),
  5-phase deployment workflow, agent delegation map, and ADR candidates
- `research.md` — 8 research decisions: Docker base images (python:3.11-slim,
  node:18-alpine), kubectl-ai prompt patterns, secrets management (K8s Secrets imperative),
  Helm single-chart strategy, Kagent 2-pass health check, imagePullPolicy:Never rationale,
  frontend→backend K8s DNS communication
- `data-model.md` — cluster topology diagram, all 6 K8s resource specs (2 Deployments,
  2 Services, 1 Secret, 1 ConfigMap), Helm values.yaml schema, audit log format
- `quickstart.md` — 10-step deployment guide: env setup, Gordon builds, secrets creation,
  kubectl-ai scaffolding, Helm packaging, Kagent verification, UI access, teardown
- `contracts/helm-values-schema.yaml` — JSON Schema for all Helm values parameters

**Architecture decisions surfaced**:
- `imagePullPolicy: Never` mandatory for Minikube local registry
- Backend exposed only via ClusterIP (internal); frontend via NodePort 30080
- K8s Secrets created imperatively (never in Git); ConfigMap for non-sensitive config
- Single Helm chart for both services (one `helm install`)

## Outcome

- ✅ Impact: Complete Phase IV implementation plan ready; all research and design artifacts generated
- 🧪 Tests: N/A (planning artifact — tests defined in tasks.md via /sp.tasks)
- 📁 Files: 5 new files in specs/014-cloud-native-deployment/
- 🔁 Next prompts: /sp.tasks to generate tasks.md with specific agent prompt tasks
- 🧠 Reflection: Infrastructure plans differ from software plans — "data model" is cluster
  topology, "contracts" are Helm values schema. The 5-phase workflow maps cleanly to the
  Agentic Dev Stack: Gordon → kubectl-ai → Helm → Kagent.

## Evaluation notes (flywheel)

- Failure modes observed: setup-plan.ps1 pointed to wrong feature (013 instead of 014)
  because no branch change. Resolved by creating 014 directory manually and writing
  artifacts directly.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): Infrastructure deployment plan (non-standard SDD usage)
- Next experiment (smallest change to try): Validate that /sp.tasks generates K8s-specific
  task phases (Environment Init, Containerisation, K8s Scaffolding, Helm, Verification)
