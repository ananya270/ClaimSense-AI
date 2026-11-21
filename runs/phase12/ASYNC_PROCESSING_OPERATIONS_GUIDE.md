# ClaimSense AI — Phase 12 Asynchronous Processing Operations & Deployment Guide

## 1. Local Developer Workflow

### 1.1 Zero-Dependency Setup (Windows/macOS/Linux)
In local development environments without Docker or Redis installed, ClaimSense AI operates natively using the in-process `ThreadPoolExecutor` with persistent SQLite state.
```powershell
# 1. Activate Virtual Environment
cd "c:\Users\ydvan\Desktop\ClaimSense Ai\ClaimSense-AI"
.\.venv\Scripts\Activate.ps1

# 2. Boot Application Server
python run.py
```
The server starts on `http://127.0.0.1:5001`. Claims submitted via the web frontend or API are automatically processed asynchronously in background worker threads.

### 1.2 Running Standalone Worker Daemon (Optional Local Testing)
To test dedicated worker process separation locally:
```powershell
python scripts/run_worker.py --broker threaded --interval 1.0
```

---

## 2. Production Containerized Deployment (Docker Compose)

### 2.1 Starting Multi-Container Stack
```bash
# Build and start all 4 services: redis, app, worker, nginx
docker compose up -d --build
```

### 2.2 Verifying Container Health
```bash
docker compose ps
```
*Expected Output:*
- `claimsense-redis`: `healthy` (Port 6379, isolated internal network)
- `claimsense-app`: `healthy` (Port 5001 exposed internally)
- `claimsense-worker`: `running` (Listening to Redis queue `claimsense:tasks:claims`)
- `claimsense-nginx`: `running` (Ports 80/443 exposed publicly)

### 2.3 Health Probing
```bash
# 1. Check Liveness
curl -i http://localhost/api/health/live

# 2. Check Deep Readiness
curl -i http://localhost/api/health/ready

# 3. Inspect Queue Telemetry
curl -i http://localhost/api/health/metrics
```

---

## 3. Operational Troubleshooting Runbook

### Issue: Task Stuck in `PROCESSING` State
- **Symptom:** UI displays "Processing (25%)..." for $> 5\text{ minutes}$.
- **Root Cause:** A worker crashed or suffered an unhandled OS kill signal while running inference.
- **Automated Fix:** `TaskManager.recover_stale_tasks()` automatically detects tasks exceeding `TASK_TIMEOUT_SECONDS` (300s) on subsequent cycles, retrying up to 3 times before setting state to `FAILED`.
- **Manual Remediation:**
  1. Trigger task retry via API:
     ```bash
     curl -X POST -H "Cookie: session=..." http://localhost/api/claims/<claim_id>/retry-task
     ```
  2. Or inspect worker logs:
     ```bash
     docker compose logs -f worker
     ```

### Issue: Redis Broker Connection Dropped
- **Symptom:** Logs show `Redis is unreachable. Falling back to DB-polling broker.`
- **Mitigation:** The application degrades gracefully, falling back to SQLite task table polling without dropping incoming claims.
- **Remediation:** Check Redis container status (`docker compose restart redis`).
