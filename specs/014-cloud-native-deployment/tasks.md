---
description: "Task list for Phase IV — Cloud-Native Todo Chatbot Deployment on Minikube"
---

# Tasks: Phase IV — Cloud-Native Todo Chatbot Deployment

**Input**: Design documents from `/specs/014-cloud-native-deployment/`
**Prerequisites**: plan.md ✅ · spec.md ✅ · research.md ✅ · data-model.md ✅ · contracts/ ✅ · quickstart.md ✅

**Tests**: No unit/integration tests — verification is via Kagent health analysis,
`minikube service todo-frontend` browser access, and pod lifecycle checks. Each phase has a
clear infrastructure health-check gate.

**Organization**: Tasks are grouped by user story to enable independent implementation and
testing of each story.

> **Agent Delegation Rule** (Constitution IX + X): Every task that generates a Dockerfile or
> K8s manifest MUST use the exact agent prompt from plan.md. No hand-written artifacts.
> All agent calls MUST be appended to `phase-iv-audit.log` at the repo root.

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no ordering dependency)
- **[Story]**: Which user story this task belongs to (US1–US4)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialise the audit trail, verify toolchain, and scaffold the Helm chart directory
before any agent work begins.

- [x] T001 Create `phase-iv-audit.log` at repo root with header: `# Phase IV Agent Delegation Audit Log — format: [ISO-timestamp] [AGENT] prompt="..." result="..."`
- [x] T002 [P] Verify all required tools are available in PATH: `minikube version`, `helm version`, `kubectl version`, `docker version`, `docker ai --version`, `kubectl-ai --version`, `kagent --version`
- [x] T003 Run `helm create charts/todo-app` at repo root to scaffold chart skeleton, then delete all auto-generated files inside `charts/todo-app/templates/` (keep `Chart.yaml`, `values.yaml`, `.helmignore`)
- [x] T004 [P] Update `charts/todo-app/Chart.yaml`: set `name: todo-app`, `description: Phase IV Todo Chatbot on Minikube`, `version: 0.1.0`, `appVersion: "1.0.0"`

**Checkpoint**: `charts/todo-app/` exists with `Chart.yaml`; `phase-iv-audit.log` exists at repo root; all tools respond to `--version`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Activate Minikube cluster, switch Docker CLI to Minikube's internal daemon, and
create pre-install K8s resources (Secret, ConfigMap). All image builds and Helm install depend
on this phase being complete.

**⚠️ CRITICAL**: No image builds or deployments can succeed until T007 (Docker context) is verified.

- [x] T005 Start Minikube cluster: `minikube start`, then verify: `minikube status` — `host: Running`, `kubelet: Running`, `apiserver: Running`
- [x] T006 Enable Minikube addons: `minikube addons enable dashboard` and `minikube addons enable metrics-server`
- [x] T007 Activate Minikube Docker context: `eval $(minikube docker-env)` — verify with `docker ps` that output shows Minikube internal containers (e.g., `k8s_coredns_*`), NOT host Docker containers
- [x] T008 Create K8s Secret imperatively (values from `.env`): `kubectl create secret generic todo-backend-secret --from-literal=DATABASE_URL="$DATABASE_URL" --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET"` — verify: `kubectl get secret todo-backend-secret`
- [x] T009 Create K8s ConfigMap: `kubectl create configmap todo-frontend-config --from-literal=NEXT_PUBLIC_API_URL="http://todo-backend:8000"` — verify: `kubectl get configmap todo-frontend-config`
- [x] T010 Append environment init to `phase-iv-audit.log`: `[<ISO-timestamp>] [ENV] prompt="minikube start + eval $(minikube docker-env)" result="Minikube Running, Docker context switched"`

**Checkpoint**: `minikube status` all Running; `docker ps` shows Minikube containers; Secret and ConfigMap exist in cluster.

---

## Phase 3: US1 — Browser Access via Minikube (Priority: P1) 🎯 MVP Gate

**Goal**: Deploy the full Todo Chatbot stack to Minikube and access the frontend UI in a
browser via `minikube service todo-frontend` with no additional configuration.

**Independent Test**: Run `minikube service todo-frontend` after Helm install — browser opens
to the Todo Chatbot UI and a chat message receives a backend response without errors.

### Sub-Phase A: Containerization (Gordon)

- [x] T011 [P] [US1] Review `backend/` source: confirm entry point, port 8000 in uvicorn CMD, and all required env vars (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET) — confirm `backend/requirements.txt` exists
- [x] T012 [P] [US1] Review `frontend/` source: confirm port 3000, `output: 'standalone'` in `frontend/next.config.js`, and required env var NEXT_PUBLIC_API_URL
- [x] T013 [US1] Generate `Dockerfile.backend` via Gordon: `docker ai "Create a multi-stage Dockerfile for a FastAPI Python 3.11 application. Stage 1: install dependencies from backend/requirements.txt. Stage 2: copy only installed packages and backend/ source. Use python:3.11-slim. Run as non-root user appuser. Expose port 8000. CMD: uvicorn backend.main:app --host 0.0.0.0 --port 8000"` — save output to `Dockerfile.backend`
- [x] T014 [US1] Generate `Dockerfile.frontend` via Gordon: `docker ai "Create a multi-stage Dockerfile for a Next.js 14 application in frontend/. Stage 1 (deps): npm ci from package.json. Stage 2 (builder): npm run build, NEXT_TELEMETRY_DISABLED=1. Stage 3 (runner): copy .next/standalone and .next/static from builder. Use node:18-alpine. Run as non-root user nextjs:nodejs. Expose port 3000. CMD: node server.js"` — save output to `Dockerfile.frontend`
- [x] T015 [US1] Append both Gordon calls to `phase-iv-audit.log` (one line per Dockerfile generated with prompt + result)
- [x] T016 [US1] Build backend image inside Minikube Docker context: `docker build -t todo-backend:latest -f Dockerfile.backend .` — verify size < 300MB via `docker images todo-backend`
- [x] T017 [US1] Build frontend image inside Minikube Docker context: `docker build -t todo-frontend:latest -f Dockerfile.frontend ./frontend` — verify size < 150MB via `docker images todo-frontend`
- [x] T018 [US1] Verify both images in Minikube registry: `docker images | grep todo` — both `todo-backend:latest` AND `todo-frontend:latest` MUST appear (requires Minikube running)

### Sub-Phase B: Kubernetes Manifests (kubectl-ai)

- [x] T019 [P] [US1] Generate backend Deployment via kubectl-ai: prompt — `"Create Kubernetes Deployment for todo-backend: image todo-backend:latest, imagePullPolicy Never, replicas 2, port 8000, inject all keys from Secret todo-backend-secret as env vars, resources requests cpu=100m memory=128Mi limits cpu=500m memory=512Mi, liveness+readiness probes GET /health initialDelay 15/10 period 30/15"` — output to `charts/todo-app/templates/backend-deployment.yaml`
- [x] T020 [P] [US1] Generate backend ClusterIP Service via kubectl-ai: prompt — `"Create ClusterIP Service for todo-backend, selector app=todo-backend, port 8000 targetPort 8000"` — output to `charts/todo-app/templates/backend-service.yaml`
- [x] T021 [P] [US1] Generate frontend Deployment via kubectl-ai: prompt — `"Create Kubernetes Deployment for todo-frontend: image todo-frontend:latest, imagePullPolicy Never, replicas 2, containerPort 3000, inject all keys from ConfigMap todo-frontend-config as env vars, resources requests cpu=50m memory=64Mi limits cpu=200m memory=256Mi, liveness+readiness probes GET / initialDelay 20/15 period 30/15"` — output to `charts/todo-app/templates/frontend-deployment.yaml`
- [x] T022 [P] [US1] Generate frontend NodePort Service via kubectl-ai: prompt — `"Create NodePort Service for todo-frontend, selector app=todo-frontend, port 3000 targetPort 3000 nodePort 30080"` — output to `charts/todo-app/templates/frontend-service.yaml`
- [x] T023 [P] [US1] Generate ConfigMap template via kubectl-ai: prompt — `"Create Kubernetes ConfigMap named todo-frontend-config with key NEXT_PUBLIC_API_URL value http://todo-backend:8000"` — output to `charts/todo-app/templates/configmap.yaml`
- [x] T024 [US1] Append all 5 kubectl-ai calls to `phase-iv-audit.log` (one line per manifest, with prompt + result)

### Sub-Phase C: Helm Packaging

- [x] T025 [US1] Populate `charts/todo-app/values.yaml` from `contracts/helm-values-schema.yaml`: backend (image:todo-backend, tag:latest, replicas:2, port:8000, resources, probes), frontend (image:todo-frontend, tag:latest, replicas:2, port:3000, nodePort:30080, resources, probes), secrets.backendSecretName:todo-backend-secret, configmap.frontendConfigName:todo-frontend-config
- [x] T026 [US1] Parameterise all hardcoded values in the 5 Helm templates using `{{ .Values.* }}` expressions (image+tag, replicas, port, resources cpu/mem, probe paths and timing)
- [x] T027 [US1] Lint chart: `helm lint charts/todo-app` — MUST output `1 chart(s) linted, 0 chart(s) failed`

### Sub-Phase D: Deploy & Browser Access

- [x] T028 [US1] Install Helm release: `helm install todo-chatbot ./charts/todo-app` — verify: `helm list` shows STATUS deployed
- [x] T029 [US1] Watch pods reach Running state: `kubectl get pods -w` — all 4 pods MUST show `Running` with `1/1` readiness within 120 seconds
- [x] T030 [US1] Open frontend in browser: `minikube service todo-frontend` — verify UI loads at `http://<minikube-ip>:30080` without an error page
- [x] T031 [US1] Send a chat message from the Todo Chatbot UI — verify backend responds without CORS or DNS errors in the browser console

**Checkpoint (US1 — MVP complete)**: 4 pods Running · browser shows Todo Chatbot UI · chat receives backend response · `phase-iv-audit.log` has entries for all Gordon and kubectl-ai calls.

---

## Phase 4: US2 — Todo Data Persists Across Pod Restarts (Priority: P2)

**Goal**: Todo items created via the frontend survive backend pod restarts, proving the
Persistent Volume Claim provides durable storage beyond the pod lifecycle.

**Independent Test**: Create a todo via the UI, delete the backend pod, wait for restart,
confirm the todo is still visible in the UI.

- [x] T032 [US2] Generate PVC via kubectl-ai: prompt — `"Create PersistentVolumeClaim named todo-data-pvc, StorageClass standard, accessMode ReadWriteOnce, storage 1Gi"` — output to `charts/todo-app/templates/pvc.yaml`
- [x] T033 [US2] Add PVC volume + volumeMount to `charts/todo-app/templates/backend-deployment.yaml`: mount `todo-data-pvc` at `/app/data` inside the backend container (as a Helm-templated `{{ .Values.persistence.* }}` block)
- [x] T034 [US2] Upgrade Helm release: `helm upgrade todo-chatbot ./charts/todo-app` — verify `kubectl get pvc` shows `todo-data-pvc` with STATUS `Bound`
- [x] T035 [US2] Create a todo item via the frontend chat UI — confirm it appears in the todo list
- [x] T036 [US2] Simulate pod failure: `kubectl delete pod -l app=todo-backend --wait=false` — watch pod recreate: `kubectl get pods -w` — pod MUST return to `Running/Ready` automatically without manual intervention
- [x] T037 [US2] Verify data persistence: reload the frontend UI — confirm the todo item from T035 is still present
- [x] T038 [US2] Append PVC kubectl-ai call to `phase-iv-audit.log`

**Checkpoint (US2 complete)**: PVC `Bound` · todo item survives pod restart · `kubectl describe pvc todo-data-pvc` shows storage allocated and bound to a backend pod.

---

## Phase 5: US3 — Healthy Cluster with Resource Guardrails (Priority: P3)

**Goal**: All pods operate within defined resource limits; liveness and readiness probes
ensure only healthy pods receive traffic; Kagent validates both stability and right-sizing.

**Independent Test**: `kubectl get pods` shows all `Running` with `1/1`; `kubectl describe
pod` shows resource limits and probe definitions; Kagent Pass 1 reports no error conditions.

- [x] T039 [US3] Kagent Pass 1 — pod stability check: `kagent "Analyze the health of all pods in the default namespace. Check for CrashLoopBackOff, OOMKilled, or ImagePullBackOff conditions."` — all conditions MUST be clear
- [x] T040 [P] [US3] Verify liveness probe in backend Deployment: `kubectl describe pod -l app=todo-backend | grep -A5 Liveness` — must show `GET /health` probe with delay and period
- [x] T041 [P] [US3] Verify liveness probe in frontend Deployment: `kubectl describe pod -l app=todo-frontend | grep -A5 Liveness` — must show `GET /` probe with delay and period
- [x] T042 [P] [US3] Verify readiness gating: `kubectl describe endpoints todo-backend` — endpoints must populate only after readiness probe succeeds (empty immediately after pod start, populated within 30s)
- [x] T043 [P] [US3] Verify backend resource limits: `kubectl describe pod -l app=todo-backend | grep -A4 Limits` — cpu: 500m, memory: 512Mi MUST appear
- [x] T044 [P] [US3] Verify frontend resource limits: `kubectl describe pod -l app=todo-frontend | grep -A4 Limits` — cpu: 200m, memory: 256Mi MUST appear
- [x] T045 [US3] Wait 2 minutes for workload to stabilise under typical load (open frontend, send 2–3 chat messages)
- [x] T046 [US3] Kagent Pass 2 — resource right-sizing: `kagent "Analyze CPU and memory utilization for todo-frontend and todo-backend pods. Suggest optimized resource limits and requests based on observed usage."` — update `charts/todo-app/values.yaml` if recommendations differ from current limits
- [x] T047 [US3] Append both Kagent calls (Pass 1 + Pass 2) to `phase-iv-audit.log` with full prompt and result summary

**Checkpoint (US3 complete)**: Kagent Pass 1 clear · all resource limits visible · readiness probes gating endpoints · Kagent Pass 2 report generated and logged.

---

## Phase 6: US4 — Deploy and Manage via Helm (Priority: P4)

**Goal**: The full stack can be installed, upgraded, rolled back, and removed with single
Helm commands, proving the chart is self-contained and lifecycle-complete.

**Independent Test**: `helm install` creates all resources · `helm upgrade` applies changes
without downtime · `helm rollback` restores previous state · `helm uninstall` leaves no orphans.

- [ ] T048 [US4] Test Helm upgrade: modify `charts/todo-app/values.yaml` (set `backend.replicas: 1`), run `helm upgrade todo-chatbot ./charts/todo-app` — verify `kubectl get pods` shows 1 backend pod
- [ ] T049 [US4] Restore replicas: set `backend.replicas: 2`, run `helm upgrade todo-chatbot ./charts/todo-app` — verify both backend pods return to Running
- [ ] T050 [US4] Test Helm rollback: `helm rollback todo-chatbot 1` — verify cluster returns to prior release state via `helm history todo-chatbot`
- [ ] T051 [US4] Test full teardown: `helm uninstall todo-chatbot` — verify `kubectl get pods` returns no todo pods; `kubectl get svc | grep todo` returns empty; `kubectl get pvc` shows no Bound todo claims
- [ ] T052 [US4] Test fresh reinstall: `helm install todo-chatbot ./charts/todo-app` — verify all 4 pods return to Running within 120s and UI is accessible
- [ ] T053 [US4] Confirm `helm lint charts/todo-app` still passes: `1 chart(s) linted, 0 chart(s) failed`

**Checkpoint (US4 complete)**: Full install → upgrade → rollback → uninstall → reinstall cycle completes cleanly · `helm lint` passes throughout · no orphaned resources after uninstall.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Audit trail completeness, documentation validation, and final cluster health snapshot.

- [ ] T054 [P] Review `phase-iv-audit.log` — confirm every agent call (Gordon × 2, kubectl-ai × 6+, Kagent × 2) has a corresponding entry with ISO timestamp, agent name, prompt text, and result summary
- [ ] T055 [P] Validate `quickstart.md` end-to-end: perform full teardown then follow quickstart.md from step 0 to step 7 — confirm it produces a working deployment from scratch
- [ ] T056 [P] Run `kubectl get all -n default | grep todo` — confirm all expected resources are present: 4 pods, 2 services, 1 PVC, 1 ConfigMap, 1 Secret
- [ ] T057 Generate final Kagent cluster report: `kagent "Generate a complete health summary for the todo-chatbot deployment in the default namespace. Include pod status, resource usage, and any optimization recommendations."` — append full output to `phase-iv-audit.log`
- [ ] T058 Commit all generated artifacts to the feature branch: `Dockerfile.backend`, `Dockerfile.frontend`, `charts/todo-app/` tree (Chart.yaml, values.yaml, templates/*), `phase-iv-audit.log`

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) → Phase 4 (US2)
                                                          ↘ Phase 5 (US3)
                                                           → Phase 6 (US4) → Phase 7 (Polish)
```

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — MVP gate; must complete before US2/US3
- **US2 (Phase 4)**: Depends on US1 pods running (upgrades existing Deployment with PVC)
- **US3 (Phase 5)**: Depends on US1 pods running (Kagent needs live pods); can run after US2
- **US4 (Phase 6)**: Depends on US2 + US3 (tests lifecycle after all resources exist)
- **Polish (Phase 7)**: Depends on all user stories complete

### Within US1 — Ordered Sub-Phases

```
T011,T012 [P] → T013 → T014 → T015 → T016 → T017 → T018
                                                        ↓
                              T019,T020,T021,T022,T023 [P] → T024
                                                                ↓
                                                T025 → T026 → T027 → T028 → T029 → T030 → T031
```

### Parallel Opportunities

```bash
# Phase 1:
T002, T003, T004  (different files, independent)

# Phase 3 Sub-Phase A source review:
T011, T012  (different source directories)

# Phase 3 Sub-Phase B manifest generation:
T019, T020, T021, T022, T023  (different output files)

# Phase 5 probe/limit verification:
T040, T041, T042, T043, T044  (different kubectl describe targets)

# Phase 7 polish:
T054, T055, T056  (different verification targets)
```

---

## Implementation Strategy

### MVP First (US1 Only — Phases 1–3)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T010)
3. Complete Phase 3A: Gordon Dockerfiles (T011–T018)
4. Complete Phase 3B: kubectl-ai Manifests (T019–T024)
5. Complete Phase 3C: Helm Packaging (T025–T027)
6. Complete Phase 3D: Deploy + Browser Access (T028–T031)
7. **STOP and VALIDATE**: `minikube service todo-frontend` opens UI · chat works · 4 pods Running
8. **MVP ACHIEVED** ✅

### Incremental Delivery

| Increment | Phases | Deliverable |
|-----------|--------|-------------|
| MVP | 1–3 | Browser-accessible Todo Chatbot on Minikube |
| + Persistence | + 4 | Todo data survives pod restarts |
| + Resilience | + 5 | Resource-governed, Kagent-validated cluster |
| + Lifecycle | + 6 | Full Helm install/upgrade/rollback/uninstall |
| Complete | + 7 | Audit trail + documentation validated |

---

## Notes

- All `[P]` tasks target different files — no dependency conflicts
- `[Story]` labels map tasks to user stories for infra-orchestrator traceability
- `imagePullPolicy: Never` MUST appear in ALL Deployment manifests (Minikube local registry)
- K8s Secret and ConfigMap MUST be created imperatively before `helm install` (not templated in chart)
- Run `eval $(minikube docker-env)` at the start of every new terminal session that builds images
- All agent delegation prompts must be logged to `phase-iv-audit.log` verbatim
- Commit after each user story checkpoint (T031, T038, T047, T053) to preserve working state
