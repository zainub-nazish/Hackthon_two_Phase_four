# Quickstart: Phase IV Cloud-Native Deployment (014-cloud-native-deployment)

**Date**: 2026-02-24 | **Branch**: `013-todo-ai-chatbot`

> **Prerequisites**: Minikube installed, Docker Desktop running, `kubectl`, `helm`, `kubectl-ai`,
> `docker ai` (Gordon), and `kagent` all available in PATH.

---

## 0. Environment Setup

```bash
# Start Minikube (if not already running)
minikube start

# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify — you should see Minikube containers, not host containers
docker ps
```

---

## 1. Build Images (Gordon — docker ai)

Build both images **inside the Minikube Docker context** so they are available to the cluster.

```bash
# Backend
cd /path/to/phase_four

# Gordon generates the Dockerfile — do NOT write it manually
docker ai "Create a multi-stage Dockerfile for a FastAPI Python 3.11 application.
Stage 1: install dependencies from backend/requirements.txt.
Stage 2: copy source from backend/. Use python:3.11-slim. Non-root user appuser.
Expose port 8000. CMD: uvicorn backend.main:app --host 0.0.0.0 --port 8000"

# Build using Gordon's generated Dockerfile
docker build -t todo-backend:latest -f Dockerfile.backend .

# Frontend
docker ai "Create a multi-stage Dockerfile for a Next.js 14 application in the frontend/ directory.
Stage 1 (deps): npm ci. Stage 2 (builder): npm run build, NEXT_TELEMETRY_DISABLED=1.
Stage 3 (runner): copy .next/standalone. Use node:18-alpine. Non-root user nextjs.
Expose port 3000. CMD: node server.js"

docker build -t todo-frontend:latest -f Dockerfile.frontend ./frontend

# Verify images are in Minikube's registry
docker images | grep todo
```

---

## 2. Create Secrets and ConfigMap

```bash
# Create backend Secret (values from your .env file)
kubectl create secret generic todo-backend-secret \
  --from-literal=DATABASE_URL="postgresql+asyncpg://user:pass@host/db?ssl=require" \
  --from-literal=OPENAI_API_KEY="sk-..." \
  --from-literal=BETTER_AUTH_SECRET="your-secret-here"

# Create frontend ConfigMap
kubectl create configmap todo-frontend-config \
  --from-literal=NEXT_PUBLIC_API_URL="http://todo-backend:8000"

# Verify
kubectl get secret todo-backend-secret
kubectl get configmap todo-frontend-config
```

---

## 3. Generate Kubernetes Manifests (kubectl-ai)

```bash
# Backend Deployment + ClusterIP Service
kubectl-ai "Create a Kubernetes Deployment for todo-backend.
  image: todo-backend:latest, imagePullPolicy: Never, replicas: 2, port: 8000.
  Inject all keys from Secret todo-backend-secret as environment variables.
  Resources: requests cpu=100m memory=128Mi, limits cpu=500m memory=512Mi.
  Add liveness and readiness probes on GET /health.
  Output to charts/todo-app/templates/backend-deployment.yaml"

kubectl-ai "Create a ClusterIP Service for todo-backend.
  Selector app=todo-backend, port 8000 → targetPort 8000.
  Output to charts/todo-app/templates/backend-service.yaml"

# Frontend Deployment + NodePort Service
kubectl-ai "Create a Kubernetes Deployment for todo-frontend.
  image: todo-frontend:latest, imagePullPolicy: Never, replicas: 2, port: 3000.
  Inject all keys from ConfigMap todo-frontend-config as environment variables.
  Resources: requests cpu=50m memory=64Mi, limits cpu=200m memory=256Mi.
  Add liveness and readiness probes on GET /.
  Output to charts/todo-app/templates/frontend-deployment.yaml"

kubectl-ai "Create a NodePort Service for todo-frontend.
  Selector app=todo-frontend, port 3000 → targetPort 3000 → nodePort 30080.
  Output to charts/todo-app/templates/frontend-service.yaml"
```

---

## 4. Package into Helm Chart

```bash
# Initialise chart structure (if charts/todo-app/ does not exist)
helm create charts/todo-app
# Remove auto-generated templates — replace with kubectl-ai output
rm -rf charts/todo-app/templates/*

# Copy kubectl-ai output (already saved to charts/todo-app/templates/ above)

# Edit values.yaml with the parameterised values from data-model.md
# (Claude parameterises this — see tasks.md T011)

# Lint the chart
helm lint charts/todo-app

# Expected output: 1 chart(s) linted, 0 chart(s) failed
```

---

## 5. Deploy to Minikube

```bash
# Install (first time)
helm install todo-app charts/todo-app

# Or upgrade (subsequent runs)
helm upgrade todo-app charts/todo-app

# Watch pods come up
kubectl get pods -w

# Expected: all 4 pods (2 backend + 2 frontend) reach Running/Ready 1/1
```

---

## 6. Verify with Kagent

```bash
# Pass 1 — Pod stability (run immediately after deploy)
kagent "Analyze the health of all pods in the default namespace.
        Check for CrashLoopBackOff, OOMKilled, or ImagePullBackOff conditions."

# Wait ~2 minutes for workload to stabilise, then:

# Pass 2 — Resource optimisation
kagent "Analyze CPU and memory utilization for todo-frontend and todo-backend pods.
        Suggest resource limits and requests based on observed usage."
```

---

## 7. Access the UI

```bash
# Open the frontend in your browser via Minikube tunnel
minikube service todo-frontend

# Or get the URL manually
minikube service todo-frontend --url
# → http://192.168.49.2:30080
```

Navigate to `http://<minikube-ip>:30080` — you should see the Todo Chatbot login page.

---

## 8. Audit Trail

All agent-generated artifacts MUST be logged to `phase-iv-audit.log` at the repo root.
Append one line per agent invocation:

```bash
echo '[2026-02-24T10:00:00Z] [GORDON] prompt="Create multi-stage Dockerfile for FastAPI..." result="Dockerfile generated, 2-stage build, python:3.11-slim"' >> phase-iv-audit.log
```

---

## 9. Teardown

```bash
# Uninstall Helm release
helm uninstall todo-app

# Delete secrets and configmaps
kubectl delete secret todo-backend-secret
kubectl delete configmap todo-frontend-config

# Stop Minikube (optional)
minikube stop

# Restore host Docker context (optional)
eval $(minikube docker-env --unset)
```

---

## 10. Key Files Reference

| File | Purpose |
|------|---------|
| `charts/todo-app/Chart.yaml` | Chart metadata |
| `charts/todo-app/values.yaml` | Parameterised defaults |
| `charts/todo-app/templates/backend-deployment.yaml` | kubectl-ai generated |
| `charts/todo-app/templates/backend-service.yaml` | kubectl-ai generated |
| `charts/todo-app/templates/frontend-deployment.yaml` | kubectl-ai generated |
| `charts/todo-app/templates/frontend-service.yaml` | kubectl-ai generated |
| `charts/todo-app/templates/configmap.yaml` | todo-frontend-config |
| `phase-iv-audit.log` | Agent delegation audit trail |
| `specs/014-cloud-native-deployment/research.md` | All tech decisions + rationale |
| `specs/014-cloud-native-deployment/data-model.md` | Cluster topology + resource specs |
| `specs/014-cloud-native-deployment/contracts/helm-values-schema.yaml` | Helm values contract |

---

## Environment Variables Reference

| Variable | Where | Description |
|----------|-------|-------------|
| `DATABASE_URL` | K8s Secret | Neon PostgreSQL async connection string |
| `OPENAI_API_KEY` | K8s Secret | OpenAI key for agentic loop |
| `BETTER_AUTH_SECRET` | K8s Secret | JWT signing secret |
| `NEXT_PUBLIC_API_URL` | K8s ConfigMap | Backend URL for frontend (`http://todo-backend:8000`) |
