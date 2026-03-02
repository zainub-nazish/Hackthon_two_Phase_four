# ============================================================
# Task ID  : T043
# Title    : WebSocket Service — Dockerfile
# Spec Ref : speckit.plan → Section 6.2: Frontend → Backend Pattern
# Plan Ref : speckit.plan → Section 1.2: WebSocket Service
# ============================================================
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8004

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
