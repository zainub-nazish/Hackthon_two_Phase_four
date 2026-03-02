#!/usr/bin/env bash
# ============================================================
# Task ID  : T057
# Title    : OKE Always-Free cluster setup reference script
# Spec Ref : speckit.plan → Section 7C: Cloud setup sequence (Oracle OKE)
# Plan Ref : speckit.plan → Section 7.2: Cloud Deployment Steps
# ============================================================
# PURPOSE: Reference documentation script — covers OKE cluster bootstrap,
#          Dapr installation, and Kubernetes secret creation.
#
# Constitution C-04: NO credentials are hardcoded — all secrets use env vars.
#
# PREREQUISITES:
#   - OCI CLI configured: oci setup config
#   - kubectl installed
#   - Helm 3.x installed
#   - Dapr CLI installed: https://docs.dapr.io/getting-started/install-dapr-cli/
#
# USAGE:
#   export OCI_COMPARTMENT_ID="ocid1.compartment.oc1..."
#   export KUBE_CONTEXT="context-name-from-oci-kubeconfig"
#   export DATABASE_URL="postgresql+asyncpg://..."
#   export KAFKA_USER="<redpanda-user>"
#   export KAFKA_PASS="<redpanda-password>"
#   bash infra/oke-setup.sh

set -euo pipefail

NAMESPACE="todo-app"
DAPR_VERSION="1.13.0"
CHART_PATH="charts/todo-app-v5"

echo "=== Step 1: OKE Cluster (Oracle Always-Free) ==="
echo "Create via OCI Console or CLI:"
echo "  - Choose: Oracle Cloud Infrastructure → Developer Services → Kubernetes Clusters (OKE)"
echo "  - Select: Quick Create, VCN auto-creation, 3 nodes → ARM-based A1.Flex (Always Free)"
echo "  - Node shape: VM.Standard.A1.Flex with 1 OCPU, 6 GB each"
echo ""
echo "After cluster is ready, download kubeconfig:"
echo "  oci ce cluster create-kubeconfig --cluster-id <CLUSTER_OCID> --file ~/.kube/config-oke --region us-ashburn-1 --token-version 2.0.0"
echo "  export KUBECONFIG=~/.kube/config-oke"

echo ""
echo "=== Step 2: Create Namespace ==="
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -
kubectl label namespace "${NAMESPACE}" dapr.io/enabled=true --overwrite

echo ""
echo "=== Step 3: Install Dapr on OKE ==="
dapr init --kubernetes --wait --runtime-version "${DAPR_VERSION}"
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=dapr -n dapr-system --timeout=120s

echo ""
echo "=== Step 4: Install Nginx Ingress Controller ==="
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx || true
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.type=LoadBalancer

echo ""
echo "=== Step 5: Create Kubernetes Secrets ==="
# Constitution C-04: values from environment variables — never hardcoded

# Backend secret (Neon DB connection string)
kubectl create secret generic todo-backend-secret \
  --namespace "${NAMESPACE}" \
  --from-literal=DATABASE_URL="${DATABASE_URL}" \
  --dry-run=client -o yaml | kubectl apply -f -

# Kafka/Redpanda credentials
kubectl create secret generic kafka-secret \
  --namespace "${NAMESPACE}" \
  --from-literal=saslUsername="${KAFKA_USER}" \
  --from-literal=saslPassword="${KAFKA_PASS}" \
  --dry-run=client -o yaml | kubectl apply -f -

echo ""
echo "=== Step 6: Deploy Todo Chatbot v5 via Helm ==="
EXTERNAL_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "PENDING")

echo "Ingress external IP: ${EXTERNAL_IP}"

helm upgrade --install todo-chatbot-v5 "${CHART_PATH}" \
  --namespace "${NAMESPACE}" \
  -f "${CHART_PATH}/values.cloud.yaml" \
  -f "${CHART_PATH}/values.redpanda.yaml" \
  --set ingress.host="${EXTERNAL_IP}" \
  --set global.imageTag="${IMAGE_TAG:-latest}" \
  --wait --timeout 5m

echo ""
echo "=== Step 7: Verify Deployment ==="
kubectl get pods -n "${NAMESPACE}"
kubectl get components -n "${NAMESPACE}"
kubectl get ingress -n "${NAMESPACE}"

echo ""
echo "=== Done! ==="
echo "Frontend: http://${EXTERNAL_IP}"
echo "Backend API: http://${EXTERNAL_IP}/api/v1"
echo "API Docs: http://${EXTERNAL_IP}/api/docs (debug mode only)"
