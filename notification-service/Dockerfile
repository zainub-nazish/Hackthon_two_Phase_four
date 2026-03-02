# ============================================================
# Task ID  : T035
# Title    : Notification Service — Dockerfile
# Spec Ref : speckit.plan → Section 7B: Minikube local setup
# Plan Ref : speckit.plan → Section 2.2: Kubernetes distribution
# ============================================================
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
