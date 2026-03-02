# ============================================================
# Task ID  : T056
# Title    : Frontend — Multi-arch Dockerfile (amd64 + arm64 / OKE A1)
# Spec Ref : speckit.plan → Section 7C: Cloud (OKE ARM64 nodes)
# Plan Ref : speckit.plan → Section 2.2: Kubernetes distribution
# ============================================================
# Build multi-arch: docker buildx build --platform linux/amd64,linux/arm64 -t <tag> --push .
# Base image node:20-alpine is officially multi-arch (amd64 + arm64)

FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --frozen-lockfile

COPY . .
RUN npm run build

# Production stage — minimal runtime image
FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["node", "server.js"]
