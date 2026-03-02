# ============================================================
# Task ID  : T056
# Title    : Backend — Multi-arch Dockerfile (amd64 + arm64 / OKE A1)
# Spec Ref : speckit.plan → Section 7C: Cloud (OKE ARM64 nodes)
# Plan Ref : speckit.plan → Section 2.2: Kubernetes distribution
# ============================================================
# Build multi-arch: docker buildx build --platform linux/amd64,linux/arm64 -t <tag> --push .
# Base image python:3.11-slim is officially multi-arch (amd64 + arm64)

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
