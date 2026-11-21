# ClaimSense AI — Phase 12 Observability, Telemetry & Queue Monitoring Audit

## 1. Executive Summary

Phase 12 introduces real-time queue observability and stage telemetry into ClaimSense AI. The observability subsystem provides:
- Live status tracking of multi-stage claim processing (`INTAKE` $\rightarrow$ `OCR_PROCESSING` $\rightarrow$ `DAMAGE_ANALYSIS` $\rightarrow$ `NLP_CHRONOLOGY` $\rightarrow$ `CROSS_SOURCE_VERIFICATION` $\rightarrow$ `COMPLETED`).
- System-level readiness probing (`/api/health/ready`) integrating Redis/Threaded queue health verification.
- Real-time queue metrics telemetry (`/api/health/metrics`) exposing active task counts by state (`queued`, `processing`, `completed`, `failed`) and broker depth.
- Client-side visual progress synchronization displaying completion percentages, current stages, and execution metadata without page refreshes.

---

## 2. Telemetry Endpoints Specification

### 2.1 `/api/health/ready` (Readiness Probe)

Verifies critical downstream resources before admitting traffic:

| Resource Checked | Check Method | Failure Impact |
| :--- | :--- | :--- |
| **Database** | `SELECT 1` execute + PRAGMA journal_mode check | Returns HTTP 503, Pod marked unready |
| **Storage Uploads** | Scratch file write/delete in `UPLOAD_FOLDER` | Returns HTTP 503, Uploads rejected |
| **ML Model Weights** | Existence check of `models/phase5/best.pt` | Returns HTTP 503, Model unavailable |
| **Task Queue Broker** | Ping check on active Redis broker or ThreadPool health | Returns HTTP 503, Async queue halted |

#### Sample Readiness Response (HTTP 200)
```json
{
  "status": "ready",
  "ready": true,
  "checks": {
    "database": true,
    "storage_uploads": true,
    "ml_model_present": true,
    "task_queue": true
  },
  "details": {
    "sqlite_journal_mode": "WAL",
    "model_checkpoint": "verified",
    "task_broker": "redis"
  },
  "timestamp": "2026-11-21T16:40:00.000000Z"
}
```

---

### 2.2 `/api/health/metrics` (Operational Telemetry)

Exposes runtime statistics for monitoring daemons (Prometheus/Grafana/Docker health scrapers):

```json
{
  "status": "ok",
  "uptime_seconds": 3840.12,
  "entity_counts": {
    "claims": 24,
    "users": 18
  },
  "queue": {
    "active_broker": "redis",
    "broker_healthy": true,
    "queue_depth": 0,
    "task_counts": {
      "queued": 0,
      "processing": 0,
      "completed": 24,
      "failed": 0
    }
  },
  "memory_rss_mb": 142.6,
  "python_version": "3.14.6",
  "platform": "Windows-11-10.0.26100-SP0",
  "timestamp": "2026-11-21T16:40:00.000000Z"
}
```

---

### 2.3 `/api/claims/<claim_id>/status` (Task State Telemetry)

Enables client polling and programmatic progress tracking with strict tenant and role isolation:

```json
{
  "success": true,
  "claim_id": "CLM-20261121-Z0CI",
  "task_id": "task-7b89f2a013c49e1a",
  "status": "completed",
  "stage": "completed",
  "progress_percent": 100,
  "retry_count": 0,
  "max_retries": 3,
  "worker_id": "worker-24372-1795123000",
  "error_code": null,
  "error_message": null,
  "result_metadata": {
    "claim_id": "CLM-20261121-Z0CI",
    "ocr_docs_processed": 3,
    "damages_detected": 4,
    "nlp_success": true,
    "verification_success": true,
    "duration_ms": 2840.5
  },
  "created_at": "2026-11-21T16:35:10.120000Z",
  "started_at": "2026-11-21T16:35:10.145000Z",
  "completed_at": "2026-11-21T16:35:12.985000Z",
  "updated_at": "2026-11-21T16:35:12.985000Z"
}
```

---

## 3. Operational Logging Standards

All task events emit structured JSON log entries when `JSON_LOGGING=true`:
- `claimsense.queue`: Task enqueueing, broker dispatch, idempotency hits, and queue metrics collection.
- `claimsense.tasks`: Individual stage start/completion, stage duration, exception handling, and error codes.
- `claimsense.worker`: Worker lifecycle, signal trap notifications, stale task recovery batches, and job completions.

Each log includes `timestamp`, `level`, `logger`, `claim_id`, `task_id`, and `worker_id` for distributed trace correlation.
