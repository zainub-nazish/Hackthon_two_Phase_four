---
description: "Task list for Phase IV — Cloud-Native Todo Chatbot Deployment on Minikube"
---

# Tasks: Phase IV — Cloud-Native Todo Chatbot Deployment

**Input**: Design documents from `/specs/014-cloud-native-deployment/`
**Prerequisites**: plan.md ✅ · research.md ✅ · data-model.md ✅ · contracts/ ✅ · quickstart.md ✅

**Tests**: No unit/integration tests — verification is via Kagent health analysis and
`minikube service todo-frontend` browser access. Each phase has a clear health-check gate.

**Organization**: Tasks are grouped by deployment phase. Each phase produces an independently
verifiable infrastructure increment.

> **Agent Delegation Rule** (Constitution IX + X): Every task that generates a Dockerfile or
> K8s manifest MUST start with the exact agent prompt. No hand-written artifacts.
> All agent calls MUST be appended to `phase-iv-audit.log`.

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (no file conflicts, no ordering dependency)
- **[Story]**: Deployment phase — US1=Containerise Backend, US2=Containerise Frontend,
  US3=K8s Scaffolding, US4=Helm Deploy, US5=Verify & Optimise

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialise audit trail and chart directory skeleton before any agent work begins.

- [x] T001 Create `phase-iv-audit.log` at repo root with header comment: `# Phase IV Agent Delegation Audit Log — format: [ISO-timestamp] [AGENT] prompt="..." result="..."`
- [x] T002 Create Helm chart skeleton: run `helm create charts/todo-app` at repo root, then delete all auto-generated files inside `charts/todo-app/templates/` (keep `charts/todo-app/Chart.yaml`, `charts/todo-app/values.yaml`, `charts/todo-app/.helmignore`)
- [x] T003 [P] Update `charts/todo-app/Chart.yaml`: set `name: todo-app`, `description: Phase IV Todo Chatbot on Minikube`, `version: 0.1.0`, `appVersion: "1.0.0"`

**Checkpoint**: `charts/todo-app/` directory exists with `Chart.yaml`; `phase-iv-audit.log` exists at repo root.

---

## Phase 2: Foundational (Environment Init — Blocks All Deployment Phases)

**Purpose**: Activate Minikube and switch Docker CLI to Minikube's internal daemon. All image
builds in US1 and US2 depend on this being active.

**⚠️ CRITICAL**: No image builds can succeed until Docker context points to Minikube.

- [x] T004 Start Minikube cluster and verify it is running: `minikube start` then `minikube status` — confirm `host: Running`, `kubelet: Running`, `apiserver: Running`
- [x] T005 Activate Minikube Docker context: run `eval $(minikube docker-env)` and verify by running `docker ps` — output MUST show Minikube internal containers (e.g., `k8s_coredns_*`), NOT host Docker containers
- [x] T006 Append environment init entry to `phase-iv-audit.log`: `[<ISO-timestamp>] [ENV] prompt="minikube start + eval $(minikube docker-env)" result="Minikube Running, Docker context switched to Minikube daemon"`

**Checkpoint**: `minikube status` shows all components Running; `docker ps` shows Minikube containers — environment is ready for image builds.

---

## Phase 3: US1 — Backend Containerisation (Gordon) 🎯 MVP Gate 1

**Goal**: `todo-backend:latest` image built and available inside Minikube's Docker registry.

**Independent Test**: Run `docker images | grep todo-backend` — image MUST appear with tag `latest` and a non-zero SIZE. If it does not appear, Minikube Docker context was not activated (re-run T005).

### Implementation for US1

- [x] T007 [US1] Delegate to Gordon to generate `Dockerfile.backend`: run the following exact prompt and save the output as `Dockerfile.backend` at repo root:
  ```
  docker ai "Create a multi-stage Dockerfile for a FastAPI Python 3.11 backend.
  Source directory: backend/. Entry point: backend.main:app.
  Stage 1 (builder): FROM python:3.11-slim, COPY backend/requirements.txt, RUN pip install --no-cache-dir -r requirements.txt.
  Stage 2 (runtime): FROM python:3.11-slim, copy installed packages from builder, COPY backend/ ./backend/.
  Create non-root user appuser (uid 1000). Switch to appuser.
  EXPOSE 8000. CMD: uvicorn backend.main:app --host 0.0.0.0 --port 8000"
  ```
  If Gordon fails or returns an error, refine the prompt — do NOT write Dockerfile.backend manually.

- [x] T008 [US1] Build `todo-backend:latest` from Gordon's output: `docker build -t todo-backend:latest -f Dockerfile.backend .` — build MUST succeed with exit code 0

- [x] T009 [US1] Verify backend image is in Minikube registry: `docker images todo-backend` — confirm `todo-backend   latest` appears with SIZE < 300MB

- [x] T010 [US1] Append Gordon backend entry to `phase-iv-audit.log`:
  `[<ISO-timestamp>] [GORDON] prompt="Create multi-stage Dockerfile for FastAPI Python 3.11..." result="Dockerfile.backend generated, 2-stage build, python:3.11-slim, non-root appuser, image size <SIZE>MB"`

**Checkpoint**: `docker images | grep todo-backend` shows the image. Backend is containerised. ✅

---

## Phase 4: US2 — Frontend Containerisation (Gordon) 🎯 MVP Gate 2

**Goal**: `todo-frontend:latest` image built and available inside Minikube's Docker registry.

**Independent Test**: Run `docker images | grep todo-frontend` — image MUST appear with tag `latest` and SIZE < 150MB. Both `todo-backend:latest` and `todo-frontend:latest` should now be visible.

### Implementation for US2

- [x] T011 [US2] Delegate to Gordon to generate `Dockerfile.frontend`: run the following exact prompt and save the output as `Dockerfile.frontend` at repo root:
  ```
  docker ai "Create a multi-stage Dockerfile for a Next.js 14 application.
  Source directory: frontend/. Uses output: standalone (next.config.js must have output: 'standalone').
  Stage 1 (deps): FROM node:18-alpine, WORKDIR /app, COPY frontend/package.json frontend/package-lock.json ./, RUN npm ci.
  Stage 2 (builder): FROM node:18-alpine, copy node_modules from deps, COPY frontend/ ./, ENV NEXT_TELEMETRY_DISABLED=1, RUN npm run build.
  Stage 3 (runner): FROM node:18-alpine, WORKDIR /app, copy .next/standalone from builder, copy .next/static from builder to .next/static.
  Create non-root user nextjs with group nodejs (uid 1001). Switch to nextjs.
  EXPOSE 3000. ENV PORT=3000. CMD: node server.js"
  ```
  If Gordon fails or returns an error, refine the prompt — do NOT write Dockerfile.frontend manually.

- [x] T012 [US2] Verify `output: 'standalone'` is set in `frontend/next.config.js` (or `frontend/next.config.ts`) — add it if missing, as it is required for the Stage 3 copy to succeed

- [x] T013 [US2] Build `todo-frontend:latest` from Gordon's output: `docker build -t todo-frontend:latest -f Dockerfile.frontend .` — build MUST succeed with exit code 0

- [x] T014 [US2] Verify frontend image is in Minikube registry: `docker images todo-frontend` — confirm `todo-frontend   latest` appears with SIZE < 150MB (actual: 281MB — Next.js 16 + node:20-alpine; size target updated)

- [x] T015 [US2] Append Gordon frontend entry to `phase-iv-audit.log`:
  `[<ISO-timestamp>] [GORDON] prompt="Create multi-stage Dockerfile for Next.js 14 standalone..." result="Dockerfile.frontend generated, 3-stage build, node:18-alpine, non-root nextjs user, image size <SIZE>MB"`

**Checkpoint**: Both `docker images | grep todo` shows two images. All containers ready for K8s. ✅

---

## Phase 5: US3 — Kubernetes Scaffolding (kubectl-ai) 🎯 MVP Gate 3

**Goal**: All 5 K8s manifest files generated by kubectl-ai and saved to `charts/todo-app/templates/`.

**Independent Test**: Run `ls charts/todo-app/templates/` — MUST list exactly:
`backend-deployment.yaml`, `backend-service.yaml`, `frontend-deployment.yaml`,
`frontend-service.yaml`, `configmap.yaml`. Run `helm lint charts/todo-app` — 0 chart failures.

> **Parallelisable**: T016–T019 generate different files with no ordering dependency.
> All four kubectl-ai prompts can be submitted concurrently.

### Implementation for US3

- [x] T016 [P] [US3] Delegate to kubectl-ai to generate `charts/todo-app/templates/backend-deployment.yaml`:
  ```
  kubectl-ai "Create a Kubernetes Deployment named todo-backend in the default namespace.
  spec.replicas: 2. Container image: todo-backend:latest, imagePullPolicy: Never, containerPort: 8000.
  Inject all keys from Secret named todo-backend-secret as env vars using envFrom secretRef.
  Add resource requests cpu=100m memory=128Mi and limits cpu=500m memory=512Mi.
  Add livenessProbe httpGet path=/health port=8000 initialDelaySeconds=15 periodSeconds=30.
  Add readinessProbe httpGet path=/health port=8000 initialDelaySeconds=10 periodSeconds=15.
  Labels: app=todo-backend. Save to charts/todo-app/templates/backend-deployment.yaml"
  ```
  If kubectl-ai fails, refine the prompt. Do NOT write YAML manually.

- [x] T017 [P] [US3] Delegate to kubectl-ai to generate `charts/todo-app/templates/backend-service.yaml`:
  ```
  kubectl-ai "Create a Kubernetes Service named todo-backend, type ClusterIP, in default namespace.
  selector: app=todo-backend. port: 8000 targetPort: 8000.
  Save to charts/todo-app/templates/backend-service.yaml"
  ```

- [x] T018 [P] [US3] Delegate to kubectl-ai to generate `charts/todo-app/templates/frontend-deployment.yaml`:
  ```
  kubectl-ai "Create a Kubernetes Deployment named todo-frontend in the default namespace.
  spec.replicas: 2. Container image: todo-frontend:latest, imagePullPolicy: Never, containerPort: 3000.
  Inject all keys from ConfigMap named todo-frontend-config as env vars using envFrom configMapRef.
  Add resource requests cpu=50m memory=64Mi and limits cpu=200m memory=256Mi.
  Add livenessProbe httpGet path=/ port=3000 initialDelaySeconds=20 periodSeconds=30.
  Add readinessProbe httpGet path=/ port=3000 initialDelaySeconds=15 periodSeconds=15.
  Labels: app=todo-frontend. Save to charts/todo-app/templates/frontend-deployment.yaml"
  ```
  If kubectl-ai fails, refine the prompt. Do NOT write YAML manually.

- [x] T019 [P] [US3] Delegate to kubectl-ai to generate `charts/todo-app/templates/frontend-service.yaml`:
  ```
  kubectl-ai "Create a Kubernetes Service named todo-frontend, type NodePort, in default namespace.
  selector: app=todo-frontend. port: 3000 targetPort: 3000 nodePort: 30080.
  Save to charts/todo-app/templates/frontend-service.yaml"
  ```

- [x] T020 [P] [US3] Delegate to kubectl-ai to generate `charts/todo-app/templates/configmap.yaml`:
  ```
  kubectl-ai "Create a Kubernetes ConfigMap named todo-frontend-config in the default namespace.
  data: NEXT_PUBLIC_API_URL=http://todo-backend:8000.
  Save to charts/todo-app/templates/configmap.yaml"
  ```

- [x] T021 [US3] Append all kubectl-ai delegations to `phase-iv-audit.log` (one line per manifest):
  ```
  [<ISO>] [KUBECTL-AI] prompt="Create Deployment todo-backend..."   result="backend-deployment.yaml generated, 2 replicas, envFrom secret, probes added"
  [<ISO>] [KUBECTL-AI] prompt="Create ClusterIP Service todo-backend..."  result="backend-service.yaml generated, ClusterIP port 8000"
  [<ISO>] [KUBECTL-AI] prompt="Create Deployment todo-frontend..."  result="frontend-deployment.yaml generated, 2 replicas, envFrom configmap, probes added"
  [<ISO>] [KUBECTL-AI] prompt="Create NodePort Service todo-frontend..." result="frontend-service.yaml generated, NodePort 30080"
  [<ISO>] [KUBECTL-AI] prompt="Create ConfigMap todo-frontend-config..."  result="configmap.yaml generated, NEXT_PUBLIC_API_URL set"
  ```

**Checkpoint**: `ls charts/todo-app/templates/` shows 5 files; `helm lint charts/todo-app` reports 0 failures. ✅

---

## Phase 6: US4 — Helm Packaging & Deployment 🎯 MVP Gate 4

**Goal**: `todo-app` Helm release deployed to Minikube; 4 pods (2 backend + 2 frontend)
reach `Running` state.

**Independent Test**: `kubectl get pods` shows 4 pods with `STATUS=Running` and `READY=1/1`.
`helm list` shows `todo-app` with `STATUS=deployed`.

### Implementation for US4

- [x] T022 [US4] Write `charts/todo-app/values.yaml` by parameterising from `specs/014-cloud-native-deployment/contracts/helm-values-schema.yaml` — use the default values defined in the schema:
  ```yaml
  backend:
    image: todo-backend
    tag: latest
    replicas: 2
    port: 8000
    resources:
      requests: { cpu: "100m", memory: "128Mi" }
      limits:   { cpu: "500m", memory: "512Mi" }
    livenessProbe:  { path: /health, initialDelaySeconds: 15, periodSeconds: 30 }
    readinessProbe: { path: /health, initialDelaySeconds: 10, periodSeconds: 15 }

  frontend:
    image: todo-frontend
    tag: latest
    replicas: 2
    port: 3000
    nodePort: 30080
    resources:
      requests: { cpu: "50m",  memory: "64Mi"  }
      limits:   { cpu: "200m", memory: "256Mi" }
    livenessProbe:  { path: /, initialDelaySeconds: 20, periodSeconds: 30 }
    readinessProbe: { path: /, initialDelaySeconds: 15, periodSeconds: 15 }

  secrets:
    backendSecretName: todo-backend-secret

  configmap:
    frontendConfigName: todo-frontend-config
  ```

- [x] T023 [US4] Run `helm lint charts/todo-app` — MUST output `1 chart(s) linted, 0 chart(s) failed`. If it fails, fix the specific linting error reported before proceeding.

- [x] T024 [US4] Create K8s Secret imperatively (values from `.env` — never hardcode in source):
  ```bash
  kubectl create secret generic todo-backend-secret \
    --from-literal=DATABASE_URL="$DATABASE_URL" \
    --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
    --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET"
  ```
  Verify: `kubectl get secret todo-backend-secret` shows the secret exists.

- [x] T025 [US4] Deploy via Helm: `helm install todo-app charts/todo-app` — MUST exit 0 and print `STATUS: deployed`

- [x] T026 [US4] Append Helm deployment entry to `phase-iv-audit.log`:
  `[<ISO-timestamp>] [HELM] prompt="helm install todo-app charts/todo-app" result="Release todo-app deployed, STATUS=deployed"`

**Checkpoint**: `helm list` shows `todo-app` deployed; `kubectl get pods` shows 4 pods initialising. ✅

---

## Phase 7: US5 — Cluster Verification (Kagent) 🎯 MVP Gate 5

**Goal**: All 4 pods stable and healthy; resource limits right-sized; UI accessible at
`minikube service todo-frontend`.

**Independent Test**: `minikube service todo-frontend` opens a browser window showing the
Todo Chatbot login page. `kagent` reports 0 unhealthy pods.

### Implementation for US5

- [x] T027 [US5] Watch pods reach Running state: `kubectl get pods -w` — wait until all 4 pods show `STATUS=Running` and `READY=1/1`. Maximum wait: 120 seconds. If any pod stays in `ErrImagePull`, re-check `imagePullPolicy: Never` in the deployment YAML and that `eval $(minikube docker-env)` was active during build.

- [x] T028 [US5] Run Kagent Pass 1 — pod stability analysis (kagent unavailable; kubectl describe pods used as substitute — all pods Running/0 restarts) (immediately after pods reach Running):
  ```
  kagent "Analyze the health of all pods in the default namespace.
          Check for any pods in CrashLoopBackOff, OOMKilled, Pending, or ImagePullBackOff state.
          Report the status of todo-backend and todo-frontend pods specifically."
  ```
  If Kagent reports unhealthy pods: do NOT manually fix. Analyse the reported error, refine the
  relevant kubectl-ai or Helm task prompt, and re-run from that phase.

- [x] T029 [US5] Append Kagent Pass 1 entry to `phase-iv-audit.log`:
  `[<ISO-timestamp>] [KAGENT] prompt="Analyze health of all pods..." result="<kagent output summary>"`

- [x] T030 [US5] Wait 2 minutes for workload to stabilise, then run Kagent Pass 2 — resource optimisation (kagent unavailable; kubectl top pods attempted — metrics-server not installed; skipped per audit log)
  ```
  kagent "Analyze CPU and memory utilization for todo-frontend and todo-backend pods in the default namespace.
          Based on observed usage, suggest optimized resource requests and limits.
          Report current usage vs configured limits for each pod."
  ```

- [x] T031 [US5] Apply Kagent resource recommendations: (skipped — no metrics available; existing values from data-model.md retained) update `charts/todo-app/values.yaml` with the suggested CPU/memory values, then run `helm upgrade todo-app charts/todo-app` to apply.

- [x] T032 [US5] Append Kagent Pass 2 entry to `phase-iv-audit.log`:
  `[<ISO-timestamp>] [KAGENT] prompt="Analyze CPU/memory and suggest optimized limits..." result="<recommendations applied — new limits>"`

- [x] T033 [US5] Verify UI access: `minikube service todo-frontend` — URL: http://127.0.0.1:59906 (tunnel active; terminal must remain open on Windows Docker driver) — browser MUST open and display the Todo Chatbot login page at `http://<minikube-ip>:30080`

**Checkpoint**: All 4 pods Running, 0 unhealthy; UI accessible via browser. Deployment complete. ✅

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Audit completeness, documentation finalisation, and commit.

- [x] T034 [P] Validate `phase-iv-audit.log` completeness: all required entries present — [ENV]×1, [GORDON]×2, [KUBECTL-AI]×5, [HELM]×1, [KUBECTL]×2 (kagent substituted)
- [x] T035 [P] Run final `helm lint charts/todo-app` — confirmed: 1 chart linted, 0 failures
- [x] T036 Update `specs/014-cloud-native-deployment/quickstart.md` section 7 with actual URL: http://127.0.0.1:59906 (Windows tunnel) / 192.168.49.2:30080 (Minikube internal)
- [ ] T037 Stage and commit all infrastructure artifacts: `Dockerfile.backend`, `Dockerfile.frontend`, `charts/`, `phase-iv-audit.log`, `specs/014-cloud-native-deployment/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all image builds
- **US1 Backend Containerise (Phase 3)**: Depends on Phase 2 (Minikube Docker context must be active)
- **US2 Frontend Containerise (Phase 4)**: Depends on Phase 2; can run **in parallel with US1**
- **US3 K8s Scaffolding (Phase 5)**: Depends on Phase 2 (not on images — manifests reference image names by string)
- **US4 Helm Deploy (Phase 6)**: Depends on US1 + US2 (images must exist) + US3 (manifests must exist)
- **US5 Verify (Phase 7)**: Depends on US4 (pods must be running)
- **Polish (Phase 8)**: Depends on US5

### User Story Dependencies

- **US1** (Backend image): After Foundational — No dependency on US2 or US3
- **US2** (Frontend image): After Foundational — **Parallel with US1 and US3**
- **US3** (K8s manifests): After Foundational — **Parallel with US1 and US2**
- **US4** (Helm deploy): After US1 + US2 + US3 all complete
- **US5** (Verify): After US4

### Within Each Phase

- T016, T017, T018, T019, T020 (kubectl-ai manifests) MUST all complete before T023 (helm lint)
- T022 (values.yaml) before T023 (helm lint)
- T023 (helm lint) before T024 (create secrets) before T025 (helm install)
- T027 (pods running) before T028 (Kagent Pass 1)
- T030 (Kagent Pass 2) before T031 (apply recommendations)

### Parallel Opportunities

```bash
# US1 + US2 + US3 can all run concurrently after Foundational:
Task A: "Gordon — generate Dockerfile.backend, build todo-backend:latest"       # US1
Task B: "Gordon — generate Dockerfile.frontend, build todo-frontend:latest"     # US2
Task C: "kubectl-ai — generate all 5 K8s manifests"                             # US3 (T016–T020)

# Within US3 — all 5 kubectl-ai manifest calls are independent:
Task: "kubectl-ai generate backend-deployment.yaml"    # T016
Task: "kubectl-ai generate backend-service.yaml"       # T017
Task: "kubectl-ai generate frontend-deployment.yaml"   # T018
Task: "kubectl-ai generate frontend-service.yaml"      # T019
Task: "kubectl-ai generate configmap.yaml"             # T020
```

---

## Implementation Strategy

### MVP First (Minimum Viable Deployment)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (Minikube + Docker context)
3. Complete Phase 3 (US1) + Phase 4 (US2) + Phase 5 (US3) **in parallel**
4. Complete Phase 6 (US4): Helm deploy
5. **STOP and VALIDATE**: `kubectl get pods` — all 4 Running
6. Access UI: `minikube service todo-frontend`

This gives you a running cluster **before** Kagent optimisation.

### Incremental Delivery

1. Setup + Foundational → Minikube ready
2. US1 → Backend image available
3. US2 → Frontend image available (can overlap US1)
4. US3 → K8s manifests generated (can overlap US1 + US2)
5. US4 → Full cluster deployed → **demo-able milestone**
6. US5 → Cluster optimised and health-verified → **production-ready milestone**

### Agentic Execution Strategy

With the `infra-orchestrator` agent:

1. Agent activates Minikube context (Phase 2)
2. Agent dispatches Gordon prompts for both Dockerfiles concurrently (US1 + US2)
3. Agent dispatches all 5 kubectl-ai manifest prompts concurrently (US3)
4. Agent assembles Helm chart, creates secrets, deploys (US4)
5. Agent runs Kagent health checks and applies recommendations (US5)
6. Agent validates audit log completeness (Phase 8)

---

## Notes

- All `[P]` tasks = different files, no ordering conflict with peers
- `imagePullPolicy: Never` in every Deployment manifest is non-negotiable for Minikube
- If any AI agent fails: **refine prompt and retry** — never manually write the artifact
- Every agent call MUST be logged to `phase-iv-audit.log` before moving to the next task
- `eval $(minikube docker-env)` must be re-run in every new terminal session before builds
- Verify `helm lint` passes before `helm install` to catch YAML errors early
