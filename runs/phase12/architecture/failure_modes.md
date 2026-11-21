# ClaimSense AI — Phase 12 Failure Modes, Exceptions & Recovery Matrix

## 1. Overview & Threat Vector Identification

This document catalogs potential failure scenarios, failure propagation paths, mitigation mechanisms, and recovery guarantees within the ClaimSense AI asynchronous processing pipeline.

---

## 2. Failure Modes & Recovery Matrix

| Failure Mode | Root Cause / Trigger | Blast Radius | Automated Mitigation | Manual / Fallback Recovery |
| :--- | :--- | :--- | :--- | :--- |
| **Worker Process Crash (OOM / SIGKILL)** | Excessive image resolution during YOLOv8 or Tesseract processing exhausts worker memory. | Task remains locked in `PROCESSING` state indefinitely. | `TaskManager.recover_stale_tasks()` detects tasks where `updated_at < (now - timeout)`. Re-enqueues if `retry_count < max_retries`. | If retries exhausted, marks `FAILED` with code `TASK_TIMEOUT`. Admin can trigger `/api/claims/<id>/retry-task`. |
| **Redis Broker Unreachable** | Redis container down, network partition, or connection timeout. | New async tasks cannot be pushed to Redis list. | System automatically logs warning and falls back to `ThreadedTaskBroker` (or worker direct polling from SQLite `processing_tasks` table). | Restart Redis container (`docker compose restart redis`). Broker health probe in `/api/health/ready` alerts operators. |
| **Duplicate Claim Submission (Double-Click)** | Policyholder double-clicks "Submit Claim" button in web browser. | Two rapid multipart POST requests sent to API. | Database-level idempotency checks active task in `['QUEUED', 'PROCESSING']`. Returns existing task with `is_new=False` on second call. | N/A — Zero duplicate background jobs dispatched. |
| **Corrupted / Unreadable Document** | Uploaded PDF has corrupted headers or zero readable text layers. | OCR extraction fails for that document. | Best-effort isolation block catches `Exception`, marks document `extraction_status="INCONCLUSIVE"`, and allows remaining documents and YOLO vision to proceed. | Discrepancy finding generated in Phase 7 report: `INSUFFICIENT_DOCUMENTATION`. |
| **Non-Photographic Image Upload (Spoof)** | User uploads clipart, meme, or screenshot instead of authentic vehicle damage photo. | YOLOv8 inference produces low-confidence or false detections. | Anti-spoof heuristic (Sobel edge entropy & color channel variance) detects non-photographic artifact, halts vision inference, sets `requires_replacement=True`. | Frontend displays replacement photo upload box; original evidence preserved in audit vault. |
| **Database Transaction Lock Contention** | Multiple workers attempt concurrent write operations on SQLite database. | `sqlite3.OperationalError: database is locked`. | Hardened connection pragmas (`PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;`) allow concurrent readers while queuing writers up to 5 seconds. | Automatic SQLite retry loop within session context manager. |
