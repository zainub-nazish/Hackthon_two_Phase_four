# Feature Specification: Cloud-Native Todo Chatbot Deployment

**Feature Branch**: `014-cloud-native-deployment`
**Created**: 2026-03-01
**Status**: Draft
**Input**: User description: "Phase IV: Cloud Native Todo Chatbot Deployment on Minikube"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Access the Todo Chatbot via Browser (Priority: P1)

A developer or end user launches the fully deployed Todo Chatbot by pointing their browser to a locally accessible URL. The frontend loads, connects to the backend, and the chat interface is immediately functional — without any manual configuration or port-forwarding.

**Why this priority**: The primary deliverable is a running, accessible application. Without browser access, no other functionality can be verified by users.

**Independent Test**: Can be tested by running `minikube service todo-frontend` and confirming the browser opens to a working chat interface that can send and receive messages.

**Acceptance Scenarios**:

1. **Given** the Kubernetes cluster is running and Helm deployment is complete, **When** the user runs `minikube service todo-frontend`, **Then** a browser window opens to the Todo Chatbot UI with no errors.
2. **Given** the frontend is loaded, **When** the user submits a message, **Then** the chat interface receives a response from the backend without connection errors.
3. **Given** the cluster is running, **When** the frontend makes a request, **Then** it reaches the backend via internal cluster DNS resolution (not exposed IP).

---

### User Story 2 — Todo Data Persists Across Pod Restarts (Priority: P2)

A user creates one or more todo items using the chatbot. When backend pods are restarted (simulating a deployment, crash, or scaling event), previously created todo items remain intact and retrievable.

**Why this priority**: Data loss on pod restart is a fundamental reliability failure for any production-like environment. Persistent storage is what differentiates a real deployment from a demo.

**Independent Test**: Can be tested by creating a todo via the UI, deleting the backend pod, waiting for it to restart, and confirming the todo is still present.

**Acceptance Scenarios**:

1. **Given** a todo item has been created via the chat interface, **When** the backend pod is deleted (forcing a restart), **Then** the todo item is still present when the pod is back online.
2. **Given** the Persistent Volume Claim is bound, **When** the cluster is restarted, **Then** the data volume is remounted and all previous todos are accessible.

---

### User Story 3 — Healthy Cluster with Resource Guardrails (Priority: P3)

All deployed services show healthy status and enforce resource limits. No pod is allowed to consume unbounded CPU or memory. Liveness and readiness probes ensure traffic is only routed to healthy pods.

**Why this priority**: Resource limits and health checks prevent a single misbehaving pod from degrading the entire cluster. This is required for reliable local development workflows.

**Independent Test**: Can be tested by querying pod health status and verifying that resource limits are set, and that a pod with a failing readiness probe does not receive traffic.

**Acceptance Scenarios**:

1. **Given** the Helm chart is deployed, **When** `kubectl get pods` is run, **Then** all pods show `Running` status with `1/1` or `2/2` readiness within 2 minutes.
2. **Given** a pod's liveness probe fails, **When** the failure threshold is reached, **Then** Kubernetes automatically restarts the pod without manual intervention.
3. **Given** resource limits are configured, **When** a pod attempts to exceed its memory limit, **Then** it is OOM-killed and restarted rather than impacting other services.

---

### User Story 4 — Deploy and Manage via Helm (Priority: P4)

The entire application stack (frontend, backend, secrets, storage) is packaged as a single Helm chart. A developer can install, upgrade, or remove the entire application with a single command.

**Why this priority**: Helm packaging provides repeatable, version-controlled deployments and is the foundation for future CI/CD pipeline integration.

**Independent Test**: Can be tested by running `helm install`, confirming all resources are created, then running `helm uninstall` and confirming all resources are removed.

**Acceptance Scenarios**:

1. **Given** Helm is installed and Minikube is running, **When** `helm install todo-app ./charts/todo-app` is run, **Then** all frontend, backend, and storage resources are created in the cluster.
2. **Given** a Helm release is installed, **When** `helm uninstall todo-app` is run, **Then** all created resources are removed cleanly.
3. **Given** the chart values are updated, **When** `helm upgrade todo-app ./charts/todo-app` is run, **Then** the running deployment is updated without downtime.

---

### Edge Cases

- What happens when Minikube's Docker environment is not activated before building images? The images will not be available inside the cluster, and pods will fail to start.
- What happens when the Persistent Volume Claim cannot be bound? Backend pods will remain in `Pending` state and no data can be stored.
- What happens when the backend is unreachable from the frontend? The chat interface shows an error and should degrade gracefully rather than crashing.
- What happens when a pod's resource limits are set too low? The pod will be OOM-killed or throttled; limits must be calibrated to observed usage.
- What happens when `imagePullPolicy` is not set to `Never`? Kubernetes attempts to pull from a registry instead of the local Minikube daemon, causing `ErrImagePull` failures.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST deploy the frontend service with 2 replicas accessible via NodePort or LoadBalancer from the host machine.
- **FR-002**: System MUST deploy the backend API service as a ClusterIP service reachable from the frontend via Kubernetes internal DNS.
- **FR-003**: System MUST provision a Persistent Volume Claim for backend data storage that survives pod restarts.
- **FR-004**: System MUST configure liveness and readiness probes for all deployed services.
- **FR-005**: System MUST enforce CPU and memory resource requests and limits on all pods.
- **FR-006**: System MUST package all Kubernetes resources (frontend, backend, PVC, secrets config) into a single Helm chart at `charts/todo-app/`.
- **FR-007**: System MUST store all sensitive configuration (API keys, database credentials) as Kubernetes Secrets, never in chart values or source files.
- **FR-008**: All Dockerfiles and Kubernetes manifests MUST be generated via AI agents (Gordon, kubectl-ai, Kagent) with no hand-written infrastructure artifacts.
- **FR-009**: System MUST verify end-to-end connectivity: frontend successfully communicates with backend via cluster DNS.
- **FR-010**: Deployment MUST complete with all pods in `Running/Ready` state within 120 seconds of `helm install`.

### Key Entities

- **Frontend Service**: The React-based chat UI, deployed as a Kubernetes Deployment with 2 replicas and exposed via NodePort.
- **Backend Service**: The FastAPI-based API, deployed as a Kubernetes Deployment with ClusterIP access only (internal cluster communication).
- **Persistent Volume Claim (PVC)**: A storage resource bound to the backend service that retains todo data across pod lifecycles.
- **Helm Chart (`charts/todo-app`)**: The package that contains all Kubernetes resource templates, configurable via `values.yaml`.
- **Kubernetes Secret**: An in-cluster resource holding sensitive environment variables (database URL, API keys) — never committed to source control.
- **Agent Audit Log (`phase-iv-audit.log`)**: A file recording every AI agent delegation prompt and result for traceability.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All pods (frontend + backend replicas) reach `Running/Ready` state within 120 seconds of deployment completion.
- **SC-002**: The frontend is accessible in a browser via a single `minikube service` command with no additional configuration.
- **SC-003**: Todo items created before a pod restart are still present and retrievable after the pod returns to `Running` state.
- **SC-004**: A full deployment (`helm install`) and teardown (`helm uninstall`) cycle completes without manual cleanup of orphaned resources.
- **SC-005**: No Dockerfile or Kubernetes manifest artifact is hand-written — all are generated via AI agent prompts with results logged to the audit file.
- **SC-006**: All pods operate within defined resource limits; no pod consumes unbounded CPU or memory.
- **SC-007**: The Helm chart lints cleanly (`helm lint ./charts/todo-app` returns no errors) and installs idempotently.

## Assumptions

- The Phase III Todo Chatbot (FastAPI backend + Next.js frontend) is fully implemented with passing tests and is available as the source for containerisation.
- Minikube, Helm 3, Docker, and the required AI agent tools (Gordon, kubectl-ai, Kagent) are installed and available in the development environment.
- The database is an external service (Neon PostgreSQL) — it is NOT deployed to Kubernetes; it is accessed via a Kubernetes Secret.
- `imagePullPolicy: Never` is required for all pod specs since images are built directly into Minikube's Docker daemon.
- The deployment targets the `default` Kubernetes namespace.
- This is a local development deployment only — no production SLAs, TLS, or external ingress is required.

## Out of Scope

- Cloud (AWS/GCP/Azure) deployment — this feature covers local Minikube only.
- CI/CD pipeline integration — chart deployment is manual via `helm install` commands.
- TLS/HTTPS or external ingress configuration.
- Multi-environment (staging, production) Helm value overrides.
- Database migration within Kubernetes — the external Neon PostgreSQL handles all schema management.
