# ClaimSense AI — Step 6: Async Worker & Task Processing Test Inventory

**Audit Phase:** Step 6: Async Worker & Task Processing Testing  
**Date:** 2026-11-22  
**Target Architecture:** Phase 12 Asynchronous Task Processing, Worker Daemon, Dual-Broker Dispatching, Retries, Idempotency & Stale Recovery  
**Inspection Mode:** Pre-Execution Architecture Discovery & Safety Assessment  

---

## 1. Asynchronous Architecture Discovery

ClaimSense AI incorporates a pluggable asynchronous task processing system (Phase 12) architected for both standalone local operation and containerized environments:

### Core Architecture Components:
1. **`ProcessingTask` ORM Model (`backend/database/models.py`):**
   - Stores task execution state, claim association, task IDs (`task-<uuid>`), status enums (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`, `TIMED_OUT`), stage enums (`INTAKE`, `OCR`, `CARDD`, `NARRATIVE`, `VERIFY`), error details, worker IDs, retry counts, execution times, and payload summaries.
2. **`TaskManager` & Pluggable Brokers (`backend/services/queue/manager.py`):**
   - **Dual-Engine Dispatching:**
     - `ThreadedTaskBroker`: Local in-process `ThreadPoolExecutor` with thread-safe queueing and persistent SQLite state tracking for standalone testing and non-Docker environments.
     - `RedisTaskBroker`: Redis list/queue protocol using `LPUSH`/`BRPOP` for containerized/Docker production deployments.
   - **Idempotency Engine:** Prevents duplicate task enqueueing for active tasks (`PENDING` / `RUNNING`).
   - **Stale Task Auto-Recovery:** Automatically detects tasks that exceeded `TASK_TIMEOUT_SECONDS` (default 300s, configurable in test) and transitions them to `TIMED_OUT` or triggers auto-recovery.
   - **Dead-Letter & Retry Logic:** Supports explicit task restart via `/api/claims/<id>/retry-task`.
3. **Pipeline Orchestrator (`backend/services/tasks/claim_tasks.py`):**
   - `execute_claim_processing_pipeline`: Sequentially progresses claim tasks through 5 stages (`INTAKE` $\rightarrow$ `OCR` $\rightarrow$ `CARDD` $\rightarrow$ `NARRATIVE` $\rightarrow$ `VERIFY`), capturing progress telemetry and timing.
4. **Worker Daemon Entrypoint (`scripts/run_worker.py`):**
   - Standalone CLI daemon supporting continuous polling (`--broker auto/redis/threaded`) and single-run batch draining (`--single-run`).

---

## 2. Test Selection & Safety Classification Matrix

| # | Test File | Test Case Method | Subsystem & Contract Tested | Safety Classification | Step 6 Group |
| :-: | :--- | :--- | :--- | :---: | :---: |
| 1 | `tests/test_phase12_async.py` | `test_01_processing_task_orm_lifecycle` | Task ORM schema, transitions (`PENDING` $\rightarrow$ `RUNNING` $\rightarrow$ `COMPLETED`), progression tracking | **SAFE TO RUN** | **Group 1** |
| 2 | `tests/test_phase12_async.py` | `test_03_async_claim_submission_returns_202_accepted` | Async claim intake returns HTTP 202 Accepted with `task_id` & tracking URL | **SAFE TO RUN** | **Group 1** |
| 3 | `tests/test_phase12_async.py` | `test_05_task_status_endpoint_returns_stage_progression` | `/api/claims/<id>/status` returns granular stage status, errors, and timing | **SAFE TO RUN** | **Group 1** |
| 4 | `tests/test_phase12_async.py` | `test_07_retry_claim_task_endpoint` | `/api/claims/<id>/retry-task` safely restarts failed/dead-letter tasks | **SAFE TO RUN** | **Group 2** |
| 5 | `tests/test_phase12_async.py` | `test_10_stale_task_recovery_mechanism` | Automatically flags tasks exceeding SLA as `TIMED_OUT` without crashing | **SAFE TO RUN** | **Group 2** |
| 6 | `tests/test_phase12_async.py` | `test_02_task_manager_idempotency_prevents_duplicate_active_tasks` | TaskManager blocks concurrent duplicate submissions for same claim | **SAFE TO RUN** | **Group 3** |
| 7 | `tests/test_phase12_async.py` | `test_04_sync_claim_submission_fallback_returns_201_created` | Synchronous fallback (`?sync=true`) bypasses queue and returns HTTP 201 | **SAFE TO RUN** | **Group 3** |
| 8 | `tests/test_phase12_async.py` | `test_11_worker_cli_single_run` | `scripts/run_worker.py` CLI daemon in `--single-run` mode against threaded broker | **SAFE TO RUN** | **Group 4** |
| 9 | `tests/test_pipeline_and_ux_fixes.py` | `test_02_async_pipeline_executes_without_detached_instance_error` | Pipeline re-attaches ORM sessions across stages, preventing `DetachedInstanceError` | **SAFE TO RUN** | **Group 4** |
| 10 | `tests/test_pipeline_and_ux_fixes.py` | `test_01_vehicle_damage_analysis_null_confidence_safety` | Guarantees non-null float defaults for `max_confidence` during async worker runs | **SAFE TO RUN** | **Group 4** |
| 11 | `tests/test_phase12_async.py` | `test_06_task_status_unauthorized_isolation` | Multi-user tenant isolation: unauthorized users cannot view other tasks | **SAFE TO RUN** | **Group 5** |
| 12 | `tests/test_phase12_async.py` | `test_08_health_ready_probe_verifies_task_queue` | `/api/health/ready` probe verifies queue connectivity and broker health | **SAFE TO RUN** | **Group 5** |
| 13 | `tests/test_phase12_async.py` | `test_09_health_metrics_telemetry_includes_queue_telemetry` | `/api/health/metrics` includes operational queue depth & task status telemetry | **SAFE TO RUN** | **Group 5** |
| 14 | `tests/test_pipeline_and_ux_fixes.py` | `test_03_claimant_narrative_visibility_endpoint` | Claimant prose narrative preserved through async processing and visible on details | **SAFE TO RUN** | **Group 5** |

**Total Step 6 Inventory:** 14 tests across 2 modules.

---

## 3. Mandatory Safety & Resource Isolation Verification

- **Production Database:** `data/claimsense.db` is strictly protected. Tests instantiate isolated temporary databases (`test_phase12.db` and `test_fixes.db`) in ephemeral `tempfile.mkdtemp()` directories.
- **Queue Broker:** All tests run with `QUEUE_BROKER_TYPE = "threaded"`. In-memory `ThreadPoolExecutor` and `queue.Queue` are used. Zero connections to production Redis (port 6379).
- **Filesystem Isolation:** Temporary uploads, reports, and backup directories are created per test class and cleaned up via `shutil.rmtree(..., ignore_errors=True)` and `close_engine()`.
- **Application Code:** Zero modifications to backend or frontend application code.
- **Test Code:** Zero modifications to existing test files.

---

## 4. Planned Sequential Execution Groups

- **Group 1:** Task Dispatch & Lifecycle (3 tests)
- **Group 2:** Retry & Failure Handling (2 tests)
- **Group 3:** Idempotency & Duplicate Prevention (2 tests)
- **Group 4:** Worker Concurrency & Recovery (3 tests)
- **Group 5:** Integration & Telemetry (4 tests)
