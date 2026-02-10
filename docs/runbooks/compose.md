# Runbook: Docker Compose Orchestration

This document describes how to launch, verify, and test the BoardGameHub microservices stack.

## 🚀 Launching the Stack

To build and start all services (API, Frontend, Redis, and Worker):

```bash
docker compose up --build
```

### Services Included:
- **Backend API**: `http://localhost:8000`
- **Frontend Dashboard**: `http://localhost:8501`
- **Redis Cache/Stats**: `localhost:6379`
- **Worker**: Runs in the background (no public port).

## ✅ Verification

### 1. Health Checks
The backend service includes a health check. You can verify the health status by running:

```bash
docker ps
```
Wait until the status shows `(healthy)`. You can also check manually:
```bash
curl http://localhost:8000/health
```

## 🧪 Testing in CI

### 1. Pytest
To run the automated test suite within the environment:

```bash
uv run pytest
```

### 2. Schemathesis (Contract Testing)
To run property-based tests against the API schema:

```bash
uv run schemathesis run http://localhost:8000/openapi.json
```

## 🛠️ Troubleshooting

- **Logs**: View logs for all services: `docker compose logs -f`
- **Reset**: To wipe the database and starts fresh: `docker compose down -v`
