# Research: Phase IV Cloud-Native Deployment (014-cloud-native-deployment)

**Date**: 2026-02-24 | **Branch**: `013-todo-ai-chatbot`

---

## 1. Multi-Stage Docker for FastAPI (Gordon — Python Backend)

**Decision**: Use a two-stage Docker build: `builder` stage installs dependencies; `runtime`
stage copies only the installed packages and source. Base image: `python:3.11-slim`.

**Rationale**:
- Multi-stage builds exclude build tools (gcc, pip cache) from the final image, reducing
  attack surface and image size.
- `python:3.11-slim` provides a minimal Debian base with Python pre-installed — avoids Alpine
  issues with musl libc and binary wheels.
- `--no-cache-dir` in pip install prevents pip caching layer bloat.
- Non-root `appuser` is created in the runtime stage for least-privilege execution.

**Gordon prompt pattern**:
```
docker ai "Create a multi-stage Dockerfile for a FastAPI Python 3.11 application.
Stage 1: install all dependencies from requirements.txt.
Stage 2: copy only the installed packages and source. Use python:3.11-slim as base.
Run as non-root user. Expose port 8000. CMD: uvicorn backend.main:app --host 0.0.0.0 --port 8000"
```

**Alternatives considered**:
- `python:3.11-alpine` — musl libc incompatible with asyncpg binary wheels; rejected.
- Single-stage — includes build tools in production image; rejected for security reasons.

---

## 2. Multi-Stage Docker for Next.js (Gordon — Frontend)

**Decision**: Three-stage build: `deps` (install node_modules), `builder` (next build),
`runner` (copy `.next/standalone` output only). Base: `node:18-alpine`.

**Rationale**:
- Next.js standalone output (`output: 'standalone'` in `next.config.js`) bundles only the
  files needed to run the server — typically 80% smaller than a full node_modules copy.
- `node:18-alpine` is the standard production Next.js base image recommended by Vercel.
- The three-stage pattern is the official Next.js Docker best practice.

**Gordon prompt pattern**:
```
docker ai "Create a multi-stage Dockerfile for a Next.js 14 application.
Stage 1 (deps): npm ci from package.json.
Stage 2 (builder): copy deps, run npm run build with NEXT_TELEMETRY_DISABLED=1.
Stage 3 (runner): copy .next/standalone and .next/static from builder. Use node:18-alpine.
Run as non-root user nextjs:nodejs. Expose port 3000. CMD: node server.js"
```

**Alternatives considered**:
- Single-stage with full node_modules — 400MB+ image vs. ~100MB standalone; rejected.
- Nginx static serving — requires SSR to be disabled; rejected (auth pages require SSR).

---

## 3. kubectl-ai Manifest Generation

**Decision**: Use `kubectl-ai` with descriptive natural-language prompts to generate
Deployment + Service YAML for each service. Save output to `charts/todo-app/templates/`.

**Rationale**:
- kubectl-ai translates declarative English requirements into valid K8s YAML, handling
  label selectors, resource specs, and port mappings automatically.
- Generated manifests should be reviewed for correctness before packaging into Helm.
- Resource requests/limits are included in the prompt to ensure Minikube doesn't OOM.

**kubectl-ai prompt patterns**:
```
# Backend
kubectl-ai "Create a Kubernetes Deployment for todo-backend:
  image: todo-backend:latest, imagePullPolicy: Never,
  replicas: 2, port: 8000,
  env from Secret todo-backend-secret (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET),
  resources: requests cpu=100m memory=128Mi limits cpu=500m memory=512Mi"

# Frontend
kubectl-ai "Create a Kubernetes Deployment and NodePort Service for todo-frontend:
  image: todo-frontend:latest, imagePullPolicy: Never,
  replicas: 2, containerPort: 3000,
  env: NEXT_PUBLIC_API_URL from ConfigMap todo-frontend-config,
  resources: requests cpu=50m memory=64Mi limits cpu=200m memory=256Mi,
  NodePort service on port 30080"
```

**Alternatives considered**:
- Manual YAML authoring — violates Constitution Principle X; rejected.
- Kompose (docker-compose → K8s) — generates verbose, unoptimised YAML; rejected in favour
  of targeted kubectl-ai prompts.

---

## 4. Secrets Management in Minikube

**Decision**: Use Kubernetes Secrets (base64-encoded) for sensitive env vars. Secrets are
created imperatively via `kubectl create secret generic` before Helm install. They are
referenced in Deployment env specs via `secretKeyRef`.

**Rationale**:
- Kubernetes Secrets prevent env vars from appearing in plain-text in Helm values or logs.
- Imperative creation (`kubectl create secret`) keeps secret values out of Git history.
- `imagePullPolicy: Never` tells K8s to use the locally built image (Minikube registry),
  avoiding a pull from a remote registry that would require pull secrets.

**Secret structure**:
```
todo-backend-secret:
  DATABASE_URL     (postgresql+asyncpg://...?ssl=require)
  OPENAI_API_KEY   (sk-...)
  BETTER_AUTH_SECRET

todo-frontend-configmap:
  NEXT_PUBLIC_API_URL  (http://<minikube-ip>:30080 or relative /api)
```

**Alternatives considered**:
- Helm values.yaml with secrets — values are plaintext in chart; rejected.
- Sealed Secrets / Vault — overkill for local Minikube; deferred to production phase.

---

## 5. Helm Chart Structure for Minikube

**Decision**: Single Helm chart at `charts/todo-app/` with templates for both services.
`values.yaml` parameterises replica counts, image tags, and NodePort number.

**Rationale**:
- A single chart simplifies `helm install` to one command.
- `values.yaml` enables per-environment overrides (e.g., `--set backend.replicas=1` for CI).
- Helm manages the full lifecycle: install, upgrade, rollback, uninstall.

**Chart layout**:
```
charts/todo-app/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    └── configmap.yaml
```

**Alternatives considered**:
- Separate charts per service — two `helm install` commands; harder to coordinate; rejected.
- Kustomize — no templating; harder to parameterise replica counts; rejected for this scope.

---

## 6. Kagent Health Check Patterns

**Decision**: Run two Kagent passes — (1) pod stability check after deploy, (2) resource
optimisation after workload stabilises (~2 min).

**Kagent prompt patterns**:
```
# Pass 1 — post-deploy stability
kagent "Analyze the health of all pods in the default namespace.
        Check for CrashLoopBackOff, OOMKilled, or ImagePullBackOff conditions."

# Pass 2 — resource right-sizing
kagent "Analyze CPU and memory utilization for todo-frontend and todo-backend pods.
        Suggest resource limits and requests based on observed usage."
```

**Rationale**:
- Kagent's cluster-aware analysis catches misconfigured resource limits and missing secrets
  faster than manual `kubectl describe pod` scanning.
- A two-pass approach separates liveness concerns from performance optimisation concerns.

---

## 7. imagePullPolicy: Never

**Decision**: All Deployment manifests MUST set `imagePullPolicy: Never`.

**Rationale**:
- Minikube's Docker daemon (activated via `eval $(minikube docker-env)`) is a separate Docker
  context from the host. Images built inside this context are only available locally.
- `imagePullPolicy: Never` tells Kubernetes not to pull from a remote registry, using the
  locally available image directly.
- Forgetting this is the #1 cause of `ErrImagePull` in local Minikube setups.

---

## 8. Frontend → Backend Communication in Minikube

**Decision**: Frontend container calls backend via `http://todo-backend:8000` (K8s DNS
internal name). `NEXT_PUBLIC_API_URL` is set to the internal backend Service ClusterIP DNS
name for SSR calls; browser calls are proxied via Next.js API routes.

**Rationale**:
- Kubernetes DNS resolves `todo-backend` to the backend ClusterIP Service automatically
  within the cluster — no IP addresses needed.
- Browser JS cannot reach a ClusterIP directly; Next.js API routes act as a server-side
  proxy, forwarding chat requests to the backend service.
- This pattern avoids CORS issues and keeps the backend unexposed externally.

**Alternatives considered**:
- Expose backend via NodePort and call from browser directly — exposes backend publicly;
  CORS configuration required; rejected in favour of proxy pattern.
