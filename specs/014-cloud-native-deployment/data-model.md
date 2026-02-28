# Deployment Topology: Phase IV Cloud-Native Deployment (014-cloud-native-deployment)

**Date**: 2026-02-24 | **Branch**: `013-todo-ai-chatbot`

> **Note**: This feature has no database schema changes. The "data model" for an
> infrastructure feature is the **cluster topology** — the Kubernetes resources, their
> relationships, and the data they carry (secrets, config maps, labels).

---

## Cluster Topology Overview

```
Minikube Cluster (default namespace)
│
├── ConfigMap: todo-frontend-config
│     └── NEXT_PUBLIC_API_URL → http://todo-backend:8000
│
├── Secret: todo-backend-secret
│     ├── DATABASE_URL
│     ├── OPENAI_API_KEY
│     └── BETTER_AUTH_SECRET
│
├── Deployment: todo-backend  (2 replicas)
│     └── Pod × 2
│           └── Container: todo-backend:latest
│                 ├── port: 8000
│                 └── env ← Secret todo-backend-secret
│
├── Service: todo-backend (ClusterIP, port 8000)
│     └── selector: app=todo-backend
│
├── Deployment: todo-frontend  (2 replicas)
│     └── Pod × 2
│           └── Container: todo-frontend:latest
│                 ├── port: 3000
│                 └── env ← ConfigMap todo-frontend-config
│
└── Service: todo-frontend (NodePort, port 3000 → NodePort 30080)
      └── selector: app=todo-frontend
```

**External Database** (Neon PostgreSQL) — NOT deployed to K8s. Accessed from backend pods
via `DATABASE_URL` in `todo-backend-secret`.

---

## Kubernetes Resources

### ConfigMap: `todo-frontend-config`

| Key | Value | Notes |
|-----|-------|-------|
| `NEXT_PUBLIC_API_URL` | `http://todo-backend:8000` | K8s DNS name of backend Service |

**Purpose**: Injects the backend URL into Next.js at runtime without hardcoding it in the image.

---

### Secret: `todo-backend-secret`

| Key | Type | Notes |
|-----|------|-------|
| `DATABASE_URL` | Opaque | `postgresql+asyncpg://...?ssl=require` — Neon connection string |
| `OPENAI_API_KEY` | Opaque | OpenAI API key for the agentic loop |
| `BETTER_AUTH_SECRET` | Opaque | JWT signing secret for Better Auth |

**Creation (imperative — keep values out of Git)**:
```bash
kubectl create secret generic todo-backend-secret \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET"
```

---

### Deployment: `todo-backend`

| Field | Value |
|-------|-------|
| `replicas` | 2 (Helm: `backend.replicas`) |
| `image` | `todo-backend:latest` |
| `imagePullPolicy` | `Never` (Minikube local registry) |
| `containerPort` | 8000 |
| `envFrom` | `secretRef: todo-backend-secret` |
| `resources.requests` | cpu: 100m, memory: 128Mi |
| `resources.limits` | cpu: 500m, memory: 512Mi |
| `livenessProbe` | `GET /health` every 30s |
| `readinessProbe` | `GET /health` — gates traffic until ready |

**Labels**: `app: todo-backend`, `version: latest`

---

### Service: `todo-backend` (ClusterIP)

| Field | Value |
|-------|-------|
| `type` | ClusterIP |
| `port` | 8000 |
| `targetPort` | 8000 |
| `selector` | `app: todo-backend` |

**Purpose**: Internal cluster DNS resolution. Frontend calls `http://todo-backend:8000`.
Not exposed externally — backend is only reachable from within the cluster.

---

### Deployment: `todo-frontend`

| Field | Value |
|-------|-------|
| `replicas` | 2 (Helm: `frontend.replicas`) |
| `image` | `todo-frontend:latest` |
| `imagePullPolicy` | `Never` (Minikube local registry) |
| `containerPort` | 3000 |
| `envFrom` | `configMapRef: todo-frontend-config` |
| `resources.requests` | cpu: 50m, memory: 64Mi |
| `resources.limits` | cpu: 200m, memory: 256Mi |
| `livenessProbe` | `GET /` every 30s |
| `readinessProbe` | `GET /` — gates traffic until ready |

**Labels**: `app: todo-frontend`, `version: latest`

---

### Service: `todo-frontend` (NodePort)

| Field | Value |
|-------|-------|
| `type` | NodePort |
| `port` | 3000 |
| `targetPort` | 3000 |
| `nodePort` | 30080 (Helm: `frontend.nodePort`) |
| `selector` | `app: todo-frontend` |

**Access**: `minikube service todo-frontend` opens the UI in a browser.
URL: `http://<minikube-ip>:30080`

---

## Helm `values.yaml` Schema

```yaml
backend:
  image: todo-backend
  tag: latest
  replicas: 2
  port: 8000
  resources:
    requests:
      cpu: "100m"
      memory: "128Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"

frontend:
  image: todo-frontend
  tag: latest
  replicas: 2
  port: 3000
  nodePort: 30080
  resources:
    requests:
      cpu: "50m"
      memory: "64Mi"
    limits:
      cpu: "200m"
      memory: "256Mi"

secrets:
  backendSecretName: todo-backend-secret

configmap:
  frontendConfigName: todo-frontend-config
```

---

## Audit Log Format

`phase-iv-audit.log` — committed with deployment artifacts.

```
[ISO-timestamp] [AGENT]   prompt="<one-line prompt>"   result="<one-line summary>"
```

**Example entries**:
```
[2026-02-24T10:00:00Z] [GORDON]      prompt="Create multi-stage Dockerfile for FastAPI..."   result="Dockerfile generated, 2-stage, python:3.11-slim, non-root user"
[2026-02-24T10:05:00Z] [KUBECTL-AI]  prompt="Create Deployment for todo-backend..."          result="backend-deployment.yaml generated, 2 replicas, envFrom secret"
[2026-02-24T10:10:00Z] [KAGENT]      prompt="Analyze health of all pods..."                  result="All 4 pods Running, no CrashLoop detected"
```
