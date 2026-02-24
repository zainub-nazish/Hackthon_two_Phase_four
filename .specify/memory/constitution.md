<!--
SYNC IMPACT REPORT
==================
Version change: v1.1.0 → v1.2.0 (MINOR bump)
Rationale: New principles IX and X added for Agentic SRE / Kubernetes Orchestrator phase;
           new Infrastructure & Deployment Standards section added. No existing principles
           removed or redefined.

Modified principles: None renamed.
Added principles:
  - IX. Agentic Infrastructure Operations (Agentic Dev Stack for all infra provisioning)
  - X. No Manual Artifact Coding (Gordon, kubectl-ai, Kagent delegation mandate)

Added sections:
  - Technology Stack & Toolchain Constraints: extended with K8s/infra toolchain row
  - Infrastructure & Deployment Standards (new section)

Removed sections: None

Templates requiring updates:
  ✅ .specify/memory/constitution.md (this file)
  ⚠ .specify/templates/plan-template.md — Constitution Check section may need K8s/infra gates
  ⚠ .specify/templates/tasks-template.md — task phases may need Deployment phase template

Follow-up TODOs: None deferred.
-->

# Phase Four Constitution

## Core Principles

### I. Spec-First Development

Every feature begins as a written specification before any implementation. Code MUST NOT
be written until a spec exists and has been reviewed.

- Feature specs live in `specs/<feature>/spec.md`
- Plans live in `specs/<feature>/plan.md`
- Tasks live in `specs/<feature>/tasks.md`
- Implementation follows the spec; specs are updated to reflect approved changes
- This applies equally to infrastructure: specs precede Dockerfiles and K8s manifests

### II. Security by Design

Security is a first-class concern at every layer of the system.

- Secrets MUST be stored in `.env` and MUST NOT be committed to source control
- Authentication MUST be enforced at every API boundary
- Input validation MUST occur at all system entry points
- No hardcoded credentials, tokens, or keys in source code
- Container images MUST be scanned for vulnerabilities before deployment

### III. Deterministic Behavior

Systems MUST produce predictable, reproducible outputs for the same inputs.

- AI agent outputs MUST be logged for traceability
- Side effects MUST be isolated and explicit
- Configuration MUST be environment-driven, not code-embedded
- State mutations MUST be explicit and traceable
- Infrastructure provisioning MUST be idempotent

### IV. Separation of Concerns

Each layer of the system MUST have a single, well-defined responsibility.

- Frontend, backend, AI agent, MCP server, and infrastructure are independently deployable
- Database models MUST be separate from business logic
- Transport concerns MUST NOT bleed into domain logic
- Infrastructure code MUST NOT be co-located with application code
- Each AI specialist agent (Gordon, kubectl-ai, Kagent) has a single, bounded role

### V. Reproducibility & Traceability

Every action in the system MUST be reproducible and auditable.

- All AI agent decisions MUST be logged with agent identity and the prompt used
- Deployment operations MUST be recorded in `deployment-audit.log`
- Every significant change MUST reference a PHR or ADR
- Environment setups MUST be scripted and idempotent
- Log format: `[ISO-timestamp] [agent] [prompt-summary] [result-summary]`

### VI. API Standards

All service interfaces MUST adhere to explicit, versioned contracts.

- API contracts MUST be defined before implementation
- Breaking changes require a version bump and migration plan
- All APIs MUST return structured, typed responses
- Error taxonomy with HTTP status codes MUST be documented
- Idempotency, timeouts, and retry behavior MUST be specified per endpoint

### VII. AI Agent Safety

AI agents operating in the system MUST be bounded, logged, and safe to fail.

- Agents MUST operate within defined tool boundaries
- All tool calls MUST be logged with inputs, outputs, and agent identity
- Agents MUST handle tool failures gracefully without cascading errors
- No agent MAY perform destructive operations without explicit confirmation
- Prompt refinement (not manual fallback) is the required response to agent failure

### VIII. Stateless Conversation Architecture

The chat backend MUST be stateless; all conversation context is fetched per request.

- Each request MUST be self-contained: include full context fetched from the database
- Conversation history MUST be persisted to the database, not held in memory
- Agent instances MUST NOT retain cross-request state
- Horizontal scaling MUST be achievable without session affinity

### IX. Agentic Infrastructure Operations

All infrastructure provisioning MUST follow the Agentic Dev Stack workflow.

- **Workflow**: Write Spec → Generate Plan → Break into Tasks → Delegate to Specialist AI Agents
- **Gordon** MUST be used for all Docker image creation, optimization, and security scanning
  - Pattern: `docker ai "Create a multi-stage Dockerfile for [service] optimized for production"`
- **kubectl-ai** MUST be used for Kubernetes manifest generation and initial scaffolding
  - Pattern: `kubectl-ai "deploy [service] with [N] replicas and a [ServiceType] service"`
- **Kagent** MUST be used for cluster health analysis and Day 2 operations
  - Pattern: `kagent "analyze the cluster health and check for resource bottlenecks"`
- **Helm** MUST be used to package all AI-generated manifests into `/charts/todo-chatbot`
- If an agent tool fails, the prompt MUST be refined and re-submitted; no manual workaround
- The Minikube Docker context MUST be activated before any image build:
  `eval $(minikube docker-env)`
- A health-check command MUST be executed after every deployment step

### X. No Manual Artifact Coding

Dockerfiles and Kubernetes YAML manifests MUST NOT be hand-written by a human or AI assistant.

- Containerization artifacts: delegate exclusively to Gordon (`docker ai "<prompt>"`)
- Kubernetes manifests: delegate exclusively to kubectl-ai (`kubectl-ai "<prompt>"`)
- Cluster diagnostics and tuning: delegate exclusively to Kagent (`kagent "<prompt>"`)
- Helm chart structure MUST be assembled from AI-generated components, not authored manually
- Every AI-generated artifact MUST be recorded in `deployment-audit.log` with:
  - Agent name, full prompt used, output summary, and ISO timestamp

## Technology Stack & Toolchain Constraints

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | Next.js 16+ (App Router) | Auth-aware, responsive, SaaS-style UI |
| Backend API | FastAPI + SQLModel | Stateless chat and REST todo endpoints |
| AI Agent | OpenAI Agents SDK | Tool-based intent resolution |
| AI Chat UI | OpenAI ChatKit | Chatbot interface component |
| MCP Server | Official MCP SDK + FastAPI | Todo operation tool registry |
| Database | SQLModel + Neon PostgreSQL | Task, user, and conversation persistence |
| Authentication | Better Auth (JWT) | Mandatory on all protected routes |
| Container Runtime | Docker (via Gordon) | Multi-stage production images only |
| Orchestration | Kubernetes (Minikube) | Local cluster target |
| K8s Scaffolding | kubectl-ai | Manifest generation — no manual YAML |
| Cluster Ops | Kagent | Health checks, Day 2 ops, diagnostics |
| Packaging | Helm | Chart path: `/charts/todo-chatbot` |
| Container Registry | Minikube local registry | `eval $(minikube docker-env)` before builds |

## Infrastructure & Deployment Standards

### Deployment Workflow

1. Activate Minikube Docker context: `eval $(minikube docker-env)`
2. Build images using Gordon (within the Minikube Docker context)
3. Generate Kubernetes manifests using kubectl-ai
4. Package all manifests into the Helm chart at `/charts/todo-chatbot`
5. Deploy to the Minikube cluster using `helm upgrade --install`
6. Run a health-check command to verify each service is reachable
7. Use Kagent for cluster-wide post-deployment health analysis

### Health & Verification Gates

- A health-check command MUST be run after every deployment step
- Kagent MUST be used for cluster-wide health analysis after full deployment
- Services MUST be verified reachable at their exposed endpoints before proceeding
- Failed health checks MUST block subsequent deployment stages

### Audit Trail

- All agent delegations MUST be logged to `deployment-audit.log`
- Log format: `[ISO-timestamp] [AGENT] prompt="<prompt>" result="<one-line-summary>"`
- The audit log MUST be committed alongside deployment artifacts
- The audit log provides the authoritative record of which agent generated which resource

## Governance

This constitution supersedes all other development and operational practices.
Amendments require:

1. Documentation of the change and rationale
2. Version bump following semantic versioning:
   - MAJOR: backward-incompatible governance changes, principle removals or redefinitions
   - MINOR: new principle or section added, or materially expanded guidance
   - PATCH: clarifications, wording, typo fixes, non-semantic refinements
3. Sync propagation to dependent templates and command files
4. PHR creation recorded under `history/prompts/constitution/`

**Amendment Procedure**: Use `/sp.constitution` with the proposed changes. The agent MUST:
- Identify the version bump type (MAJOR/MINOR/PATCH) with rationale
- Update the constitution file with a Sync Impact Report HTML comment
- Propagate changes to dependent templates
- Create a PHR under `history/prompts/constitution/`

**Compliance Review**: All PRs MUST verify that changes comply with the active constitution.
Complexity violations MUST be documented in the Complexity Tracking section of the relevant
plan file.

**Runtime Guidance**: Consult `.specify/memory/constitution.md` (this file) as the
authoritative source for all project governance decisions.

**Version**: 1.2.0 | **Ratified**: 2026-01-12 | **Last Amended**: 2026-02-24
